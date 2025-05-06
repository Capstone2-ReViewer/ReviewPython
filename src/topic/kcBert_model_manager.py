from transformers import BertForSequenceClassification, BertTokenizer

# KcBERT 모델 저장 함수
def save_kcbert_model(model, tokenizer, path="./saved_kcbert_model"):
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    print(f"✅ KcBERT 모델과 토크나이저가 {path}에 저장되었습니다.")

# KcBERT 모델 불러오기 함수
def load_kcbert_model(path="./saved_kcbert_model"):
    model = BertForSequenceClassification.from_pretrained(path)
    tokenizer = BertTokenizer.from_pretrained(path)
    print(f"✅ KcBERT 모델과 토크나이저가 {path}에서 불러와졌습니다.")
    return model, tokenizer