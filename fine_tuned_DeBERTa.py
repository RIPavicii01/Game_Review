import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import get_linear_schedule_with_warmup, logging
from transformers import DebertaV2ForSequenceClassification, DebertaV2Tokenizer
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm import tqdm

# 1. 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device: ", device)

# 경고 제거
logging.set_verbosity_error()

# 2. 데이터 불러오기 및 정제
path = "metacritic_review_labeled.csv"
df = pd.read_csv(path, encoding="utf-8")

# 결측 제거 및 레이블 정제
df = df.dropna(subset=['Text', 'predicted_label'])
df = df[df['predicted_label'].astype(str).str.strip().isin(['0', '1'])]

data_X = df['Text'].astype(str).tolist()  # 문자열 리스트
labels = df['predicted_label'].astype(int).values  # 정수형 레이블 배열

# 3. 토크나이징
tokenizer = DebertaV2Tokenizer.from_pretrained('microsoft/deberta-v3-small')
inputs = tokenizer(
    data_X,
    truncation=True,
    padding="max_length",
    max_length=256,
    add_special_tokens=True,
    return_tensors='pt',  # 텐서 반환
    clean_up_tokenization_spaces=True
)

input_ids = inputs['input_ids'].tolist()
attention_mask = inputs['attention_mask'].tolist()

# 4. 학습/검증 데이터 분리
train, validation, train_y, validation_y = train_test_split(input_ids, labels, test_size=0.2, random_state=2025)
train_mask, validation_mask, _, _ = train_test_split(attention_mask, labels, test_size=0.2, random_state=2025)

# 5. TensorDataset 구성
batch_size = 8
train_inputs = torch.tensor(train)
train_labels = torch.tensor(train_y)
train_masks = torch.tensor(train_mask)
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

validation_inputs = torch.tensor(validation)
validation_labels = torch.tensor(validation_y)
validation_masks = torch.tensor(validation_mask)
validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

# 6. 모델 로드 및 설정
model = DebertaV2ForSequenceClassification.from_pretrained('microsoft/deberta-v3-small', num_labels=2)
model.to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, eps=1e-8)
epochs = 4
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=len(train_dataloader) * epochs
)

# 7. 학습 루프
epoch_result = []
for e in range(epochs):
    model.train()
    total_train_loss = 0

    progress_bar = tqdm(train_dataloader, desc=f"Training Epoch {e+1}", leave=True)
    for batch in progress_bar:
        batch_ids, batch_mask, batch_labels = [b.to(device) for b in batch]

        model.zero_grad()
        output = model(batch_ids, attention_mask=batch_mask, labels=batch_labels)
        loss = output.loss
        total_train_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        progress_bar.set_postfix({'loss': loss.item()})

    avg_train_loss = total_train_loss / len(train_dataloader)

    # 8. 검증
    model.eval()
    val_pred = []
    val_true = []

    for batch in tqdm(validation_dataloader, desc=f"Validation Epoch {e + 1}", leave=True):
        batch_ids, batch_mask, batch_labels = [b.to(device) for b in batch]

        with torch.no_grad():
            output = model(batch_ids, attention_mask=batch_mask)

        logits = output.logits
        pred = torch.argmax(logits, dim=1)
        val_pred.extend(pred.cpu().numpy())
        val_true.extend(batch_labels.cpu().numpy())

    val_accuracy = (np.array(val_pred) == np.array(val_true)).mean()
    epoch_result.append((avg_train_loss, val_accuracy))

# 9. 결과 출력
for idx, (loss, val_acc) in enumerate(epoch_result, start=1):
    print(f"Epoch {idx}: Train loss: {loss:.4f}, Validation Accuracy: {val_acc:.4f}")

# 10. 모델 저장
save_path = "D:/Game_review/deberta_custom_model_metacritic"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"\n모델과 토크나이저가 저장되었습니다 → {save_path}")
