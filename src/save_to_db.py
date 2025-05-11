from pymongo import MongoClient

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

    for score_data in score_data_list:
        app_id = score_data.get("app_id")
        year_month = score_data.get("year_month")
        final_score = score_data.get("final_score")
        playtime_forever = score_data.get("playtime_forever", 0)

        # MongoDB에 데이터 저장 (upsert)
        collection_score.update_one(
            {"app_id": app_id, "year_month": year_month},
            {"$set": {
                "app_id": app_id,
                "year_month": year_month,
                "final_score": final_score,
                "playtime_forever": playtime_forever
            }},
            upsert=True
        )
        print(f"✅ {app_id} ({year_month}) 데이터 저장 완료")

    print("\n🚀 모든 점수 데이터 저장 완료!")


# ✅ 테스트 데이터
if __name__ == "__main__":
    test_data = [
        {"app_id": 730, "year_month": "2024-05", "final_score": 85.0, "playtime_forever": 1200},
        {"app_id": 570, "year_month": "2024-06", "final_score": 78.5, "playtime_forever": 3000},
        {"app_id": 440, "year_month": "2024-07", "final_score": 92.0, "playtime_forever": 500},
    ]
    save_score_playtime(test_data)