import json
import os
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from .model import get_device
from .dataset import prepare_dataset
from .config import CATEGORIES

def evaluate_model(model_path=None, from_hub=False, hub_model_id=None):
    print("[evaluate] Iniciando avaliação...")

    data = prepare_dataset()
    test_texts = [item['text'] for item in data]
    test_labels = [item['label'] for item in data]

    device = get_device()

    if from_hub and hub_model_id:
        print(f"[evaluate] Carregando do HuggingFace Hub: {hub_model_id}")
        tokenizer = AutoTokenizer.from_pretrained(hub_model_id)
        model = AutoModelForSequenceClassification.from_pretrained(hub_model_id)
    elif model_path:
        print(f"[evaluate] Carregando modelo local: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
    else:
        print("[evaluate] Nenhum modelo especificado para avaliação")
        return None

    model.to(device)
    model.eval()

    predictions = []
    confidences = []

    for text in test_texts:
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            pred = torch.argmax(probs, dim=-1).item()
            conf = probs[0][pred].item()

        predictions.append(pred)
        confidences.append(conf)

    predictions = np.array(predictions)
    test_labels = np.array(test_labels)

    acc = accuracy_score(test_labels, predictions)
    f1 = f1_score(test_labels, predictions, average='weighted')
    prec = precision_score(test_labels, predictions, average='weighted', zero_division=0)
    rec = recall_score(test_labels, predictions, average='weighted', zero_division=0)

    cm = confusion_matrix(test_labels, predictions, labels=list(range(len(CATEGORIES))))

    per_class = classification_report(test_labels, predictions, target_names=CATEGORIES, output_dict=True, zero_division=0)

    per_class_metrics = {}
    for cat in CATEGORIES:
        if cat in per_class:
            per_class_metrics[cat] = {
                'precision': per_class[cat].get('precision', 0),
                'recall': per_class[cat].get('recall', 0),
                'f1': per_class[cat].get('f1-score', 0),
                'support': per_class[cat].get('support', 0)
            }

    results = {
        'accuracy': float(acc),
        'f1': float(f1),
        'precision': float(prec),
        'recall': float(rec),
        'per_class': per_class_metrics,
        'total_samples': len(test_labels)
    }

    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "evaluation.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(output_dir / "classification_report.txt", 'w') as f:
        f.write(classification_report(test_labels, predictions, target_names=CATEGORIES))

    cm_normalized = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    with open(output_dir / "confusion_matrix.json", 'w') as f:
        json.dump(cm_normalized.tolist(), f, indent=2)

    np.save(output_dir / "confusion_matrix.npy", cm)

    with open(output_dir / "per_class_metrics.json", 'w') as f:
        json.dump(per_class_metrics, f, indent=2, ensure_ascii=False)

    print("\n[evaluate] Resultados da Avaliação:")
    print(f"  Accuracy:  {acc*100:.2f}%")
    print(f"  F1-Score:  {f1*100:.2f}%")
    print(f"  Precision: {prec*100:.2f}%")
    print(f"  Recall:    {rec*100:.2f}%")

    print("\n[evaluate] Relatório por Classe:")
    print(classification_report(test_labels, predictions, target_names=CATEGORIES))

    return results

if __name__ == "__main__":
    import torch
    evaluate_model()