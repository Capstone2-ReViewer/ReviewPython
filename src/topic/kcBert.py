import os
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification


def load_kcbert_model(path="C:/Users/rhkda/PycharmProjects/PythonProject/src/topic/saved_kcbert_model"):
    if not os.path.exists(path):
        raise ValueError(f"경로 '{path}'에 모델이 존재하지 않습니다.")

    model = BertForSequenceClassification.from_pretrained(path)
    tokenizer = BertTokenizer.from_pretrained(path)
    print(f"✅ KcBERT 모델과 토크나이저가 {path}에서 불러와졌습니다.")
    return model, tokenizer


def analyze_sentiment_kcbert(reviews):
    model, tokenizer = load_kcbert_model()
    results = []

    print(f"📝 분석할 리뷰 개수: {len(reviews)}")

    for review in reviews:
        # ✅ 데이터 순서에 맞춰 처리
        inputs = tokenizer(review, return_tensors="pt", truncation=True, padding=True)

        # 모델을 이용한 예측
        with torch.no_grad():
            outputs = model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)  # 확률값 계산
            label = torch.argmax(probs).item()  # 라벨 추출 (긍정/부정)
            confidence = probs[0][label].item()  # 우호도 (확률)

            # 결과 저장
            results.append({
                "label": label,  # 0: 부정, 1: 긍정, -1: 불확실
                "confidence": confidence  # 예측 확신도
            })


    print(f"✅ 총 {len(results)}개의 리뷰 분석 완료")
    return results
