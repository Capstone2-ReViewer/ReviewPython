import requests
import time
import re

def is_valid_review(text):
    # 한국어 + 영어 외의 언어 포함 여부 (중국어, 러시아어 등 제외 조건)
    if re.search(r"[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,!?~()\"']+", text) is None:
        return False

    # 영어 비율이 30% 이하인지 확인
    total_len = len(text)
    if total_len < 10:
        return False  # 너무 짧은 리뷰 제외

    eng_count = len(re.findall(r'[a-zA-Z]', text))
    if eng_count / total_len > 0.3:
        return False

    return True


def fetch_reviews(app_id, language="korean", num_pages=10):
    all_reviews = []
    seen_reviews = set()

    for page in range(1, num_pages + 1):
        url = (
            f"https://store.steampowered.com/appreviews/{app_id}"
            f"?json=1&language={language}&day_range=730&filter=recent&review_type=all"
            f"&purchase_type=all&num_per_page=100&cursor=*&page={page}"
        )

        res = requests.get(url)
        if res.status_code != 200:
            break

        reviews = res.json().get("reviews", [])
        for r in reviews:
            text = r["review"].strip()
            if not is_valid_review(text):
                continue
            if text in seen_reviews:
                continue

            seen_reviews.add(text)

            all_reviews.append({
                "review": text,
                "timestamp_created": r["timestamp_created"],
                "voted_up": r["voted_up"],
                "playtime_forever": r.get("playtime_forever", 0),
                "weighted_vote_score": r.get("weighted_vote_score", None)
            })

        time.sleep(0.5)  # 요청 간 딜레이

    return all_reviews
