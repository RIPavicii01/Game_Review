import torch
import pandas as pd
from transformers import MobileBertForSequenceClassification, MobileBertTokenizer
from tqdm import tqdm
from sklearn.metrics import accuracy_score
from transformers import DebertaV2ForSequenceClassification

# 1. 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# 2. 데이터 불러오기 및 정제
df = pd.read_csv("metacitic_review.csv", encoding="utf-8-sig")
df = df[df['Text'].apply(lambda x: isinstance(x, str) and x.strip() != "")]
df['Score'] = df['Score'].apply(lambda x: x / 10 if x > 10 else x)
print("리뷰 개수:", len(df))

# 3. 토크나이징
tokenizer = MobileBertTokenizer.from_pretrained("google/mobilebert-uncased", do_lower_case=True)
inputs = tokenizer(
    list(df['Text'].values),
    truncation=True,
    padding="max_length",
    max_length=256,
    return_tensors="pt"
)

input_ids = inputs['input_ids']         # ⛔️ GPU로 이동 X
attention_mask = inputs['attention_mask']

# 4. 데이터셋 구성 (CPU 상태로 유지)
test_data = torch.utils.data.TensorDataset(input_ids, attention_mask)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=8)

# 5. 모델 불러오기
model = DebertaV2ForSequenceClassification.from_pretrained("D:\\Game_review\\deberta_custom_model_metacritic")
model.to(device)
model.eval()

# 6. 감정 추론
predictions = []
for batch in tqdm(test_loader, desc="Inferring Sentiments"):
    input_ids_batch, mask_batch = [b.to(device) for b in batch]  # ✅ 여기서 GPU로 이동

    with torch.no_grad():
        outputs = model(input_ids_batch, attention_mask=mask_batch)

    logits = outputs.logits
    preds = torch.argmax(logits, dim=1)
    predictions.extend(preds.cpu().numpy())  # ✅ 결과는 다시 CPU로

# 7. Score 기준 감정 라벨 생성 (0~5 부정: 0, 6~10 긍정: 1)
df['ScoreBasedLabel'] = df['Score'].apply(lambda x: 1 if x >= 6 else 0)

# 8. 정확도 평가
df['PredictedSentiment'] = predictions
acc = accuracy_score(df['ScoreBasedLabel'], df['PredictedSentiment'])
print(f"\n✅ 감정 분석 정확도 (Score 기준 비교): {acc:.4f}")
