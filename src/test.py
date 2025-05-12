import csv
import os
from datetime import datetime, timezone
from steamAPI.review import fetch_reviews_with_filter

# 전체 게임 목록
GAME_IDS = {
    "Counter-Strike: Global Offensive": 730,
    "Dota 2": 570,
    "PLAYERUNKNOWN'S BATTLEGROUNDS": 578080,
    "Apex Legends": 1172470,
    "Grand Theft Auto V": 271590,
    "Rust": 252490,
    "Destiny 2": 1085660,
    "ARK: Survival Evolved": 346110,
    "Warframe": 230410,
    "Tom Clancy's Rainbow Six Siege": 359550,
    "Team Fortress 2": 440,
    "Garry's Mod": 4000,
    "Rocket League": 252950
}

OUTPUT_DIR = "all_game_reviews"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_reviews_to_csv(app_id, reviews, filename):
    # ✅ 파일을 "a" 모드로 열어 데이터 누적
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # 파일이 비어 있으면 헤더 추가
        if os.stat(filename).st_size == 0:
            writer.writerow(["app_id", "timestamp_created", "year_month", "playtime_forever", "final_score"])  # 컬럼명

        for review in reviews:
            # 리뷰 데이터 추출
            timestamp = review["timestamp_created"]
            year_month = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m")
            playtime_forever = review["playtime_forever"]
            final_score = 50  # 기본 점수 (수정 가능)

            # 데이터 저장
            writer.writerow([app_id, timestamp, year_month, playtime_forever, final_score])

    print(f"✅ {len(reviews)}개의 리뷰가 '{filename}' 파일로 저장되었습니다.")


if __name__ == "__main__":
    for game_name, app_id in GAME_IDS.items():
        print(f"🔄 {game_name} ({app_id}) 게임의 리뷰 가져오는 중...")

        # ✅ 리뷰 수집
        valid_reviews, filtered_reviews = fetch_reviews_with_filter(app_id)

        # ✅ 유효 리뷰 저장
        valid_csv_filename = os.path.join(OUTPUT_DIR, f"{app_id}_valid_reviews.csv")
        save_reviews_to_csv(app_id, valid_reviews, valid_csv_filename)

        # ✅ 필터된 리뷰도 저장
        filtered_csv_filename = os.path.join(OUTPUT_DIR, f"{app_id}_filtered_reviews.csv")
        save_reviews_to_csv(app_id, filtered_reviews, filtered_csv_filename)

        print(f"✅ {game_name} 리뷰 저장 완료 (유효: {len(valid_reviews)}개, 필터됨: {len(filtered_reviews)}개)\n")
