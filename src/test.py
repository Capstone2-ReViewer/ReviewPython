import requests
import json

def check_playtime_field(app_id, num_pages=1):
    url = (
        f"https://store.steampowered.com/appreviews/{app_id}"
        f"?json=1&language=korean&day_range=730&filter=recent&review_type=all"
        f"&purchase_type=all&num_per_page=5&cursor=*&page={num_pages}"
    )

    res = requests.get(url)
    if res.status_code != 200:
        print(f"❌ 요청 실패: {res.status_code}")
        return

    # JSON 응답 파싱
    reviews = res.json().get("reviews", [])
    if not reviews:
        print("⚠️ 리뷰 데이터가 없습니다.")
        return

    # 각 리뷰의 플레이타임 확인
    for i, review in enumerate(reviews[:10]):  # 샘플 10개만 확인
        author_data = review.get("author", {})
        playtime_forever = author_data.get("playtime_forever", "N/A")
        print(f"📝 리뷰 {i+1} - 플레이타임: {playtime_forever}")

    # 전체 구조 출력 (테스트용)
    print("\n📦 전체 응답 구조")
    print(json.dumps(reviews[0], indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # 테스트할 앱 ID (예시: 730 = Counter-Strike: Global Offensive)
    test_app_id = 730
    check_playtime_field(test_app_id, num_pages=1)
