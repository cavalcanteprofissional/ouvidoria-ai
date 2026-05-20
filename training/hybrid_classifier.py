import os
import json
import requests
from .config import HF_SPACES_URL, CATEGORIES

def classify_hf_spaces(text, api_key=None):
    try:
        response = requests.post(
            f"{HF_SPACES_URL}/predict",
            json={"text": text},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'categoria': data.get('categoria', 'Outros'),
                'confianca': float(data.get('confidence', 0.5)),
                'source': 'hf_spaces'
            }
    except Exception as e:
        print(f"[HF Spaces] Erro: {e}")
    return None

def classify_local(text, model, tokenizer, device):
    try:
        import torch
        from transformers import pipeline

        classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device,
            top_k=None
        )

        results = classifier(text, truncation=True, max_length=512)

        if results and len(results) > 0:
            top = max(results[0], key=lambda x: x['score'])
            label_idx = int(top['label'].split('_')[-1])
            categoria = CATEGORIES[label_idx] if label_idx < len(CATEGORIES) else 'Outros'

            return {
                'categoria': categoria,
                'confianca': float(top['score']),
                'source': 'local'
            }
    except Exception as e:
        print(f"[Local Model] Erro: {e}")
    return None

def classify_cohere(text, api_key):
    try:
        from cohere import CohereClient

        cohere = CohereClient(token=api_key)

        EXAMPLES = [
            {"text": "Tem um buraco gigante na avenida principal", "label": "Infraestrutura"},
            {"text": "Calçada quebrada na frente da escola municipal", "label": "Infraestrutura"},
            {"text": "Falta dipirona no posto de saúde do bairro", "label": "Saúde"},
            {"text": "Médico não apareceu na UBS hoje de manhã", "label": "Saúde"},
            {"text": "Semáforo quebrado na esquina da rua 7 com a 15", "label": "Trânsito"},
            {"text": "Ônibus 302 não passa há dois dias no meu bairro", "label": "Trânsito"},
            {"text": "Poste apagado há três noites na rua das flores", "label": "Iluminação"},
            {"text": "Toda a praça central está sem luz", "label": "Iluminação"},
            {"text": "Quero elogiar o atendimento do servidor João", "label": "Outros"},
            {"text": "Preciso de informação sobre alvará de funcionamento", "label": "Outros"}
        ]

        res = cohere.classify(inputs=[text], examples=EXAMPLES)
        result = res.classifications[0]

        return {
            'categoria': result.prediction,
            'confianca': float(result.confidence),
            'source': 'cohere'
        }
    except Exception as e:
        print(f"[Cohere] Erro: {e}")
    return None

def classify_hybrid(text, cohere_api_key=None, model=None, tokenizer=None, device=-1):
    sources_tried = []
    result = classify_hf_spaces(text)
    if result:
        return result
    sources_tried.append('hf_spaces')

    if model and tokenizer:
        result = classify_local(text, model, tokenizer, device)
        if result:
            return result
        sources_tried.append('local')

    if cohere_api_key:
        result = classify_cohere(text, cohere_api_key)
        if result:
            return result
        sources_tried.append('cohere')

    return {
        'categoria': 'Outros',
        'confianca': 0.0,
        'source': 'none',
        'sources_tried': sources_tried
    }