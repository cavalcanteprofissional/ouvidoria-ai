import os
from dotenv import load_dotenv
from pathlib import Path
from huggingface_hub import HfApi, login

load_dotenv('.env.local')

HF_TOKEN = os.getenv('HF_TOKEN')

def upload_model_to_hub(model_path, repo_id="cavalcanteprofissional/ouvidoria-ai"):
    if not HF_TOKEN:
        print("[upload] HF_TOKEN não encontrado no .env.local")
        return False

    print(f"[upload] Fazendo login no HuggingFace Hub...")
    login(token=HF_TOKEN)

    api = HfApi()

    print(f"[upload] Carregando modelo de: {model_path}")
    api.upload_folder(
        folder_path=model_path,
        repo_id=repo_id,
        repo_type="model",
        commit_message="Upload modelo fine-tuned - Ouvidoria Triagem"
    )

    print(f"[upload] Modelo enviado com sucesso para: https://huggingface.co/{repo_id}")
    return True

def upload_results_to_hub():
    if not HF_TOKEN:
        print("[upload] HF_TOKEN não encontrado")
        return False

    print("[upload] Enviando resultados para HuggingFace...")
    login(token=HF_TOKEN)

    api = HfApi()
    results_dir = Path(__file__).parent.parent / "results"

    if results_dir.exists():
        for file in results_dir.glob("*.json"):
            print(f"  [upload] {file.name}")

    print("[upload] Resultados salvos localmente")

def create_spaces_app():
    spaces_dir = Path(__file__).parent.parent / "hf_spaces_app"
    spaces_dir.mkdir(exist_ok=True)

    app_code = '''import gradio as gr
import requests
import json

API_URL = "https://api.ouvidoria-municipal.com"

def classify_text(text):
    try:
        response = requests.post(
            f"{API_URL}/api/triagem",
            json={"texto": text},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return (
                f"**Categoria:** {data['categoria']} (confiança: {data['confianca']*100:.0f}%)\\n"
                f"**Secretaria:** {data['secretaria_sugerida']}\\n"
                f"**Urgência:** {data['entidades']['urgencia']}\\n"
                f"**Localização:** {', '.join(data['entidades']['localizacao']) or 'Não identificada'}"
            )
        else:
            return f"Erro: {response.status_code}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

demo = gr.Interface(
    fn=classify_text,
    inputs=gr.Textbox(label="Descreva seu problema", placeholder="Ex: Tem um buraco na Av. Principal..."),
    outputs=gr.Markdown(),
    title="Ouvidoria Municipal - Triagem Automática",
    description="Sistema de classificação automática de reclamações usando IA",
    examples=[
        ["Buraco enorme na Av. Principal perto do posto de saúde"],
        ["Semáforo quebrado na esquina da rua 7"],
        ["Poste apagado há 3 dias na rua das Flores"],
        ["Falta dipirona no posto de saúde do bairro"],
    ]
)

if __name__ == "__main__":
    demo.launch()
'''

    with open(spaces_dir / "app.py", 'w') as f:
        f.write(app_code)

    requirements = '''gradio>=4.0.0
requests>=2.28.0
'''

    with open(spaces_dir / "requirements.txt", 'w') as f:
        f.write(requirements)

    print(f"[spaces] App criado em: {spaces_dir}")
    print("[spaces] Para deploy: https://huggingface.co/new-space")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        upload_model_to_hub(sys.argv[1])
    else:
        create_spaces_app()