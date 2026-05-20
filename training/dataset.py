import random
import json
from pathlib import Path
from config import TRAINING_CONFIG, CATEGORIES

def augment_data(data, target_size=None):
    if not data:
        return data

    if target_size is None:
        target_size = len(data) * 10

    augmented = []
    templates = {
        'Infraestrutura': [
            "Problema de infraestrutura: {text}",
            "Solicito reparo: {text}",
            "Denúncia sobre infraestrutura: {text}",
            "Há um problema de infraestrutura em: {text}",
        ],
        'Saúde': [
            "Problema na área de saúde: {text}",
            "Solicito atenção da saúde: {text}",
            "Denúncia de saúde: {text}",
            "Na área da saúde: {text}",
        ],
        'Trânsito': [
            "Problema de trânsito: {text}",
            "Solicito intervenção no trânsito: {text}",
            "Denúncia de trânsito: {text}",
            "No trânsito: {text}",
        ],
        'Iluminação': [
            "Problema de iluminação: {text}",
            "Solicito reparo na iluminação: {text}",
            "Denúncia de iluminação: {text}",
            "Sobre iluminação: {text}",
        ],
        'Outros': [
            "Manifestação: {text}",
            "Solicito informações: {text}",
            "Denúncia: {text}",
            "Reclamação: {text}",
        ]
    }

    for item in data:
        augmented.append(item)

        text = item['text']
        label = item.get('categoria', CATEGORIES[item['label']])

        for _ in range(3):
            template = random.choice(templates.get(label, templates['Outros']))
            new_text = template.format(text=text.lower())
            augmented.append({
                'text': new_text,
                'label': item['label'],
                'categoria': label
            })

        words = text.lower().split()
        if len(words) > 5:
            shortened = ' '.join(random.sample(words, min(len(words)-2, len(words))))
            augmented.append({
                'text': shortened + "...",
                'label': item['label'],
                'categoria': label
            })

        words_upper = ' '.join([w.upper() if random.random() > 0.5 else w for w in text.split()])
        augmented.append({
            'text': words_upper,
            'label': item['label'],
            'categoria': label
        })

    random.shuffle(augmented)

    if target_size and len(augmented) < target_size:
        repeat_factor = (target_size // len(augmented)) + 1
        augmented = augmented * repeat_factor
        random.shuffle(augmented)

    return augmented[:target_size] if target_size else augmented

def prepare_dataset():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    processed_file = data_dir / "processed_ouvidoria.json"

    if processed_file.exists():
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[dataset] Dataset carregado: {len(data)} amostras")

            max_samples = TRAINING_CONFIG.get('max_samples', 200)
            if len(data) > max_samples:
                data = data[:max_samples]
                print(f"[dataset] Limitado a {max_samples} amostras")

            return data

    from .download_dataset import download_dataset
    result = download_dataset()

    if result and Path(result).exists():
        with open(result, 'r', encoding='utf-8') as f:
            data = json.load(f)

            max_samples = TRAINING_CONFIG.get('max_samples', 200)
            if len(data) > max_samples:
                data = data[:max_samples]
                print(f"[dataset] Limitado a {max_samples} amostras")

            return data

    return generate_synthetic_data()

def generate_synthetic_data():
    print("[dataset] Gerando dados sintéticos...")

    examples = [
        ("Buraco enorme na Av. Principal perto do posto de saúde municipal", 0, "Infraestrutura"),
        ("Calçada quebrada na frente da escola José de Alencar", 0, "Infraestrutura"),
        ("Falta de água no bairro Vila Nova há 3 dias", 0, "Infraestrutura"),
        ("Rua com buracos enormes na região central", 0, "Infraestrutura"),
        ("Ponte com rachaduras na estrada vicinal", 0, "Infraestrutura"),
        ("Bueiro entupido na rua das flores causando alagamento", 0, "Infraestrutura"),
        ("Poste de luz quebrado na entrada do bairro", 0, "Infraestrutura"),
        ("Asfalto deteriorado na estrada do aeropuerto", 0, "Infraestrutura"),
        ("Guia quebrada na calçada da rua commerciantes", 0, "Infraestrutura"),
        ("Esgoto a céu aberto na vizinhança", 0, "Infraestrutura"),

        ("Falta dipirona no posto de saúde do bairro centro", 1, "Saúde"),
        ("Médico Dr. João não apareceu na UBS Santa Maria", 1, "Saúde"),
        ("Farmácia do posto sem medicamentos há semanas", 1, "Saúde"),
        ("Enfermeira Maria não atende no posto do bairro", 1, "Saúde"),
        ("Hospital sem insumos para emergência", 1, "Saúde"),
        ("Ambulância quebrada no garage municipal", 1, "Saúde"),
        ("Falta soro no hospital regional", 1, "Saúde"),
        ("Médico ausentou-se do plantão noturno", 1, "Saúde"),
        ("UBS sem atendimento médico hoje", 1, "Saúde"),
        ("Posto de saúde com filas enormes", 1, "Saúde"),

        ("Semáforo quebrado na esquina da rua 7 com a 15", 2, "Trânsito"),
        ("Ônibus 302 não passa há dois dias no meu bairro", 2, "Trânsito"),
        ("Ponto de ônibus sem banco para esperar", 2, "Trânsito"),
        ("Placa de trânsito arrancada na estrada", 2, "Trânsito"),
        ("Semáforo piscando amarelo na av. brasil", 2, "Trânsito"),
        ("Radar com defeito na via expressa", 2, "Trânsito"),
        ("Lombada desgastada na rua escolar", 2, "Trânsito"),
        ("Sinalização de obra abandonada na via", 2, "Trânsito"),
        ("Faixa de pedestre apagada na frente da escola", 2, "Trânsito"),
        ("Ponto de ônibus destruído por vândalos", 2, "Trânsito"),

        ("Poste apagado há três noites na rua das flores", 3, "Iluminação"),
        ("Toda a praça central está sem luz", 3, "Iluminação"),
        ("Lâmpada do poste queimada há dias", 3, "Iluminação"),
        ("Iluminação pública quebrada na entrada do parque", 3, "Iluminação"),
        ("Refletor do campo de futebol queimado", 3, "Iluminação"),
        ("Postes sem luz na entrada da escola", 3, "Iluminação"),
        ("Réveillon sem iluminação na praça", 3, "Iluminação"),
        ("Lâmpada da rua piscando constantemente", 3, "Iluminação"),

        ("Elogio ao atendimento do servidor Pedro da ouvidoria", 4, "Outros"),
        ("Informação sobre alvará de funcionamento", 4, "Outros"),
        ("Denúncia sobre irregularidades na administração", 4, "Outros"),
        ("Solicito documentação sobre obras", 4, "Outros"),
        ("Horário de funcionamento da prefeitura", 4, "Outros"),
        ("Reclamação sobre atendimento no setor", 4, "Outros"),
        ("Solicito informações sobre IPTU", 4, "Outros"),
        ("Denúncia de descarte irregular de lixo", 4, "Outros"),
        ("Reclamação sobre barulho de construção", 4, "Outros"),
        ("Solicito poda de árvore na calçada", 4, "Outros"),
    ]

    data = []
    for text, label, categoria in examples:
        for _ in range(5):
            data.append({
                'text': text,
                'label': label,
                'categoria': categoria
            })

    print(f"[dataset] Dados sintéticos gerados: {len(data)} amostras")
    return data

def load_train_test_split(test_size=0.2, random_state=42):
    import random
    random.seed(random_state)

    data = prepare_dataset()

    if not data:
        return [], [], []

    random.shuffle(data)

    split_idx = int(len(data) * (1 - test_size))
    train_data = data[:split_idx]
    test_data = data[split_idx:]

    return train_data, test_data, data

if __name__ == "__main__":
    data = prepare_dataset()
    print(f"\n[dataset] Total: {len(data)} amostras")

    if data:
        categories = {}
        for item in data:
            cat = item.get('categoria', CATEGORIES[item['label']])
            categories[cat] = categories.get(cat, 0) + 1

        print("\nDistribuição:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")