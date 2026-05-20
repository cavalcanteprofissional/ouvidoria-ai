import json
import random
from pathlib import Path
from .config import CATEGORIES, CATEGORY_MAPPING

def prepare_dataset(raw_data=None):
    if raw_data is None:
        from .download_dataset import load_dataset
        raw_data = load_dataset()

    if not raw_data:
        print("[dataset] Usando dados sintéticos para teste...")
        return generate_synthetic_data()

    processed = []
    for item in raw_data:
        text = item.get('texto', item.get('text', item.get('description', '')))
        categoria = item.get('categoria', item.get('category', item.get('label', 'Outros')))

        if categoria not in CATEGORIES:
            mapped = CATEGORY_MAPPING.get(categoria, 'Outros')
            if mapped not in CATEGORIES:
                mapped = 'Outros'
        else:
            mapped = categoria

        if text and len(text) > 10:
            processed.append({
                'text': text,
                'label': CATEGORIES.index(mapped)
            })

    return processed

def generate_synthetic_data():
    examples = [
        ("Tem um buraco gigante na avenida principal perto do posto de saúde municipal", 0),
        ("Calçada quebrada na frente da escola José de Alencar, risco para crianças", 0),
        ("Falta de água no bairro Vila Nova há 3 dias, situação crítica", 0),
        ("Rua com buracos enormes na região central, varios carros prejudicados", 0),
        ("Ponte com rachaduras na estrada vicinal, muito perigoso", 0),
        ("Falta dipirona e paracetamol no posto de saúde do bairro centro", 1),
        ("Médico não apareceu na UBS Santa Maria hoje de manhã, consulta cancelada", 1),
        ("Farmácia do posto está sem medicamentos há semanas, sem atendimento", 1),
        ("Enfermeira não atende no posto do bairro progressista, descaso", 1),
        ("Hospital municipal sem insumos básicos para atendimento de emergência", 1),
        ("Semáforo quebrado na esquina da rua 7 com a rua 15, perigoso", 2),
        ("Ônibus 302 não passa há dois dias no meu bairro, sem informação", 2),
        ("Ponto de ônibus quebrado na Av. Brasil, sem banco para esperar", 2),
        (" много транспорта на дороге, muito congestionamento", 2),
        ("Placa de trânsito arrancada na estrada do bairro industrial", 2),
        ("Poste apagado há três noites na rua das flores, escuridão total", 3),
        ("Toda a praça central está sem luz, inseguro à noite", 3),
        ("Lâmpada do poste em frente ao número 45 está queimada há dias", 3),
        ("Iluminação pública quebrada na entrada do parque municipal", 3),
        (" множество фонарей не работает, vários postes sem funcionar", 3),
        ("Quero elogiar o atendimento do servidor João da ouvidoria", 4),
        ("Preciso de informação sobre como tirar alvará de funcionamento", 4),
        ("Denúncia sobre irregularidades na administração pública municipal", 4),
        ("Solicito documentação sobre obras na rua principal do bairro", 4),
        ("Рецепция была отличная, elogio ao atendimento da recepção", 4),
    ]

    random.shuffle(examples)

    processed = []
    for text, label in examples:
        for _ in range(40):
            variations = generate_variations(text)
            for var_text in variations:
                processed.append({
                    'text': var_text,
                    'label': label
                })

    return processed

def generate_variations(text):
    variations = [text]

    words_to_add = [
        "Por favor, ",
        "Venho por meio desta ",
        "Gostaria de registrar ",
        "Venho relatar ",
        "Informo que ",
    ]

    endings = [
        " já faz alguns dias.",
        " situação urgente.",
        " peço providências.",
        " preciso de ajuda.",
        " isso está atrapalhando.",
    ]

    base = text.lower().replace("tem", "existe").replace("falta", "ausência de")
    variations.append(base)

    for prefix in words_to_add[:2]:
        for suffix in endings[:2]:
            variations.append(f"{prefix}{text.lower()}{suffix}")

    return variations[:5]

def split_dataset(data, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    random.shuffle(data)

    total = len(data)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)

    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]

    return train_data, val_data, test_data

if __name__ == "__main__":
    data = prepare_dataset()
    print(f"Dataset preparado: {len(data)} amostras")
    print(f"Exemplo: {data[0] if data else 'Nenhum'}")