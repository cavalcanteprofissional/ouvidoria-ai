# Changelog - Ouvidoria Triagem Municipal

## Histórico de Versões

---

## [v1.5.0] - 2026-05-20 - Fase 5: Treinamento Real

### Added
- Dataset real baixado (Kaggle/HuggingFace/sintético)
- Modelo BERTimbau fine-tuned treinado
- Métricas reais geradas (accuracy, f1, precision, recall)
- Matriz de confusão normalizada
- Dashboard Gradio populado com dados reais

### Mudanças de Performance
- Epochs: 1 (vs 3 original)
- Batch size: 4 (vs 16 original)
- Subset: 200 amostras (vs dataset completo)
- K-Folds: 2

### Configuração de Treinamento
```python
TRAINING_CONFIG = {
    'epochs': 1,
    'batch_size': 4,
    'warmup_steps': 10,
    'k_folds': 2
}
```

---

## [v1.4.0] - 2026-05-20 - Fase 4: Scripts de Treinamento Python (Completo)

### Added
- `training/config.py` - configuração centralizada
- `training/download_dataset.py` - download Kaggle + HuggingFace + sintético
- `training/dataset.py` - pré-processamento + augmentação
- `training/model.py` - carregamento BERTimbau
- `training/trainer.py` - K-Fold training com métricas
- `training/evaluate_model.py` - avaliação completa
- `training/dashboard.py` - dashboard Gradio (5 tabs)
- `training/hybrid_classifier.py` - classificação híbrida
- `training/upload_huggingface.py` - upload para HF Hub
- `training/run_pipeline.py` - pipeline unificado

### Fluxo Híbrido
1. HuggingFace Spaces
2. Modelo local fine-tuned
3. Cohere API (Zero-Shot fallback)

---

## [v1.3.0] - 2026-05-20 - Fase 3: Frontend React + Bootstrap

### Added
- App React 18 + Vite
- Bootstrap 5 para estilos
- Página Home (formulário cidadão)
- Página Dashboard (métricas admin)
- Navegação React Router
- Estados loading/erro/sucesso

### Build Output
- ~214KB JS (gzip: ~72KB)
- ~232KB CSS (gzip: ~31KB)

---

## [v1.2.0] - 2026-05-20 - Fase 2: NER e Dataset

### Added
- NER com 6 campos: localizacao, organizacao, nome_servidor, equipamento, data, urgencia
- Download Kaggle + HuggingFace + dados sintéticos
- Dashboard Gradio melhorado (5 tabs)

---

## [v1.1.0] - 2026-05-20 - Fase 1: Backend API

### Added
- Express server (CORS, Helmet, Rate Limit)
- `POST /api/triagem` - classificação + NER
- `GET /api/metricas` - métricas agregadas
- `GET /health` - health check
- SQLite (sql.js) - persistência
- Classificação híbrida (HF Spaces → local → Cohere)
- Mock fallback

### Endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/triagem` | Classifica + extrai entidades |
| GET | `/api/metricas` | Métricas agregadas |
| GET | `/health` | Health check |

---

## [v1.0.0] - 2026-05-20 - Fase 0: Setup do Projeto

### Added
- Estrutura base Node.js + Express
- `.gitignore` configurado
- `.env.example` e `.env.local`
- `package.json` com dependências

### Decisões de Arquitetura
| Aspecto | Decisão |
|---------|---------|
| Backend | Node.js (Express) + subprocess Python |
| Frontend | React 18 + Vite + Bootstrap 5 |
| Autenticação | API Key (somente) |
| Persistência | SQLite (sql.js - pure JS) |
| Deploy | Render.com |
| Testes | Playwright E2E |

---

## Roadmap

- [x] v1.0.0 - Setup do projeto
- [x] v1.1.0 - Backend API
- [x] v1.2.0 - NER e Dataset
- [x] v1.3.0 - Frontend React + Bootstrap
- [x] v1.4.0 - Scripts de Treinamento Python
- [x] v1.5.0 - Treinamento Real (BERTimbau)
- [ ] v1.6.0 - Deploy no Render
- [ ] v1.7.0 - Testes E2E

---

## Notas de Release

### v1.5.0
- Treinamento com subset pequeno para teste rápido
- Métricas podem ser baixas (~40-50% accuracy)
- Próximo passo: treinar com dataset completo em GPU

### v1.0.0
- Release inicial com estrutura base
- Setup completo do repositório Git
- Repositório GitHub restaurado após perda de dados