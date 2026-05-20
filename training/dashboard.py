import gradio as gr
import json
import os
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"

def load_all_metrics():
    metrics = {
        'global': {'accuracy': 0, 'f1': 0, 'precision': 0, 'recall': 0, 'total_samples': 0},
        'per_fold': [],
        'per_class': {},
        'confusion_matrix': None,
        'folds': []
    }

    if not RESULTS_DIR.exists():
        return metrics

    for fold_dir in sorted(RESULTS_DIR.iterdir()):
        if not fold_dir.is_dir():
            continue

        fold_name = fold_dir.name
        eval_file = fold_dir / "evaluation.json"
        checkpoint_dirs = [d for d in fold_dir.iterdir() if d.is_dir() and d.name.startswith("checkpoint-")]

        if not checkpoint_dirs:
            continue

        best_checkpoint = max(checkpoint_dirs, key=lambda x: int(x.name.split("-")[1]))
        eval_file = best_checkpoint / "evaluation.json"

        if eval_file.exists():
            with open(eval_file) as f:
                fold_data = json.load(f)
                metrics['per_fold'].append({
                    'name': fold_name,
                    'accuracy': fold_data.get('accuracy', 0),
                    'f1': fold_data.get('f1', 0),
                    'precision': fold_data.get('precision', 0),
                    'recall': fold_data.get('recall', 0),
                    'checkpoint': best_checkpoint.name
                })

        trainer_state = best_checkpoint / "trainer_state.json"
        if trainer_state.exists():
            with open(trainer_state) as f:
                state = json.load(f)
                metrics['folds'].append({
                    'name': fold_name,
                    'epochs': len(state.get('log_history', [])),
                    'best_step': state.get('best_model_checkpoint', 'N/A')
                })

        confusion_file = fold_dir / "confusion_matrix.json"
        if confusion_file.exists():
            with open(confusion_file) as f:
                metrics['confusion_matrix'] = json.load(f)

    if metrics['per_fold']:
        n = len(metrics['per_fold'])
        metrics['global'] = {
            'accuracy': np.mean([f['accuracy'] for f in metrics['per_fold']]),
            'f1': np.mean([f['f1'] for f in metrics['per_fold']]),
            'precision': np.mean([f['precision'] for f in metrics['per_fold']]),
            'recall': np.mean([f['recall'] for f in metrics['per_fold']]),
            'total_samples': sum(f.get('total_samples', 0) for f in metrics['per_fold']),
            'std_accuracy': np.std([f['accuracy'] for f in metrics['per_fold']]),
            'std_f1': np.std([f['f1'] for f in metrics['per_fold']])
        }

    class_metrics_file = RESULTS_DIR / "per_class_metrics.json"
    if class_metrics_file.exists():
        with open(class_metrics_file) as f:
            metrics['per_class'] = json.load(f)

    return metrics

