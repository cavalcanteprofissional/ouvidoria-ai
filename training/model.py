import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import MODEL_CONFIG

def load_model_and_tokenizer(model_path=None, from_hub=False, hub_model_id=None):
    if from_hub and hub_model_id:
        print(f"[model] Carregando modelo do HuggingFace Hub: {hub_model_id}")
        tokenizer = AutoTokenizer.from_pretrained(hub_model_id)
        model = AutoModelForSequenceClassification.from_pretrained(hub_model_id)
        return model, tokenizer

    if model_path:
        print(f"[model] Carregando modelo local: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        return model, tokenizer

    print(f"[model] Carregando modelo base: {MODEL_CONFIG['name']}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_CONFIG['name'])
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_CONFIG['name'],
        num_labels=MODEL_CONFIG['num_labels']
    )
    return model, tokenizer

def get_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("[device] CUDA disponível - usando GPU")
    else:
        device = torch.device("cpu")
        print("[device] CUDA não disponível - usando CPU")
    return device

if __name__ == "__main__":
    model, tokenizer = load_model_and_tokenizer()
    print(f"Modelo carregado: {model.config.model_type}")
    print(f"Tokenizador: {tokenizer.__class__.__name__}")