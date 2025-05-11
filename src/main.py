from steamAPI.game_enum import get_game_codes
from steamAPI.game_info import get_game_info
from steamAPI.update_dates import get_updates
from steamAPI.review import fetch_reviews_with_filter
from save_to_db import save_game_info, save_updates, save_score_playtime
from topic.kcBert import analyze_sentiment_kcbert
from datetime import datetime, timezone
import time


def calculate_final_score(voted_up, weighted_vote_score, sentiment_score):
    try:
        weighted_vote_score = float(weighted_vote_score)
    except (ValueError, TypeError):
        weighted_vote_score = 0.5

    score = (
                    (voted_up * 0.4) +
                    (weighted_vote_score * 0.4) +
                    (sentiment_score * 0.2)
            ) * 100

    if score < 0:
        score = 100 + score

    return round(score, 2)


if __name__ == "__main__":
    # 게임 코드 로드
    codes = get_game_codes()

    # 게임 정보 수집
    game_info_dict = {}
    for name, app_id in codes.items():
        info = get_game_info(app_id)
        if info:
            info["game_name"] = name
            game_info_dict[app_id] = info

    # 게임 정보 저장
    save_game_info(game_info_dict)

    # 업데이트 내역 수집
    update_dict = {}
    for name, app_id in codes.items():
        updates = get_updates(app_id)
        if updates:
            update_dict[app_id] = {"name": name, "update_dates": updates}

    # 업데이트 내역 저장
    save_updates(update_dict)

    # 리뷰 데이터 수집 및 분석
    all_scores = []
    for app_id in codes.values():
        # 전체 리뷰 수집
        valid_reviews, filtered_reviews = fetch_reviews_with_filter(app_id, language="korean")

        # 리뷰 분석 (필터 통과된 리뷰만)
        if valid_reviews:
            review_texts = [review["review"] for review in valid_reviews]
            analyzed_reviews = analyze_sentiment_kcbert(review_texts)

            for i, review in enumerate(valid_reviews):
                sentiment_label = analyzed_reviews[i]["label"]
                sentiment_score = 1.0 if sentiment_label == 1 else 0.0

                # 최종 점수 계산
                final_score = calculate_final_score(
                    voted_up=review["voted_up"],
                    weighted_vote_score=review.get("weighted_vote_score", 0.5),
                    sentiment_score=sentiment_score
                )

                # 월별 정보 추가
                review_date = datetime.fromtimestamp(review["timestamp_created"], tz=timezone.utc).strftime("%Y-%m")

                all_scores.append({
                    "app_id": app_id,
                    "year_month": review_date,
                    "final_score": final_score,
                    "playtime_forever": review.get("playtime_forever", 0)
                })

        # 필터된 리뷰도 기본 0.5 점수로 저장
        for review in filtered_reviews:
            review_date = datetime.fromtimestamp(review["timestamp_created"], tz=timezone.utc).strftime("%Y-%m")
            all_scores.append({
                "app_id": app_id,
                "year_month": review_date,
                "final_score": calculate_final_score(
                    voted_up=review["voted_up"],
                    weighted_vote_score=0.5,
                    sentiment_score=0.5
                ),
                "playtime_forever": review.get("playtime_forever", 0)
            })

        print(f"✅ {app_id} 리뷰 수집 및 분석 완료")
        time.sleep(0.5)  # 딜레이 추가

    # 점수 데이터 저장
    save_score_playtime(all_scores)

    print("\n🚀 모든 데이터 저장 완료!")
