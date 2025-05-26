from steamAPI.game_enum import get_game_codes
from steamAPI.game_info import get_game_info
from steamAPI.update_dates import get_updates
from steamAPI.review import run_review
from save_to_db import save_game_info, save_updates, save_score_playtime, save_keyword
from topic.kcBert import analyze_sentiment_kcbert
from datetime import datetime, timezone
from topic.keword_konlpy import run_keyword

import time
import os
import csv


def calculate_final_score(voted_up, weighted_vote_score, sentiment_score):
    try:
        weighted_vote_score = float(weighted_vote_score)
    except (ValueError, TypeError):
        weighted_vote_score = 0.5

    score = (
        (voted_up * 0.4) +
        (weighted_vote_score * 0.3) +
        (sentiment_score * 0.3)
    ) * 100

    if score < 0:
        score = 100 + score

    return round(score, 2)


def load_reviews_from_csv(file_path, include_text=True):
    reviews = []
    print(f"📂 파일 로드 중: {file_path}")  # 파일 로드 메시지 추가
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)  # 헤더 건너뛰기
        for row in reader:
            try:
                # ✅ 필드 개수에 따라 처리 분기
                if include_text:
                    if len(row) == 6:
                        app_id, voted_up, weighted_vote_score, playtime_forever, timestamp_created, review = row
                        reviews.append({
                            "app_id": int(app_id.strip() or 0),
                            "voted_up": int(voted_up.strip() or 0),
                            "weighted_vote_score": float(weighted_vote_score.strip() or 0.0),
                            "playtime_forever": int(playtime_forever.strip() or 0),
                            "timestamp_created": int(timestamp_created.strip() or 0),
                            "review": review.strip()
                        })
                    elif len(row) == 5:
                        # ✅ 타임스탬프가 누락된 경우 현재 시간 사용
                        app_id, voted_up, weighted_vote_score, playtime_forever, review = row
                        timestamp_created = int(time.time())  # 현재 시간 사용
                        reviews.append({
                            "app_id": int(app_id.strip() or 0),
                            "voted_up": int(voted_up.strip() or 0),
                            "weighted_vote_score": float(weighted_vote_score.strip() or 0.0),
                            "playtime_forever": int(playtime_forever.strip() or 0),
                            "timestamp_created": timestamp_created,
                            "review": review.strip()
                        })
                    else:
                        print(f"⚠️ 필드 개수 오류 - {row}")
                else:
                    app_id, voted_up, weighted_vote_score, playtime_forever = row
                    reviews.append({
                        "app_id": int(app_id.strip() or 0),
                        "voted_up": int(voted_up.strip() or 0),
                        "weighted_vote_score": float(weighted_vote_score.strip() or 0.0),
                        "playtime_forever": int(playtime_forever.strip() or 0)
                    })
            except ValueError as e:
                print(f"⚠️ 데이터 변환 오류: {e} - {row}")
                continue
    print(f"✅ {len(reviews)}개의 리뷰 로드 완료")  # 로드 완료 메시지 추가
    return reviews


def main():

    # 게임 코드 로드
    codes = get_game_codes()

    # 게임 정보 수집 및 저장
    game_info_dict = {app_id: get_game_info(app_id) for name, app_id in codes.items() if get_game_info(app_id)}
    save_game_info(game_info_dict)

    # 업데이트 내역 수집 및 저장
    update_dict = {app_id: {"name": name, "update_dates": get_updates(app_id)} for name, app_id in codes.items() if get_updates(app_id)}
    save_updates(update_dict)


    run_review()

    # 리뷰 데이터 수집 및 분석
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filtered_dir = os.path.join(BASE_DIR, "steamAPI", "filtered")
    unfiltered_dir = os.path.join(BASE_DIR,"steamAPI", "unfiltered")

    print(f"📂 필터된 리뷰 폴더: {filtered_dir}")
    print(f"📂 필터되지 않은 리뷰 폴더: {unfiltered_dir}")

    for name, app_id in codes.items():
        print(f"🎮 {name} ({app_id}) 데이터 처리 중...")
        all_scores = []

        # 필터된 리뷰 처리 (기본 0.5 점수)
        filtered_file = os.path.join(filtered_dir, f"{app_id}.csv")
        if os.path.exists(filtered_file):
            filtered_reviews = load_reviews_from_csv(filtered_file, include_text=True)
            if filtered_reviews:
                for review in filtered_reviews:
                    review_date = datetime.fromtimestamp(review["timestamp_created"], tz=timezone.utc).strftime("%Y-%m")

                    final_score = calculate_final_score(
                        voted_up=review["voted_up"],
                        weighted_vote_score=review["weighted_vote_score"],
                        sentiment_score=0.5  # 기본 점수
                    )

                    score_data = {
                        "app_id": review["app_id"],
                        "year_month": review_date,
                        "final_score": final_score,
                        "playtime_forever": review["playtime_forever"]
                    }

                    all_scores.append(score_data)
            else:
                print(f"⚠️ {app_id} (필터된) 저장할 리뷰 데이터가 없습니다.")
        else:
            print(f"⚠️ {app_id} 필터된 리뷰 파일이 존재하지 않습니다.")

        # 필터되지 않은 리뷰 처리
        # 필터되지 않은 리뷰 처리 (KcBERT 감성 분석)
        unfiltered_file = os.path.join(unfiltered_dir, f"{app_id}.csv")
        if os.path.exists(unfiltered_file):
            unfiltered_reviews = load_reviews_from_csv(unfiltered_file, include_text=True)
            if unfiltered_reviews:
                review_texts = [review["review"] for review in unfiltered_reviews]
                analyzed_reviews = analyze_sentiment_kcbert(review_texts)

                for i, review in enumerate(unfiltered_reviews):
                    # ✅ KcBERT의 confidence 값 사용
                    sentiment_score = analyzed_reviews[i]["confidence"]  # 0.0 ~ 1.0 사이의 확률

                    # ✅ 리뷰의 생성일을 year-month 형식으로 변환
                    review_date = datetime.fromtimestamp(review["timestamp_created"], tz=timezone.utc).strftime("%Y-%m")

                    # 최종 점수 계산
                    final_score = calculate_final_score(
                        voted_up=review["voted_up"],
                        weighted_vote_score=review["weighted_vote_score"],
                        sentiment_score=sentiment_score
                    )

                    score_data = {
                        "app_id": review["app_id"],
                        "year_month": review_date,
                        "final_score": final_score,
                        "playtime_forever": review["playtime_forever"]
                    }

                    all_scores.append(score_data)

            else:
                print(f"⚠️ {app_id} (필터되지 않은) 저장할 리뷰 데이터가 없습니다.")
        else:
            print(f"⚠️ {app_id} 필터되지 않은 리뷰 파일이 존재하지 않습니다.")

        # 점수 데이터 저장
        if all_scores:
            save_score_playtime(all_scores)
            print(f"✅ {name} ({app_id}) 데이터 저장 완료")
        else:
            print(f"⚠️ {name} ({app_id}) 저장할 데이터가 없습니다.")

    print("\n🚀 모든 데이터 저장 완료!")


    keword_data = run_keyword()
    save_keyword(keword_data)


# 실행 예시
if __name__ == "__main__":
    main()