import torch
import pandas as pd
import random
from torch.utils.data import DataLoader, Dataset
from transformers import BertForSequenceClassification, BertTokenizer
import torch.optim as optim

# 1. 데이터 로드
def load_data(file_path):
    df = pd.read_csv(file_path)
    df = df[df['label'] != -1]  # ❗ -1 제거
    return df['review'].tolist(), df['label'].tolist()

# 2. EDA 기법 (WordNet 제거)
def eda(text, alpha_ri=0.1, alpha_rs=0.1, alpha_rd=0.1, num_aug=1):
    words = text.split()
    n = len(words)
    augmented_texts = set()

    # RI (Random Insertion)
    if alpha_ri > 0:
        for _ in range(int(alpha_ri * n)):
            words.insert(random.randint(0, n), random.choice(words))

    # RS (Random Swap)
    if alpha_rs > 0:
        for _ in range(int(alpha_rs * n)):
            swap_idx1, swap_idx2 = random.sample(range(n), 2)
            words[swap_idx1], words[swap_idx2] = words[swap_idx2], words[swap_idx1]

    # RD (Random Deletion)
    if alpha_rd > 0:
        words = [w for w in words if random.random() > alpha_rd]

    # 조합 후 결과 반환
    augmented_texts.add(" ".join(words))
    return list(augmented_texts)

# 3. Dataset 클래스 정의
class ReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len, augment_prob=0.3):
        self.texts = []
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

        # 증강 처리
        for text in texts:
            self.texts.append(text)  # 원본 추가
            if random.random() < augment_prob:
                augmented_texts = eda(text, alpha_ri=0.05, alpha_rs=0.05, alpha_rd=0.05)
                self.texts.extend(augmented_texts)

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = self.texts[item]
        label = self.labels[item % len(self.labels)]
        encoding = self.tokenizer.encode_plus(
            text,
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            add_special_tokens=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# 4. 모델 저장 함수
def save_kcbert_model(model, tokenizer, path="./saved_kcbert_model"):
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    print(f"✅ 모델 저장 완료: {path}")

# 5. 학습 함수
def train_kcbert_model():
    file_path = './review_labeled.csv'
    texts, labels = load_data(file_path)

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    dataset = ReviewDataset(texts, labels, tokenizer, max_len=128, augment_prob=0.3)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    optimizer = optim.Adam(model.parameters(), lr=1e-5)

    model.train()
    for epoch in range(4):
        total_loss = 0
        for i, batch in enumerate(dataloader):
            input_ids = batch['input_ids']
            attention_mask = batch['attention_mask']
            labels = batch['labels']

            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"📘 Epoch {epoch + 1} 완료 - 평균 Loss: {total_loss / len(dataloader):.4f}")

    save_kcbert_model(model, tokenizer)

# 6. 실행
if __name__ == "__main__":
    train_kcbert_model()
