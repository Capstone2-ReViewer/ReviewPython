import requests
import time
from datetime import datetime, timezone

APP_ID = 271590  # GTA5
LANGUAGE = "korean"
DAY_RANGE = 730  # 2년

def fetch_recent_reviews(app_id, language="korean", day_range=730):
    seen_review_ids = set()
    cursor = "*"
    total_reviews = 0

    while True:
        url = (
            f"https://store.steampowered.com/appreviews/{app_id}"
            f"?json=1&language={language}&day_range={day_range}&filter=all&review_type=all"
            f"&purchase_type=all&num_per_page=100&cursor={cursor}"
        )

        res = requests.get(url)
        if res.status_code != 200:
            print(f"❌ 요청 실패: {res.status_code}")
            break

        data = res.json()
        reviews = data.get("reviews", [])
        cursor = data.get("cursor", "*")

        # 더 이상 가져올 리뷰가 없으면 종료
        if not reviews or cursor == "*":
            break

        for r in reviews:
            review_id = r.get("recommendationid")
            if review_id in seen_review_ids:
                continue

            seen_review_ids.add(review_id)

            # 리뷰 정보
            timestamp_created = r.get("timestamp_created", 0)
            date_str = datetime.fromtimestamp(timestamp_created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            text = r.get("review", "").strip()
            voted_up = r.get("voted_up")
            playtime_forever = r.get("author", {}).get("playtime_forever", 0)
            weighted_vote_score = r.get("weighted_vote_score", 0.5)

            print(f"📝 {date_str} | 추천 여부: {voted_up} | 점수: {weighted_vote_score} | 플레이타임: {playtime_forever}분")
            print(f"리뷰: {text}")
            print("-" * 80)

            total_reviews += 1

        time.sleep(0.5)  # 딜레이 추가

    print(f"\n🚀 총 {total_reviews}개의 리뷰 수집 완료")


if __name__ == "__main__":
    fetch_recent_reviews(APP_ID, language=LANGUAGE, day_range=DAY_RANGE)
