import json
import requests

def get_game_info(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=korean&cc=kr"
    try:
        res = requests.get(url)
        data = res.json()
        game_data = data.get(str(app_id))
        if not game_data or not game_data.get("success"):
            return None

        game = game_data["data"]
        price_raw = game.get("price_overview", {}).get("final")
        is_free = game.get("is_free", False)

        if price_raw is not None:
            price = price_raw // 100
            price_text = f"{price:,}"
        elif is_free:
            price = 0
            price_text = "무료"
        else:
            price = None
            price_text = "비공개"

        return {
            "appid": game.get("steam_appid"),
            "name": game.get("name"),
            "description": game.get("short_description"),
            "release_date": game.get("release_date", {}).get("date"),
            "price": price,
            "price_text": price_text,
            "discount": game.get("price_overview", {}).get("discount_percent"),
            "genres": [g["description"] for g in game.get("genres", [])],
            "categories": [c["description"] for c in game.get("categories", [])[:2]],
            "image": game.get("header_image")
        }
    except Exception as e:
        print(f"❌ {app_id} 요청 실패: {e}")
        return None