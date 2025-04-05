import json

# ✅ 게임 코드 로드 함수
def get_game_codes(path="steamAPI/games_enum.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
