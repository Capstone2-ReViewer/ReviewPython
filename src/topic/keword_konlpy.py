import os
import pandas as pd
from konlpy.tag import Okt
from collections import Counter
from steamAPI.game_enum import get_game_codes

okt = Okt()

EXCLUDE = set([
    "스토리", "모드", "사람", "재미", "시간", "친구", "추천",
    "무기", "그래픽", "유저", "난이도", "처음", "엔딩", "컨텐츠", "시작", "보스",
    "몬스터", "월드", "멀티", "소울", "서버", "전작", "뉴비", "힐링", "진행", "전투",
    "퀘스트", "사양", "업데이트", "온라인", "할인", "생존", "장비", "혼자", "평가",
    "메인", "무료", "입문", "탐험", "시스템", "캐릭터", "한글화", "연출", "매력", "조작",
    "씨발", "버그", "패드", "병신", "새끼", "시발", "해킹", "계정", "생존자",
    "살인마", "심즈", "문명", "로딩", "스킨", "쓰레기", "짱깨", "패치", "망겜",
    "최적화", "프레임", "오류", "반복", "강제", "과금", "불편", "불안정", "욕설", "튕김"
])

# 수정된 경로: main.py 기준으로 steamAPI/unfiltered 폴더를 찾도록 한 단계 위로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNFILTERED_PATH = os.path.join(BASE_DIR, "steamAPI", "unfiltered")


def extract_keywords_from_reviews(app_id: int, df: pd.DataFrame):
    result = []
    for sentiment_value, sentiment_name in [(1, "positive"), (0, "negative")]:
        reviews = df[df["voted_up"] == sentiment_value]["review"].dropna().astype(str).tolist()
        tokens = []
        for review in reviews:
            nouns = okt.nouns(review)
            filtered = [n for n in nouns if len(n) > 1 and n in EXCLUDE]  # ✅ EXCLUDE에 정의된 키워드만 사용
            tokens.extend(filtered)
        counter = Counter(tokens)
        top_keywords = counter.most_common(3)  # ✅ 상위 3개만 추출
        seen = set()
        for keyword, count in top_keywords:
            if keyword not in seen and count > 1:  # ✅ count가 1인 키워드는 제외
                seen.add(keyword)
                result.append({
                    "app_id": app_id,
                    "sentiment": sentiment_name,
                    "keyword": keyword,
                    "count": count
                })
    return result


def run_keyword():
    all_data = []
    game_codes = get_game_codes()  # {"Dota 2": 570, ...}
    for name, app_id in game_codes.items():
        file_path = os.path.join(UNFILTERED_PATH, f"{app_id}.csv")
        if not os.path.exists(file_path):
            print(f"❌ {app_id}.csv 없음 → 스킵")
            continue
        try:
            df = pd.read_csv(file_path)
            if "review" not in df.columns or "voted_up" not in df.columns:
                print(f"⚠️ {app_id} 스킵 - 필요한 컬럼 없음")
                continue
            print(f"[진행] {name} ({app_id}) 키워드 추출 중...")
            keyword_data = extract_keywords_from_reviews(app_id, df)
            if keyword_data:
                all_data.extend(keyword_data)
                print(f"✅ {name} ({app_id}) 키워드 상위 3개: {[k['keyword'] for k in keyword_data]}")
            else:
                print(f"ℹ️ {name} ({app_id}) 지정 키워드 없음")
        except Exception as e:
            print(f"❌ {name} ({app_id}) 처리 실패: {e}")
    return all_data
