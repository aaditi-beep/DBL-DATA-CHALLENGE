from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from datasets import load_dataset
from sklearn.metrics import classification_report, confusion_matrix
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

#configuration
model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
batch_size = 32 #change as per computer's capacity

#load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)
model.eval()

#load tweeteval dataset
print("Loading TweetEval dataset...")
dataset = load_dataset("tweet_eval", "sentiment")
test_data = dataset["test"]
texts = test_data["text"]
true_labels = test_data["label"]

#sentiment prediction
print("Running sentiment analysis...")
pred_labels = []

for i in tqdm(range(0, len(texts), batch_size)):
    batch_texts = texts[i:i+batch_size]
    inputs = tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        batch_preds = torch.argmax(probs, dim=1).cpu().numpy()
        pred_labels.extend(batch_preds)

#metrics (if needed)
target_names = ["negative", "neutral", "positive"]
# print("\nClassification Report:\n")
# print(classification_report(true_labels, pred_labels, target_names=target_names))

#confusion matrix
cm = confusion_matrix(true_labels, pred_labels)
df_cm = pd.DataFrame(cm, index=target_names, columns=target_names)

plt.figure(figsize=(6, 4))
sns.heatmap(df_cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix: XLM-R on TweetEval")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.tight_layout()
plt.show()
