import requests
from datetime import datetime, timedelta, UTC

# ✅ 함수만 따로 정의 (import용)
def get_updates(app_id, max_news=50):
    url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={app_id}&count={max_news}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return []

        news_items = res.json().get("appnews", {}).get("newsitems", [])
        keywords = ["update", "patch", "major", "release", "season", "expansion"]

        today = datetime.now(UTC)
        two_years_ago = today - timedelta(days=730)

        updates = []
        for item in news_items:
            title = item["title"].lower()
            if any(keyword in title for keyword in keywords):
                ts = datetime.fromtimestamp(item["date"], tz=UTC)
                if ts >= two_years_ago:
                    updates.append(ts.strftime("%Y-%m-%d"))

        return sorted(set(updates), reverse=True)

    except Exception as e:
        print(f"❌ {app_id} 뉴스 가져오기 실패: {e}")
        return []