from steamAPI.game_enum import get_game_codes
from steamAPI.game_info import get_game_info
from steamAPI.update_dates import get_updates
from steamAPI.review import fetch_reviews
from save_to_db import save_game_info, save_updates

if __name__ == "__main__":
    # 게임 코드 로드
    codes = get_game_codes()

    # 게임 정보 수집
    game_info_dict = {}
    for name, app_id in codes.items():
        info = get_game_info(app_id)
        if info:
            info["game_name"] = name
            game_info_dict[app_id] = info

    # 게임 정보 저장
    save_game_info(game_info_dict)

    # 업데이트 내역 수집
    update_dict = {}
    for name, app_id in codes.items():
        updates = get_updates(app_id)
        if updates:
            update_dict[app_id] = {"name": name, "update_dates": updates}

    # 업데이트 내역 저장
    save_updates(update_dict)

    # 리뷰 데이터 수집
    reviews_dict = {}
    for name, app_id in codes.items():
        reviews = fetch_reviews(app_id, language="korean", num_pages=3)
        if reviews:
            reviews_dict[app_id] = {"name": name, "reviews": reviews}
            print(f"✅ {name} ({app_id}) 리뷰 수집 완료")

    print("\n🚀 리뷰 데이터 수집 완료!")
