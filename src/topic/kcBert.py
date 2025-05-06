import os
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification

# 절대 경로를 사용하여 모델 로드
def load_kcbert_model(path="C:/Users/rhkda/PycharmProjects/PythonProject/src/topic/saved_kcbert_model"):
    if not os.path.exists(path):
        raise ValueError(f"경로 '{path}'에 모델이 존재하지 않습니다.")

    model = BertForSequenceClassification.from_pretrained(path)  # KcBERT 모델 로드
    tokenizer = BertTokenizer.from_pretrained(path)  # 토크나이저 로드
    print(f"✅ KcBERT 모델과 토크나이저가 {path}에서 불러와졌습니다.")
    return model, tokenizer


# 리뷰에 대한 감성 분석 함수
def analyze_sentiment_kcbert(reviews):
    model, tokenizer = load_kcbert_model()  # 모델을 로드
    results = []

    for review in reviews:
        inputs = tokenizer(review, return_tensors="pt", truncation=True, padding=True)

        # 모델을 이용한 예측
        with torch.no_grad():
            outputs = model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)  # 확률값 계산
            label = torch.argmax(probs).item()  # 라벨 추출 (긍정/부정)
            confidence = probs[0][label].item()  # 우호도 (확률)

            # 확신도가 낮으면 -1로 설정
            if confidence < 0.5:
                label = -1  # 불확실한 경우

            # 결과 저장
            results.append({
                "text": review,
                "label": label,  # 0: 부정, 1: 긍정, -1: 불확실
                "confidence": confidence  # 예측 확신도
            })

    return results
