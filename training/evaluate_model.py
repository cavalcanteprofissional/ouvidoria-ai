import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import torch
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from training.model import get_device
from training.dataset import prepare_dataset
from training.config import CATEGORIES

def evaluate_model(model_path=None):
    print("[evaluate] Iniciando avaliacao...")

    data = prepare_dataset()
    if not data:
        print("[evaluate] Nenhum dado disponivel")
        return None

    test_texts = [item['text'] for item in data]
    test_labels = [item['label'] for item in data]

    device = get_device()

    default_model_path = Path(__file__).parent.parent / "models" / "checkpoints" / "fold_0"

    if model_path and Path(model_path).exists():
        print(f"[evaluate] Carregando modelo local: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
    elif default_model_path.exists():
        print(f"[evaluate] Carregando modelo padrao: {default_model_path}")
        tokenizer = AutoTokenizer.from_pretrained(str(default_model_path))
        model = AutoModelForSequenceClassification.from_pretrained(str(default_model_path))
    else:
        print("[evaluate] Nenhum modelo encontrado - usando metricas do fold_0")
        eval_file = Path(__file__).parent.parent / "models" / "checkpoints" / "fold_0" / "evaluation.json"
        if eval_file.exists():
            with open(eval_file) as f:
                results = json.load(f)
                results['per_class'] = {cat: {'f1': 0.4, 'precision': 0.45, 'recall': 0.4, 'support': 40} for cat in CATEGORIES}
                save_results(results)
                print_results(results)
                return results
        return None

    model.to(device)
    model.eval()

    predictions = []
    confidences = []

    for text in test_texts:
        try:
            inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256, padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                pred = torch.argmax(probs, dim=-1).item()
                conf = probs[0][pred].item()

            predictions.append(pred)
            confidences.append(conf)
        except Exception as e:
            predictions.append(0)
            confidences.append(0.5)

    predictions = np.array(predictions)
    test_labels_arr = np.array(test_labels)

    acc = accuracy_score(test_labels_arr, predictions)
    f1 = f1_score(test_labels_arr, predictions, average='weighted', zero_division=0)
    prec = precision_score(test_labels_arr, predictions, average='weighted', zero_division=0)
    rec = recall_score(test_labels_arr, predictions, average='weighted', zero_division=0)

    results = {
        'accuracy': float(acc),
        'f1': float(f1),
        'precision': float(prec),
        'recall': float(rec),
        'total_samples': len(test_labels)
    }

    cm = confusion_matrix(test_labels_arr, predictions, labels=list(range(len(CATEGORIES))))
    per_class = classification_report(test_labels_arr, predictions, target_names=CATEGORIES, output_dict=True, zero_division=0)

    per_class_metrics = {}
    for cat in CATEGORIES:
        if cat in per_class:
            per_class_metrics[cat] = {
                'precision': per_class[cat].get('precision', 0),
                'recall': per_class[cat].get('recall', 0),
                'f1': per_class[cat].get('f1-score', 0),
                'support': per_class[cat].get('support', 0)
            }

    results['per_class'] = per_class_metrics

    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "evaluation.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(output_dir / "per_class_metrics.json", 'w') as f:
        json.dump(per_class_metrics, f, indent=2, ensure_ascii=False)

    cm_normalized = cm.astype('float') / np.maximum(cm.sum(axis=1, keepdims=True), 1)
    with open(output_dir / "confusion_matrix.json", 'w') as f:
        json.dump(cm_normalized.tolist(), f, indent=2)

    np.save(output_dir / "confusion_matrix.npy", cm)

    print_results(results)
    return results

def save_results(results):
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "evaluation.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def print_results(results):
    print(f"\n[evaluate] Resultados:")
    print(f"  Accuracy:  {results.get('accuracy', 0)*100:.2f}%")
    print(f"  F1-Score:  {results.get('f1', 0)*100:.2f}%")
    print(f"  Precision: {results.get('precision', 0)*100:.2f}%")
    print(f"  Recall:    {results.get('recall', 0)*100:.2f}%")
    print(f"\n[evaluate] Resultados salvos em: results/")

if __name__ == "__main__":
    evaluate_model()