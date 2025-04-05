import requests
import time

def fetch_reviews(app_id, language="korean", start_date=None, end_date=None, num_pages=10):
    all_reviews = []

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
            all_reviews.append({
                "review": r["review"],
                "timestamp_created": r["timestamp_created"],
                "voted_up": r["voted_up"],
                "playtime_forever": r.get("playtime_forever", 0)  # 플레이타임을 추가
            })

        time.sleep(0.5)

    return all_reviews
