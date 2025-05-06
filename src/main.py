# main.py
from steamAPI.game_enum import get_game_codes
from steamAPI.game_info import get_game_info
from steamAPI.update_dates import get_updates
from steamAPI.review import fetch_reviews
from save_to_db import save_game_info, save_updates
from topic.kcBert import analyze_sentiment_kcbert  # 분석 함수 불러오기
import pandas as pd

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
    reviews_dict = {}
    for name, app_id in codes.items():
        reviews = fetch_reviews(app_id, language="korean", num_pages=3)
        if reviews:
            # 리뷰 텍스트만 추출
            review_texts = [review["review"] for review in reviews]

            # 리뷰 분석
            analyzed_reviews = analyze_sentiment_kcbert(review_texts)  # 리뷰 분석만 넘김
            reviews_dict[app_id] = {"name": name, "reviews": analyzed_reviews}
            print(f"✅ {name} ({app_id}) 리뷰 수집 및 분석 완료")

    # 분석된 리뷰를 DataFrame으로 변환
    all_reviews = []
    for app_id, data in reviews_dict.items():
        for review in data["reviews"]:
            all_reviews.append({
                "game_name": data["name"],
                "review": review["text"],
                "label": review["label"],
                "confidence": review["confidence"]
            })

    df_reviews = pd.DataFrame(all_reviews)

    # CSV로 출력
    df_reviews.to_csv('./game_reviews_analysis.csv', index=False)

    print("\n🚀 리뷰 데이터 수집 및 분석 완료! CSV로 저장되었습니다.")
