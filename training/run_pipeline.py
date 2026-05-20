import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from download_dataset import download_dataset
from dataset import prepare_dataset
from trainer import run_training
from evaluate_model import evaluate_model
from dashboard import create_dashboard
import argparse

def main():
    parser = argparse.ArgumentParser(description='Pipeline de Treinamento - Ouvidoria AI')
    parser.add_argument('--step', choices=['all', 'download', 'dataset', 'train', 'evaluate', 'dashboard'],
                        default='all', help='Qual passo executar')
    parser.add_argument('--model-path', type=str, help='Caminho para modelo treinado (avaliação)')
    parser.add_argument('--no-launch', action='store_true', help='Não abrir dashboard automaticamente')

    args = parser.parse_args()

    print("=" * 60)
    print("PIPELINE DE TREINAMENTO - OUVIDORIA TRIAGEM MUNICIPAL")
    print("=" * 60)

    if args.step in ['all', 'download']:
        print("\n📥 [PASSO 1] Baixando dataset...")
        result = download_dataset()
        if result:
            print(f"✓ Dataset salvo em: {result}")
        else:
            print("⚠️ Falha no download, usando dados sintéticos")
        print("-" * 40)

    if args.step in ['all', 'dataset']:
        print("\n📊 [PASSO 2] Preparando dataset...")
        data = prepare_dataset()
        print(f"✓ Dataset preparado: {len(data)} amostras")
        print("-" * 40)

    if args.step in ['all', 'train']:
        print("\n🏋️ [PASSO 3] Treinando modelo (K-Fold)...")
        print("⚠️ Este processo pode levar muito tempo em CPU")
        results = run_training()
        print(f"✓ Treinamento concluído: {len(results)} folds")
        print("-" * 40)

    if args.step in ['all', 'evaluate']:
        print("\n📈 [PASSO 4] Avaliando modelo...")
        if args.model_path:
            eval_results = evaluate_model(model_path=args.model_path)
        else:
            model_path = Path(__file__).parent.parent / "models" / "checkpoints" / "fold_0"
            if model_path.exists():
                eval_results = evaluate_model(model_path=str(model_path))
            else:
                print("⚠️ Nenhum modelo encontrado. Pulando avaliação.")
                eval_results = None

        if eval_results:
            print(f"✓ Accuracy: {eval_results['accuracy']*100:.2f}%")
            print(f"✓ F1-Score: {eval_results['f1']*100:.2f}%")
        print("-" * 40)

    if args.step in ['all', 'dashboard']:
        print("\n📊 [PASSO 5] Abrindo dashboard...")
        if args.no_launch:
            print("✓ Dashboard configurado (não aberto automaticamente)")
        else:
            print("✓ Abrindo dashboard em http://localhost:7860")
            dashboard = create_dashboard()
            dashboard.launch(
                server_name="0.0.0.0",
                server_port=7860,
                share=False,
                inbrowser=True
            )

    print("\n" + "=" * 60)
    print("PIPELINE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    main()