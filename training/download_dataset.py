import kaggle
import os
import json
from pathlib import Path
from .config import KAGGLE_KEY, KAGGLE_USERNAME, CATEGORIES, CATEGORY_MAPPING

def download_dataset():
    dataset_path = Path(__file__).parent.parent / "data" / "raw"
    dataset_path.mkdir(parents=True, exist_ok=True)

    print("[download] Baixando dataset do Kaggle...")

    try:
        os.environ['KAGGLE_KEY'] = KAGGLE_KEY
        os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME

        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()

        api.dataset_download_files(
            'nickpro/ouvidoria-setor-categoria',
            path=str(dataset_path),
            unzip=True
        )

        print("[download] Dataset baixado com sucesso!")

        csv_files = list(dataset_path.glob("*.csv"))
        if csv_files:
            return process_dataset(csv_files[0])

        return None

    except Exception as e:
        print(f"[download] Erro ao baixar do Kaggle: {e}")
        return download_from_alternative()

def download_from_alternative():
    print("[download] Tentando fonte alternativa...")

    alternative_url = "https://huggingface.co/datasets/nickpro/ouvidoria_setor_categoria/resolve/main/data.csv"

    try:
        import requests
        dataset_path = Path(__file__).parent.parent / "data" / "raw"
        dataset_path.mkdir(parents=True, exist_ok=True)

        response = requests.get(alternative_url, timeout=60)
        response.raise_for_status()

        file_path = dataset_path / "ouvidoria.csv"
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print("[download] Dataset baixado da alternativa!")
        return process_dataset(file_path)

    except Exception as e:
        print(f"[download] Erro na fonte alternativa: {e}")
        return None

def process_dataset(csv_path):
    import pandas as pd

    print(f"[process] Processando {csv_path}...")

    df = pd.read_csv(csv_path)

    print(f"[process] Colunas disponíveis: {df.columns.tolist()}")
    print(f"[process] Total de linhas: {len(df)}")

    output_path = csv_path.parent / "processed_ouvidoria.json"

    records = df.to_dict('records')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"[process] Dataset processado salvo em {output_path}")
    return str(output_path)

def load_dataset():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    json_file = data_dir / "processed_ouvidoria.json"

    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return download_dataset()

if __name__ == "__main__":
    download_dataset()