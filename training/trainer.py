import os
import json
import torch
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from transformers import TrainingArguments, Trainer, EarlyStoppingCallback
from torch.utils.data import Dataset
from .model import load_model_and_tokenizer, get_device
from .dataset import prepare_dataset, split_dataset
from .config import MODEL_CONFIG, TRAINING_CONFIG, CATEGORIES

class ClassificationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    acc = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    prec = precision_score(labels, predictions, average='weighted', zero_division=0)
    rec = recall_score(labels, predictions, average='weighted', zero_division=0)

    return {
        'accuracy': acc,
        'f1': f1,
        'precision': prec,
        'recall': rec
    }

def train_fold(fold_idx, train_data, val_data, output_dir, device):
    print(f"\n[fold {fold_idx}] Iniciando treinamento...")

    model, tokenizer = load_model_and_tokenizer()
    model.to(device)

    train_texts = [item['text'] for item in train_data]
    train_labels = [item['label'] for item in train_data]
    val_texts = [item['text'] for item in val_data]
    val_labels = [item['label'] for item in val_data]

    train_dataset = ClassificationDataset(train_texts, train_labels, tokenizer)
    val_dataset = ClassificationDataset(val_texts, val_labels, tokenizer)

    checkpoint_dir = output_dir / f"fold_{fold_idx}" / "checkpoint-best"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(checkpoint_dir),
        num_train_epochs=TRAINING_CONFIG['epochs'],
        per_device_train_batch_size=TRAINING_CONFIG['batch_size'],
        per_device_eval_batch_size=TRAINING_CONFIG['batch_size'],
        learning_rate=TRAINING_CONFIG['learning_rate'],
        warmup_steps=TRAINING_CONFIG['warmup_steps'],
        weight_decay=TRAINING_CONFIG['weight_decay'],
        logging_dir=str(output_dir / f"fold_{fold_idx}" / "logs"),
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=device.type == "cuda",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    trainer.train()

    eval_results = trainer.evaluate()
    print(f"[fold {fold_idx}] Resultados: {eval_results}")

    model.save_pretrained(str(output_dir / f"fold_{fold_idx}"))
    tokenizer.save_pretrained(str(output_dir / f"fold_{fold_idx}"))

    predictions = trainer.predict(val_dataset)
    preds = np.argmax(predictions.predictions, axis=1)

    cm = confusion_matrix(val_labels, preds, labels=list(range(len(CATEGORIES))))

    metrics = {
        'fold': fold_idx,
        'accuracy': float(eval_results.get('eval_accuracy', 0)),
        'f1': float(eval_results.get('eval_f1', 0)),
        'precision': float(eval_results.get('eval_precision', 0)),
        'recall': float(eval_results.get('eval_recall', 0)),
        'total_samples': len(val_data)
    }

    with open(output_dir / f"fold_{fold_idx}" / "evaluation.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    np.save(output_dir / f"fold_{fold_idx}" / "confusion_matrix.npy", cm)

    cm_normalized = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    with open(output_dir / f"fold_{fold_idx}" / "confusion_matrix.json", 'w') as f:
        json.dump(cm_normalized.tolist(), f, indent=2)

    with open(output_dir / f"fold_{fold_idx}" / "trainer_state.json", 'w') as f:
        json.dump(trainer.state.state, f, indent=2)

    return metrics, cm

def run_training():
    print("[train] Iniciando pipeline de treinamento...")

    data = prepare_dataset()
    print(f"[train] Dataset carregado: {len(data)} amostras")

    device = get_device()
    output_dir = Path(__file__).parent.parent / "models" / "checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    all_cms = []

    k_folds = TRAINING_CONFIG['k_folds']
    skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)

    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(texts, labels)):
        train_data = [data[i] for i in train_idx]
        val_data = [data[i] for i in val_idx]

        metrics, cm = train_fold(fold_idx, train_data, val_data, output_dir, device)
        results.append(metrics)
        all_cms.append(cm)

        print(f"[fold {fold_idx}] Concluído: {metrics}")

    aggregate_metrics(results, output_dir)

    print("\n[train] Treinamento concluído!")
    return results

def aggregate_metrics(results, output_dir):
    import pandas as pd

    total_accuracy = np.mean([r['accuracy'] for r in results])
    total_f1 = np.mean([r['f1'] for r in results])
    total_precision = np.mean([r['precision'] for r in results])
    total_recall = np.mean([r['recall'] for r in results])

    std_accuracy = np.std([r['accuracy'] for r in results])
    std_f1 = np.std([r['f1'] for r in results])

    summary = {
        'k_folds': len(results),
        'mean_accuracy': float(total_accuracy),
        'mean_f1': float(total_f1),
        'mean_precision': float(total_precision),
        'mean_recall': float(total_recall),
        'std_accuracy': float(std_accuracy),
        'std_f1': float(std_f1),
        'per_fold': results
    }

    with open(output_dir / "training_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n[summary] Métricas agregadas:")
    print(f"  Accuracy: {total_accuracy*100:.2f}% ± {std_accuracy*100:.2f}%")
    print(f"  F1-Score: {total_f1*100:.2f}% ± {std_f1*100:.2f}%")
    print(f"  Precision: {total_precision*100:.2f}%")
    print(f"  Recall: {total_recall*100:.2f}%")

    return summary

if __name__ == "__main__":
    run_training()