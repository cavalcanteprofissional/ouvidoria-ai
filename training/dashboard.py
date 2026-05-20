import os
import json
import gradio as gr
import numpy as np
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"

def load_all_metrics():
    metrics = {
        'global': {
            'accuracy': 0.0, 'f1': 0.0, 'precision': 0.0, 'recall': 0.0,
            'total_samples': 0, 'std_accuracy': 0.0, 'std_f1': 0.0
        },
        'per_fold': [],
        'per_class': {},
        'confusion_matrix': None,
        'folds': [],
        'last_updated': None
    }

    if not RESULTS_DIR.exists():
        metrics['last_updated'] = 'Nunca'
        return metrics

    evaluation_file = RESULTS_DIR / "evaluation.json"
    if evaluation_file.exists():
        with open(evaluation_file) as f:
            eval_data = json.load(f)
            metrics['global'].update({
                'accuracy': eval_data.get('accuracy', 0),
                'f1': eval_data.get('f1', 0),
                'precision': eval_data.get('precision', 0),
                'recall': eval_data.get('recall', 0),
                'total_samples': eval_data.get('total_samples', 0)
            })

    per_class_file = RESULTS_DIR / "per_class_metrics.json"
    if per_class_file.exists():
        with open(per_class_file) as f:
            metrics['per_class'] = json.load(f)

    confusion_file = RESULTS_DIR / "confusion_matrix.json"
    if confusion_file.exists():
        with open(confusion_file) as f:
            metrics['confusion_matrix'] = json.load(f)

    for fold_dir in sorted(RESULTS_DIR.iterdir()):
        if not fold_dir.is_dir() or not fold_dir.name.startswith('fold_'):
            continue

        fold_name = fold_dir.name
        eval_file = fold_dir / "evaluation.json"

        if eval_file.exists():
            with open(eval_file) as f:
                fold_data = json.load(f)
                metrics['per_fold'].append({
                    'name': fold_name,
                    'accuracy': fold_data.get('accuracy', 0),
                    'f1': fold_data.get('f1', 0),
                    'precision': fold_data.get('precision', 0),
                    'recall': fold_data.get('recall', 0),
                    'total_samples': fold_data.get('total_samples', 0)
                })

        trainer_state = None
        for ckpt_dir in fold_dir.iterdir():
            if ckpt_dir.is_dir() and ckpt_dir.name.startswith('checkpoint-'):
                ts = ckpt_dir / "trainer_state.json"
                if ts.exists():
                    trainer_state = ts
                    break

        if trainer_state:
            with open(trainer_state) as f:
                state = json.load(f)
                metrics['folds'].append({
                    'name': fold_name,
                    'total_steps': state.get('total_steps', 0),
                    'best_model_checkpoint': state.get('best_model_checkpoint', 'N/A'),
                    'epoch': state.get('epoch', 0)
                })

    if metrics['per_fold']:
        n = len(metrics['per_fold'])
        metrics['global'].update({
            'accuracy': np.mean([f['accuracy'] for f in metrics['per_fold']]),
            'f1': np.mean([f['f1'] for f in metrics['per_fold']]),
            'precision': np.mean([f['precision'] for f in metrics['per_fold']]),
            'recall': np.mean([f['recall'] for f in metrics['per_fold']]),
            'std_accuracy': np.std([f['accuracy'] for f in metrics['per_fold']]),
            'std_f1': np.std([f['f1'] for f in metrics['per_fold']])
        })

    try:
        metrics['last_updated'] = datetime.fromtimestamp(
            RESULTS_DIR.stat().st_mtime
        ).strftime('%d/%m/%Y %H:%M:%S')
    except:
        metrics['last_updated'] = 'Desconhecido'

    return metrics

