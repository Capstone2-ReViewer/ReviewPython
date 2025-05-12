from pymongo import MongoClient
import pymongo  # ✅ pymongo 추가
import hashlib

# ✅ MongoDB 연결
client = MongoClient("mongodb://localhost:27017")
db = client["steam"]
collection_game = db["game_info"]
collection_update = db["updates"]
collection_score = db["score_playtime"]

def save_game_info(game_info_dict):
    for app_id, game_info in game_info_dict.items():
        name = game_info.get("name", "")
        print(f"\n🎮 {name} ({app_id}) 게임 정보 저장 중...")
        if game_info:
            collection_game.update_one({"appid": app_id}, {"$set": game_info}, upsert=True)
            print("✅ 게임 정보 저장 완료")
        else:
            print("⚠️ 게임 정보 없음")

def save_updates(update_dict):
    for app_id, update_info in update_dict.items():
        name = update_info.get("name", "")
        updates = update_info.get("update_dates", [])
        print(f"\n🛠 {name} ({app_id}) 업데이트 내역 저장 중...")
        if updates:
            collection_update.update_one(
                {"appid": app_id},
                {"$set": {"game_name": name, "update_dates": updates}},
                upsert=True
            )
            print(f"✅ 업데이트 {len(updates)}개 저장 완료")
        else:
            print("⚠️ 업데이트 내역 없음")

def save_score_playtime(score_data_list):
    if not score_data_list:
        print("⚠️ 저장할 데이터가 없습니다.")
        return

    # 데이터 분할 저장
    bulk_operations = []
    for score_data in score_data_list:
        app_id = score_data.get("app_id")
        year_month = score_data.get("year_month")
        final_score = score_data.get("final_score")
        playtime_forever = score_data.get("playtime_forever", 0)

        # ✅ 고유 ID 생성 (해시 사용)
        unique_string = f"{app_id}_{year_month}_{playtime_forever}_{final_score}"
        unique_id = hashlib.sha1(unique_string.encode()).hexdigest()

        # ✅ 저장 데이터 확인
        print(f"📝 저장할 개별 데이터: {score_data}")

        # MongoDB에 데이터 저장 (upsert)
        bulk_operations.append(
            pymongo.UpdateOne(
                {"_id": unique_id},  # ✅ 고유 ID 사용
                {"$set": {
                    "app_id": app_id,
                    "year_month": year_month,
                    "final_score": final_score,
                    "playtime_forever": playtime_forever
                }},
                upsert=True
            )
        )

    # Bulk Write 실행
    if bulk_operations:
        result = collection_score.bulk_write(bulk_operations)
        print(f"✅ {result.upserted_count + result.modified_count}개의 데이터 저장 완료")

    print("\n🚀 모든 점수 데이터 저장 완료!")

    print("\n🚀 모든 점수 데이터 저장 완료!")
