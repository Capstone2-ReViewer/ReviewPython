from bertopic import BERTopic

# BERTopic 모델 저장 함수
def save_bertopic_model(topic_model, path="./saved_bertopic_model"):
    topic_model.save(path)
    print(f"✅ BERTopic 모델이 {path}에 저장되었습니다.")

# BERTopic 모델 불러오기 함수
def load_bertopic_model(path="./saved_bertopic_model"):
    topic_model = BERTopic.load(path)
    print(f"✅ BERTopic 모델이 {path}에서 불러와졌습니다.")
    return topic_model
