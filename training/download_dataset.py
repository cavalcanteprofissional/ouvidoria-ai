import os
import json
import kaggle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

KAGGLE_KEY = os.getenv('KAGGLE_KEY')
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME', 'cavalcanteprofissional')

def download_dataset():
    dataset_path = Path(__file__).parent.parent / "data" / "raw"
    dataset_path.mkdir(parents=True, exist_ok=True)

    print(f"[download] KAGGLE_KEY: {'*' * len(KAGGLE_KEY) if KAGGLE_KEY else 'NOT SET'}")
    print(f"[download] KAGGLE_USERNAME: {KAGGLE_USERNAME}")

    if KAGGLE_KEY:
        os.environ['KAGGLE_KEY'] = KAGGLE_KEY
        os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()

            dataset_slug = 'nickpro/ouvidoria-setor-categoria'
            print(f"[download] Baixando do Kaggle: {dataset_slug}")

            api.dataset_download_files(
                dataset_slug,
                path=str(dataset_path),
                unzip=True,
                quiet=False
            )

            print("[download] ✓ Dataset baixado do Kaggle!")

            csv_files = list(dataset_path.glob("*.csv"))
            if csv_files:
                return process_dataset(csv_files[0])

        except Exception as e:
            print(f"[download] Erro Kaggle: {e}")
            print("[download] Tentando fonte alternativa...")

    return download_from_huggingface()

def download_from_huggingface():
    print("[download] Baixando do HuggingFace...")

    try:
        from datasets import load_dataset

        dataset_path = Path(__file__).parent.parent / "data" / "raw"
        dataset_path.mkdir(parents=True, exist_ok=True)

        print("[download] Carregando dataset 'nickpro/ouvidoria_setor_categoria'...")
        ds = load_dataset("nickpro/ouvidoria_setor_categoria")

        for split_name, split_data in ds.items():
            csv_file = dataset_path / f"ouvidoria_{split_name}.csv"
            split_data.to_csv(csv_file)
            print(f"[download] Salvo: {csv_file}")

        if 'train' in ds:
            train_file = dataset_path / "ouvidoria.csv"
            ds['train'].to_csv(train_file)
            print(f"[download] Dataset principal salvo: {train_file}")
            return process_dataset(train_file)

        return str(dataset_path / "ouvidoria_train.csv")

    except Exception as e:
        print(f"[download] Erro HuggingFace: {e}")

    return download_synthetic()

def download_synthetic():
    print("[download] Gerando dados sintéticos para teste...")

    data = [
        {"texto": "Tem um buraco enorme na Av. Principal, perto do posto de saúde municipal, já faz 3 dias", "categoria": "Infraestrutura"},
        {"texto": "Calçada quebrada na frente da escola José de Alencar, risco para crianças", "categoria": "Infraestrutura"},
        {"texto": "Falta de água no bairro Vila Nova há 3 dias, situação crítica", "categoria": "Infraestrutura"},
        {"texto": "Rua com buracos enormes na região central, varios carros prejudicados", "categoria": "Infraestrutura"},
        {"texto": "Ponte com rachaduras na estrada vicinal, muito perigoso", "categoria": "Infraestrutura"},
        {"texto": "Bueiro entupido na rua das flores, alagamento constante", "categoria": "Infraestrutura"},
        {"texto": "Falta dipirona e paracetamol no posto de saúde do bairro centro", "categoria": "Saúde"},
        {"texto": "Médico Dr. João não apareceu na UBS Santa Maria hoje de manhã", "categoria": "Saúde"},
        {"texto": "Farmácia do posto está sem medicamentos há semanas", "categoria": "Saúde"},
        {"texto": "Enfermeira Maria não atende no posto do bairro progressista", "categoria": "Saúde"},
        {"texto": "Hospital municipal sem insumos básicos para emergência", "categoria": "Saúde"},
        {"texto": "Semáforo quebrado na esquina da rua 7 com a rua 15, perigoso", "categoria": "Trânsito"},
        {"texto": "Ônibus 302 não passa há dois dias no meu bairro, sem informação", "categoria": "Trânsito"},
        {"texto": "Ponto de ônibus quebrado na Av. Brasil, sem banco para esperar", "categoria": "Trânsito"},
        {"texto": "Placa de trânsito arrancada na estrada do bairro industrial", "categoria": "Trânsito"},
        {"texto": "Radar quebrado na avança principal há semanas", "categoria": "Trânsito"},
        {"texto": "Poste apagado há três noites na rua das flores, escuridão total", "categoria": "Iluminação"},
        {"texto": "Toda a praça central está sem luz, inseguro à noite", "categoria": "Iluminação"},
        {"texto": "Lâmpada do poste em frente ao número 45 está queimada há dias", "categoria": "Iluminação"},
        {"texto": "Iluminação pública quebrada na entrada do parque municipal", "categoria": "Iluminação"},
        {"texto": "Quero elogiar o atendimento do servidor Pedro da ouvidoria", "categoria": "Outros"},
        {"texto": "Preciso de informação sobre como tirar alvará de funcionamento", "categoria": "Outros"},
        {"texto": "Denúncia sobre irregularidades na administração pública", "categoria": "Outros"},
        {"texto": "Solicito documentação sobre obras na rua principal", "categoria": "Outros"},
        {"texto": "Gostaria de saber sobre horário de funcionamento da prefeitura", "categoria": "Outros"},
    ]

    import pandas as pd
    dataset_path = Path(__file__).parent.parent / "data" / "raw"
    dataset_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(data)
    csv_file = dataset_path / "ouvidoria.csv"
    df.to_csv(csv_file, index=False)

    print(f"[download] Dados sintéticos salvos: {csv_file}")
    return process_dataset(csv_file)

