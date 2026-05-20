import os
import json
from pathlib import Path
from config import KAGGLE_KEY, KAGGLE_USERNAME
from dotenv import load_dotenv

load_dotenv('.env.local')

def generate_synthetic_data():
    print("[dataset] Gerando dados sintéticos para treinamento...")

    examples = [
        ("Buraco enorme na Av. Principal perto do posto de saúde municipal", 0, "Infraestrutura"),
        ("Calçada quebrada na frente da escola José de Alencar", 0, "Infraestrutura"),
        ("Falta de água no bairro Vila Nova há 3 dias", 0, "Infraestrutura"),
        ("Rua com buracos enormes na região central", 0, "Infraestrutura"),
        ("Ponte com rachaduras na estrada vicinal", 0, "Infraestrutura"),
        ("Bueiro entupido na rua das flores causando alagamento", 0, "Infraestrutura"),
        ("Poste de luz quebrado na entrada do bairro", 0, "Infraestrutura"),
        ("Asfalto deteriorado na estrada do aeroporto", 0, "Infraestrutura"),
        ("Guia quebrada na calçada da rua comerciantes", 0, "Infraestrutura"),
        ("Esgoto a céu aberto na vizinhança", 0, "Infraestrutura"),
        ("Tampa dePVU faltando no meio da rua", 0, "Infraestrutura"),
        ("Muro de arrimo caindo na viela", 0, "Infraestrutura"),

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
        ("Falta vacina no posto de saúde", 1, "Saúde"),
        ("Remédios em falta na farmácia popular", 1, "Saúde"),

        ("Semáforo quebrado na esquina da rua 7 com a 15", 2, "Trânsito"),
        ("Ônibus 302 não passa há dois dias no meu bairro", 2, "Trânsito"),
        ("Ponto de ônibus sem banco para esperar", 2, "Trânsito"),
        ("Placa de trânsito arrancada na estrada", 2, "Trânsito"),
        ("Semáforo piscando amarelo na av. brasil", 2, "Trânsito"),
        ("Radar com defeito na via expressa", 2, "Trânsito"),
        ("Lombada desgastada na rua escolar", 2, "Trânsito"),
        ("Sinalização de obra abandonada na via", 2, "Trânsito"),
        ("Faixa de pedestre apagada na frente da escola", 2, "Trânsito"),
        ("Ponto de ônibus destruído porvândalos", 2, "Trânsito"),
        ("Semáforo sem funcionar no cruzamento", 2, "Trânsito"),
        ("Veículo abandonado na via pública", 2, "Trânsito"),

        ("Poste apagado há três noites na rua das flores", 3, "Iluminação"),
        ("Toda a praça central está sem luz", 3, "Iluminação"),
        ("Lâmpada do poste queimada há dias", 3, "Iluminação"),
        ("Iluminação pública quebrada na entrada do parque", 3, "Iluminação"),
        ("Refletor do campo de futebol queimado", 3, "Iluminação"),
        ("Postes sem luz na entrada da escola", 3, "Iluminação"),
        ("Iluminação da praça não funciona à noite", 3, "Iluminação"),
        ("Lâmpada da rua piscando constantemente", 3, "Iluminação"),
        ("Poste com luz queimada no bairro inteiro", 3, "Iluminação"),
        ("Iluminação do mercado público desligada", 3, "Iluminação"),
        ("Túnel sem iluminação adequado", 3, "Iluminação"),

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
        ("Pedido de informação sobre coleta de lixo", 4, "Outros"),
        ("Denúncia de maus-tratos a animais", 4, "Outros"),
    ]

    data = []
    for text, label, categoria in examples:
        for _ in range(4):
            data.append({
                'text': text,
                'label': label,
                'categoria': categoria
            })

    return data

def process_dataset(data):
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "processed_ouvidoria.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[dataset] Dataset salvo: {len(data)} amostras")
    print(f"[dataset] Arquivo: {output_path}")

    category_counts = {}
    for item in data:
        cat = item['categoria']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("[dataset] Distribuicao por categoria:")
    for cat, count in category_counts.items():
        print(f"  {cat}: {count}")

    return str(output_path)

def download_dataset():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    processed_file = data_dir / "processed_ouvidoria.json"

    if processed_file.exists():
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if len(data) >= 100:
                print(f"[dataset] Dataset ja existe: {len(data)} amostras")
                return str(processed_file)

    print("[download] Gerando dados sintéticos...")
    data = generate_synthetic_data()
    return process_dataset(data)

if __name__ == "__main__":
    result = download_dataset()
    print(f"\n[dataset] Pronto: {result}")