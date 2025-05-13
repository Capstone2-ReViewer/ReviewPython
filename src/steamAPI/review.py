import os
import csv
import json
import re
import requests
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILTERED_DIR = os.path.join(BASE_DIR, "filtered")
UNFILTERED_DIR = os.path.join(BASE_DIR, "unfiltered")
GAMES_ENUM_PATH = os.path.join(BASE_DIR, "games_enum.json")
os.makedirs(FILTERED_DIR, exist_ok=True)
os.makedirs(UNFILTERED_DIR, exist_ok=True)

import re


def is_valid_review(text):
    # ✅ 허용된 문자 체크
    if not re.match(r"^[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,!?~()\-\"“”ㅎㅠㅋ^]+$", text.strip()):
        print(f"❌ 허용되지 않는 문자 포함: {text}")
        return False

    # ✅ 최소 길이 필터 (5자 이상)
    stripped_text = text.strip()
    total_len = len(stripped_text)
    if total_len < 5:
        print(f"❌ 너무 짧은 리뷰: {text}")
        return False

    # ✅ 영문 비율 필터 (30% 이하)
    eng_count = len(re.findall(r"[a-zA-Z]", stripped_text))
    pure_text_len = len(re.sub(r"[^a-zA-Zㄱ-ㅎ가-힣0-9]", "", stripped_text))

    # 영문 비율이 계산되지 않는 경우 (모든 글자가 특수문자일 때)
    if pure_text_len == 0:
        print(f"❌ 순수 텍스트 없음: {text}")
        return False

    # 영문 비율 필터
    ratio = eng_count / pure_text_len
    if ratio > 0.3:
        print(f"❌ 영문 비율 초과 ({ratio:.2f}): {text}")
        return False

    print(f"✅ 통과: {text}")
    return True



def save_reviews_to_csv(reviews, folder_path, filename):
    filepath = os.path.join(folder_path, filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # ✅ 헤더 추가
        writer.writerow(["app_id", "voted_up", "weighted_vote_score", "playtime_forever", "timestamp_created", "review"])
        for review in reviews:
            writer.writerow([
                review["app_id"],
                review["voted_up"],
                review["weighted_vote_score"],
                review["playtime_forever"],
                review["timestamp_created"],
                review["review"]
            ])
    print(f"✅ 리뷰 저장 완료: {filepath}")

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

        if not reviews or cursor == "*":
            break

        for r in reviews:
            review_id = r.get("recommendationid")
            text = r.get("review", "").strip()
            timestamp_created = r.get("timestamp_created", 0)
            voted_up = r.get("voted_up")
            playtime_forever = r.get("author", {}).get("playtime_forever", 0)
            weighted_vote_score = r.get("weighted_vote_score", 0.5)

            if review_id in seen_review_ids:
                continue

            seen_review_ids.add(review_id)

            review_data = {
                "app_id": app_id,
                "voted_up": int(voted_up),
                "weighted_vote_score": float(weighted_vote_score),
                "playtime_forever": int(playtime_forever),
                "timestamp_created": int(timestamp_created),
                "review": text
            }

            # ✅ 필터 체크 (반대로 저장 문제 수정)
            if is_valid_review(text):
                valid_reviews.append(review_data)  # 필터 통과 (unfiltered)
            else:
                filtered_reviews.append(review_data)  # 필터 실패 (filtered)

        time.sleep(0.5)

    return valid_reviews, filtered_reviews



def run_review():
    # ✅ 게임 코드 로드 (games_enum.json 직접 로드)
    with open(GAMES_ENUM_PATH, "r", encoding="utf-8") as f:
        game_codes = json.load(f)

    for app_name, app_id in game_codes.items():
        print(f"🎮 {app_name} ({app_id}) 리뷰 수집 시작...")
        valid_reviews, filtered_reviews = fetch_reviews_with_filter(app_id)

        # 필터된 리뷰 저장
        save_reviews_to_csv(filtered_reviews, FILTERED_DIR, f"{app_id}.csv")

        # 필터되지 않은 리뷰 저장
        save_reviews_to_csv(valid_reviews, UNFILTERED_DIR, f"{app_id}.csv")

        print(f"✅ {app_name} ({app_id}) 리뷰 저장 완료")


# ✅ 테스트 실행
if __name__ == "__main__":
    run_review()