def process_dataset(csv_path):
    import pandas as pd

    print(f"[process] Processando {csv_path}...")

    if not Path(csv_path).exists():
        print(f"[process] Arquivo não encontrado: {csv_path}")
        return None

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[process] Erro ao ler CSV: {e}")
        return None

    print(f"[process] Colunas: {df.columns.tolist()}")
    print(f"[process] Total de linhas: {len(df)}")

    text_col = None
    for col in ['texto', 'text', 'description', 'content', 'reclamacao']:
        if col in df.columns:
            text_col = col
            break

    if not text_col:
        print("[process] Nenhuma coluna de texto encontrada")
        return None

    cat_col = None
    for col in ['categoria', 'category', 'label', 'setor']:
        if col in df.columns:
            cat_col = col
            break

    categories = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']
    category_map = {
        'Infraestrutura': 'Infraestrutura',
        'Saúde': 'Saúde',
        'Trânsito': 'Trânsito',
        'Iluminação': 'Iluminação',
        'Outros': 'Outros',
        'Crash': 'Infraestrutura', 'Bug': 'Infraestrutura', 'Technical': 'Infraestrutura', 'Hardware': 'Infraestrutura',
        'Maintenance': 'Saúde', 'Security': 'Saúde', 'Breach': 'Saúde',
        'Performance': 'Trânsito', 'Incident': 'Trânsito',
        'Documentation': 'Iluminação', 'Feedback': 'Iluminação',
        'Resolution': 'Outros', 'Feature': 'Outros', 'Sales': 'Outros', 'Product': 'Outros'
    }

    processed = []
    for _, row in df.iterrows():
        text = str(row[text_col])
        categoria = str(row.get(cat_col, 'Outros')) if cat_col else 'Outros'

        if categoria not in categories:
            categoria = category_map.get(categoria, 'Outros')

        if len(text) > 10:
            processed.append({
                'text': text,
                'label': categories.index(categoria),
                'categoria': categoria
            })

    output_path = csv_path.parent / "processed_ouvidoria.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print(f"[process] ✓ Processado: {len(processed)} amostras")
    print(f"[process] Salvo em: {output_path}")

    category_counts = {}
    for item in processed:
        cat = item['categoria']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("[process] Distribuição por categoria:")
    for cat, count in category_counts.items():
        print(f"  {cat}: {count}")

    return str(output_path)

if __name__ == "__main__":
    result = download_dataset()
    print(f"\n[done] Dataset disponível em: {result}")