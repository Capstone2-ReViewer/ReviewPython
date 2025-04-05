from pymongo import MongoClient

# ✅ MongoDB 연결
client = MongoClient("mongodb://localhost:27017")
db = client["steam"]
collection_game = db["game_info"]
collection_update = db["updates"]

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