def create_dashboard():
    metrics = load_all_metrics()

    with gr.Blocks(title="Dashboard de Métricas - Ouvidoria AI", theme=gr.themes.Soft()) as dashboard:
        gr.Markdown("# Dashboard de Métricas - Ouvidoria Triagem Municipal")
        gr.Markdown("### Modelo: BERTimbau Fine-tuned para Classificação de Reclamações")

        with gr.Tabs():
            with gr.TabItem("Resumo Geral"):
                gr.Markdown("## Métricas Globais (Média entre Folds)")

                with gr.Row():
                    accuracy_gauge = gr.Number(label="Accuracy (%)", value=round(metrics['global']['accuracy'] * 100, 2))
                    f1_gauge = gr.Number(label="F1-Score (%)", value=round(metrics['global']['f1'] * 100, 2))
                    precision_gauge = gr.Number(label="Precision (%)", value=round(metrics['global']['precision'] * 100, 2))
                    recall_gauge = gr.Number(label="Recall (%)", value=round(metrics['global']['recall'] * 100, 2))

                gr.Markdown(f"**Total de Amostras:** {metrics['global']['total_samples']}")

                if 'std_accuracy' in metrics['global']:
                    gr.Markdown(f"**Desvio Padrão Accuracy:** ±{round(metrics['global']['std_accuracy'] * 100, 2)}%")
                    gr.Markdown(f"**Desvio Padrão F1:** ±{round(metrics['global']['std_f1'] * 100, 2)}%")

            with gr.TabItem("Por Fold"):
                gr.Markdown("## Métricas por Fold (K-Fold Cross-Validation)")

                if metrics['per_fold']:
                    fold_data = []
                    for fold in metrics['per_fold']:
                        fold_data.append([
                            fold['name'],
                            f"{fold['accuracy']*100:.2f}%",
                            f"{fold['f1']*100:.2f}%",
                            f"{fold['precision']*100:.2f}%",
                            f"{fold['recall']*100:.2f}%",
                            fold.get('checkpoint', 'N/A')
                        ])

                    fold_table = gr.DataFrame(
                        headers=["Fold", "Accuracy", "F1-Score", "Precision", "Recall", "Checkpoint"],
                        value=fold_data if fold_data else [[]],
                        label="Resultados por Fold"
                    )
                else:
                    gr.Markdown("Nenhum resultado encontrado. Execute o treinamento primeiro.")

                if metrics['folds']:
                    gr.Markdown("### Detalhes dos Folds")
                    for fold_info in metrics['folds']:
                        gr.Markdown(f"**{fold_info['name']}** - Epochs: {fold_info['epochs']}, Best Step: {fold_info['best_step']}")

            with gr.TabItem("Por Classe"):
                gr.Markdown("## Métricas por Classe (Categoria)")

                categories = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']

                if metrics['per_class']:
                    class_data = []
                    for cat in categories:
                        if cat in metrics['per_class']:
                            m = metrics['per_class'][cat]
                            class_data.append([
                                cat,
                                f"{m.get('f1', 0)*100:.2f}%" if m.get('f1') else "N/A",
                                f"{m.get('precision', 0)*100:.2f}%" if m.get('precision') else "N/A",
                                f"{m.get('recall', 0)*100:.2f}%" if m.get('recall') else "N/A",
                                m.get('support', 0)
                            ])
                        else:
                            class_data.append([cat, "N/A", "N/A", "N/A", 0])

                    class_table = gr.DataFrame(
                        headers=["Categoria", "F1-Score", "Precision", "Recall", "Support"],
                        value=class_data if class_data else [[]],
                        label="Métricas por Classe"
                    )
                else:
                    gr.Markdown("Nenhuma métrica por classe disponível.")

            with gr.TabItem("Matriz de Confusão"):
                gr.Markdown("## Matriz de Confusão")

                categories = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']

                if metrics['confusion_matrix']:
                    confusion = metrics['confusion_matrix']
                    gr.Markdown("### Matriz de Confusão Normalizada")

                    confusion_display = []
                    for i, cat_true in enumerate(categories):
                        row = [cat_true]
                        for j, cat_pred in enumerate(categories):
                            if i < len(confusion) and j < len(confusion[i]):
                                row.append(f"{confusion[i][j]:.2f}")
                            else:
                                row.append("0.00")
                        confusion_display.append(row)

                    headers = ["True \\ Pred"] + categories
                    confusion_table = gr.DataFrame(
                        headers=headers,
                        value=confusion_display if confusion_display else [[]],
                        label="Matriz de Confusão"
                    )
                else:
                    gr.Markdown("Nenhuma matriz de confusão disponível.")

        gr.Markdown("---")
        gr.Markdown("*Dashboard gerado automaticamente - Atualize a página para ver novos resultados*")

        refresh_btn = gr.Button("Atualizar Métricas")
        refresh_btn.click(fn=load_all_metrics, outputs=[
            accuracy_gauge, f1_gauge, precision_gauge, recall_gauge
        ])

    return dashboard

if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(server_name="0.0.0.0", server_port=7860, share=False)