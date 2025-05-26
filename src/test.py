import os
import pandas as pd
from konlpy.tag import Okt
from collections import Counter

# === 경로 설정 ===
filtered_dir = r"C:\Users\rhkda\PycharmProjects\PythonProject\src\steamAPI\filtered"
output_path = r"C:\Users\rhkda\PycharmProjects\PythonProject\bertopic_output\all_topics.csv"

# === 키워드 필터 기준 ===
positive_keywords = ["플레이", "스토리", "모드", "사람", "재미", "시간", "진짜", "친구", "추천", "정말",
    "무기", "그래픽", "유저", "난이도", "처음", "엔딩", "컨텐츠", "시작", "보스", "장점",
    "몬스터", "월드", "멀티", "소울", "서버", "전작", "뉴비", "힐링", "진행", "전투",
    "퀘스트", "사양", "스팀", "업데이트", "온라인", "할인", "생존", "장비", "혼자", "평가",
    "메인", "무료", "입문", "탐험", "시스템", "캐릭터", "한글화", "연출", "매력", "조작"]

negative_keywords = ["씨발", "버그", "진짜", "서버", "플레이", "유저", "패드", "사람", "시간", "병신",
    "새끼", "재미", "시발", "문제", "스토리", "해킹", "모드", "계정", "친구", "생존자",
    "존나", "살인마", "스팀", "심즈", "문명", "시작", "업데이트", "로딩", "난이도", "스킨",
    "처음", "쓰레기", "짱깨", "패치", "소울", "그래픽", "망겜", "컨텐츠", "진행", "전투",
    "최적화", "프레임", "오류", "반복", "강제", "과금", "불편", "불안정", "욕설", "튕김"]

EXCLUDE = set(positive_keywords + negative_keywords)

# === 리뷰 필터 함수 ===
def filter_reviews(df, voted_up, keyword_list):
    sub = df[df["voted_up"] == voted_up].copy()
    if "review" not in sub.columns:
        return []
    sub = sub[sub["review"].notna()]
    sub["review"] = sub["review"].astype(str)
    filtered = sub[sub["review"].apply(lambda x: any(k in x for k in keyword_list))]
    print(f"[DEBUG] voted_up={voted_up} 리뷰 수: {len(sub)} → 필터 통과: {len(filtered)}")
    if len(filtered) <= 5:
        return []
    return filtered["review"].tolist()

# === 키워드 추출 ===
okt = Okt()
all_counts = []

for filename in os.listdir(filtered_dir):
    if not filename.endswith(".csv"):
        continue
    app_id = filename.replace(".csv", "")
    path = os.path.join(filtered_dir, filename)
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"❌ {app_id} 로드 실패: {e}")
        continue

    if "review" not in df.columns or "voted_up" not in df.columns:
        print(f"⚠️ {app_id} 누락 컬럼. 스킵 → {df.columns.tolist()}")
        continue

    df["review"] = df["review"].astype(str)

    for sentiment, reviews in [("positive", filter_reviews(df, 1, positive_keywords)),
                                ("negative", filter_reviews(df, 0, negative_keywords))]:
        tokens = []
        for review in reviews:
            nouns = okt.nouns(review)
            nouns = [n for n in nouns if len(n) > 1 and n not in EXCLUDE]
            tokens.extend(nouns)

        counter = Counter(tokens)
        for keyword, count in counter.items():
            all_counts.append({"app_id": app_id, "sentiment": sentiment, "keyword": keyword, "count": count})

# === 저장 ===
if all_counts:
    pd.DataFrame(all_counts).to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 키워드 데이터를 하나의 파일로 저장 완료 → {output_path}")
else:
    print("⚠️ 저장할 키워드 데이터가 없습니다.")
