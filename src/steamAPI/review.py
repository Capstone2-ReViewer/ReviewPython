import requests
import time
import re
import csv
import os
import json

# 게임 ID 불러오기
games_enum_path = os.path.join(os.path.dirname(__file__), "games_enum.json")
with open(games_enum_path, "r", encoding="utf-8") as f:
    GAME_IDS = json.load(f)

def is_valid_review(text):
    # ✅ 수정된 정규 표현식 (특수문자 범위 수정)
    if re.search(r"[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,!?~()\"'\-]+", text) is None:
        return False

    total_len = len(text)
    if total_len < 10:
        return False  # 너무 짧은 리뷰 제외

    eng_count = len(re.findall(r'[a-zA-Z]', text))
    if eng_count / total_len > 0.3:
        return False

    return True


def fetch_reviews_with_filter(app_id, language="korean", delay=0.5):
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
            voted_up = r["voted_up"]
            playtime_forever = r.get("author", {}).get("playtime_forever", 0)
            weighted_vote_score = r.get("weighted_vote_score", 0)

            # 중복 제거 (리뷰 ID 기준)
            if review_id in seen_review_ids:
                continue

            # 필터 체크
            if not is_valid_review(text):
                filtered_reviews.append((app_id, int(voted_up), weighted_vote_score, playtime_forever, text))
                continue

            # 중복 체크
            seen_review_ids.add(review_id)

            # 통과된 리뷰 저장 (내용 제외)
            valid_reviews.append((app_id, int(voted_up), weighted_vote_score, playtime_forever))

        # 요청 간 딜레이
        time.sleep(delay)

    return valid_reviews, filtered_reviews


def save_reviews_to_csv(reviews, output_dir, filename, include_text=True):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if include_text:
            writer.writerow(["app_id", "voted_up", "weighted_vote_score", "playtime_forever", "review"])
        else:
            writer.writerow(["app_id", "voted_up", "weighted_vote_score", "playtime_forever"])
        writer.writerows(reviews)
    print(f"✅ {filename} 저장 완료")


def run():
    for game_name, app_id in GAME_IDS.items():
        print(f"🎮 {game_name} ({app_id}) 리뷰 수집 중...")
        valid_reviews, filtered_reviews = fetch_reviews_with_filter(app_id)
        save_reviews_to_csv(valid_reviews, "unfiltered", f"{app_id}.csv", include_text=False)
        save_reviews_to_csv(filtered_reviews, "filtered", f"{app_id}.csv", include_text=True)


# 실행 예시
if __name__ == '__main__':

    run()