def create_dashboard():
    metrics = load_all_metrics()

    with gr.Blocks(
        title="Dashboard - Ouvidoria AI",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green"
        )
    ) as dashboard:

        gr.Markdown("""
        # Dashboard de Métricas - Ouvidoria Triagem Municipal
        ### Modelo: BERTimbau Fine-tuned para Classificação de Reclamações
        """)

        with gr.Row():
            status_box = gr.Markdown(
                f"**Última atualização:** {metrics.get('last_updated', 'Nunca')}\n"
                f"**Total de amostras:** {metrics['global']['total_samples']}"
            )
            refresh_btn = gr.Button("🔄 Atualizar Métricas", variant="primary")

        with gr.Tabs():
            with gr.TabItem("📊 Resumo Geral"):
                gr.Markdown("## Métricas Globais (Média entre Folds)")

                with gr.Row():
                    accuracy_gauge = gr.Number(
                        label="Accuracy",
                        value=round(metrics['global']['accuracy'] * 100, 2)
                    )
                    f1_gauge = gr.Number(
                        label="F1-Score",
                        value=round(metrics['global']['f1'] * 100, 2)
                    )
                    precision_gauge = gr.Number(
                        label="Precision",
                        value=round(metrics['global']['precision'] * 100, 2)
                    )
                    recall_gauge = gr.Number(
                        label="Recall",
                        value=round(metrics['global']['recall'] * 100, 2)
                    )

                if metrics['per_fold']:
                    gr.Markdown(f"""
                    **Desvio Padrão:**
                    - Accuracy: ±{round(metrics['global']['std_accuracy'] * 100, 2)}%
                    - F1-Score: ±{round(metrics['global']['std_f1'] * 100, 2)}%

                    **Total de Folds:** {len(metrics['per_fold'])}
                    """)

            with gr.TabItem("📁 Por Fold"):
                gr.Markdown("## Métricas Detalhadas por Fold")

                if metrics['per_fold']:
                    fold_headers = ["Fold", "Accuracy", "F1-Score", "Precision", "Recall", "Amostras"]
                    fold_data = []
                    for fold in metrics['per_fold']:
                        fold_data.append([
                            fold['name'],
                            f"{fold['accuracy']*100:.2f}%",
                            f"{fold['f1']*100:.2f}%",
                            f"{fold['precision']*100:.2f}%",
                            f"{fold['recall']*100:.2f}%",
                            fold.get('total_samples', 0)
                        ])

                    fold_table = gr.DataFrame(
                        headers=fold_headers,
                        value=fold_data,
                        label="Resultados por Fold"
                    )
                else:
                    gr.Markdown("⚠️ Nenhum fold encontrado. Execute o treinamento primeiro.")

                if metrics['folds']:
                    gr.Markdown("### Detalhes dos Treinamentos")
                    for fold_info in metrics['folds']:
                        gr.Markdown(f"""
                        **{fold_info['name']}**
                        - Epochs: {fold_info.get('epoch', 'N/A')}
                        - Total Steps: {fold_info.get('total_steps', 'N/A')}
                        - Best Checkpoint: `{fold_info.get('best_model_checkpoint', 'N/A')}`
                        """)

            with gr.TabItem("🎯 Por Classe"):
                gr.Markdown("## Métricas por Categoria")

                categories = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']
                secretarias = {
                    'Infraestrutura': 'Secretaria de Obras',
                    'Saúde': 'Secretaria de Saúde',
                    'Trânsito': 'DETRAN / Mobilidade',
                    'Iluminação': 'Serviços Urbanos',
                    'Outros': 'Ouvidoria Geral'
                }

                if metrics['per_class']:
                    class_headers = ["Categoria", "Secretaria", "F1-Score", "Precision", "Recall", "Support"]
                    class_data = []

                    for cat in categories:
                        if cat in metrics['per_class']:
                            m = metrics['per_class'][cat]
                            class_data.append([
                                cat,
                                secretarias.get(cat, ''),
                                f"{m.get('f1', 0)*100:.2f}%" if m.get('f1') else "N/A",
                                f"{m.get('precision', 0)*100:.2f}%" if m.get('precision') else "N/A",
                                f"{m.get('recall', 0)*100:.2f}%" if m.get('recall') else "N/A",
                                m.get('support', 0)
                            ])
                        else:
                            class_data.append([cat, secretarias.get(cat, ''), "N/A", "N/A", "N/A", 0])

                    class_table = gr.DataFrame(
                        headers=class_headers,
                        value=class_data,
                        label="Métricas por Classe"
                    )
                else:
                    gr.Markdown("⚠️ Nenhuma métrica por classe disponível.")

                gr.Markdown("""
                ### Mapeamento Categoria → Secretaria
                | Categoria | Secretaria Responsável |
                |-----------|------------------------|
                | Infraestrutura | Secretaria de Obras e Infraestrutura |
                | Saúde | Secretaria Municipal de Saúde |
                | Trânsito | DETRAN / Secretaria de Mobilidade |
                | Iluminação | Secretaria de Serviços Urbanos |
                | Outros | Ouvidoria Geral |
                """)

            with gr.TabItem("📈 Matriz de Confusão"):
                gr.Markdown("## Matriz de Confusão Normalizada")

                categories = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']

                if metrics['confusion_matrix']:
                    confusion = metrics['confusion_matrix']
                    headers = [""] + categories

                    confusion_display = []
                    for i, cat_true in enumerate(categories):
                        row = [f"**{cat_true}**"]
                        for j, cat_pred in enumerate(categories):
                            if i < len(confusion) and j < len(confusion[i]):
                                val = confusion[i][j]
                                if val > 0.5:
                                    row.append(f"**{val:.2f}**")
                                elif val > 0.2:
                                    row.append(f"{val:.2f}")
                                else:
                                    row.append(f"{val:.2f}")
                            else:
                                row.append("0.00")
                        confusion_display.append(row)

                    confusion_table = gr.DataFrame(
                        headers=headers,
                        value=confusion_display,
                        label="Predito →"
                    )
                else:
                    gr.Markdown("⚠️ Nenhuma matriz de confusão disponível.")

                gr.Markdown("""
                **Legenda:**
                - Linhas = Categoria Real
                - Colunas = Categoria Predita
                - Valores em **negrito** indicam alta probabilidade
                """)

            with gr.TabItem("🔧 Comandos"):
                gr.Markdown("## Comandos para Treinamento")

                gr.Markdown("""
                ```bash
                # 1. Baixar dataset
                cd training
                python download_dataset.py

                # 2. Preparar dados
                python dataset.py

                # 3. Treinar modelo (pode demorar em CPU)
                python trainer.py

                # 4. Avaliar modelo
                python evaluate_model.py

                # 5. Abrir dashboard
                python dashboard.py
                ```

                **Requisitos:**
                - Python 3.9+
                - ~4GB espaço em disco para modelo
                - Recomendado: GPU com CUDA para treinamento mais rápido
                """)

        gr.Markdown("---")
        gr.Markdown("*Dashboard gerado automaticamente - Use o botão 'Atualizar Métricas' para recarregar*")

        refresh_btn.click(
            fn=load_all_metrics,
            outputs=[status_box, accuracy_gauge, f1_gauge, precision_gauge, recall_gauge]
        )

    return dashboard

if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )