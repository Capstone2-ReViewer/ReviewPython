import requests
import time
import re

def is_valid_review(text):
    if re.search(r"[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,!?~()\"']+", text) is None:
        return False

    total_len = len(text)
    if total_len < 10:
        return False  # 너무 짧은 리뷰 제외

    eng_count = len(re.findall(r'[a-zA-Z]', text))
    if eng_count / total_len > 0.3:
        return False

    return True


def fetch_reviews_with_filter(app_id, language="korean"):
    valid_reviews = []
    filtered_reviews = []
    seen_review_ids = set()
    cursor = "*"

    while True:
        url = (
            f"https://store.steampowered.com/appreviews/{app_id}"
            f"?json=1&language={language}&day_range=730&filter=recent&review_type=all"
            f"&purchase_type=all&num_per_page=100&cursor={cursor}"
        )

        res = requests.get(url)
        if res.status_code != 200:
            break

        data = res.json()
        reviews = data.get("reviews", [])
        cursor = data.get("cursor", "*")

        # 더 이상 가져올 리뷰가 없으면 종료
        if not reviews or cursor == "*":
            break

        for r in reviews:
            review_id = r.get("recommendationid")
            text = r["review"].strip()
            timestamp_created = r["timestamp_created"]
            voted_up = r["voted_up"]
            playtime_forever = r.get("author", {}).get("playtime_forever", 0)
            weighted_vote_score = r.get("weighted_vote_score", None)

            # 중복 제거 (리뷰 ID 기준)
            if review_id in seen_review_ids:
                continue

            # 필터 체크
            if not is_valid_review(text):
                filtered_reviews.append({
                    "review": text,
                    "timestamp_created": timestamp_created,
                    "voted_up": voted_up,
                    "playtime_forever": playtime_forever,
                    "weighted_vote_score": weighted_vote_score,
                    "sentiment_score": 0.5  # 필터된 리뷰는 0.5로 처리
                })
                continue

            # 중복 체크
            seen_review_ids.add(review_id)

            # 통과된 리뷰 저장
            valid_reviews.append({
                "review": text,
                "timestamp_created": timestamp_created,
                "voted_up": voted_up,
                "playtime_forever": playtime_forever,
                "weighted_vote_score": weighted_vote_score
            })

        # 요청 간 딜레이
        time.sleep(0.5)

    return valid_reviews, filtered_reviews
