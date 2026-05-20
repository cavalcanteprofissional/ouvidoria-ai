# Changelog - Ouvidoria Triagem Municipal

## [v1.0.0] - 2026-05-20 - Fase 0: Setup do Projeto

### Added
- Estrutura base do projeto com Node.js + Express
- `.gitignore` configurado (ignora `node_modules/`, `.env`, `models/`, `results/`)
- Arquivo `.env.example` com variáveis necessárias
- `package.json` com dependências base
- Documentação SKILL para guiar implementação

### Estrutura
```
ouvidoria-triagem/
├── api/              # Backend Node.js Express
├── client/           # Frontend React + Bootstrap 5
├── training/        # Scripts Python para BERTimbau fine-tuning
├── models/           # Checkpoints (gitignored)
├── results/          # Métricas (gitignored)
├── data/             # Datasets crus
├── package.json
├── .env.example
└── .gitignore
```

### Decisões de Arquitetura
| Aspecto | Decisão |
|---------|---------|
| Backend | Node.js (Express) + subprocess Python para ML |
| Frontend | React 18 + Vite + Bootstrap 5 |
| Autenticação | API Key (somente) |
| Persistência | SQLite (sql.js - pure JS) |
| Deploy | Render.com (1 serviço) |
| Testes | Playwright E2E |

---

## [v1.1.0] - 2026-05-20 - Fase 1: Backend API

### Added
- Servidor Express com CORS configurado
- Endpoint `POST /api/triagem` - classificação + NER
- Endpoint `GET /health` - health check
- Endpoint `GET /api/metricas` - métricas agregadas
- Rate limiting básico (100 req/15min)
- Helmet headers de segurança
- Serviços Cohere (classificação Zero-Shot + NER)
- Mock fallback quando COHERE_API_KEY não está configurada

### Arquivos
```
api/
├── index.js              # Servidor principal
├── db.js                 # SQLite (sql.js)
├── middleware/
│   └── auth.js           # Validação API Key
├── routes/
│   ├── triagem.js        # Endpoint POST /api/triagem
│   └── metricas.js       # Endpoint GET /api/metricas
└── services/
    ├── classify.js       # Classificação Zero-Shot (Cohere)
    ├── ner.js            # Extração de entidades (Cohere Chat)
    └── routing.js        # Mapa categoria → secretaria
```

### Endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/triagem` | Classifica texto + extrai entidades |
| GET | `/api/metricas` | Métricas agregadas |
| GET | `/health` | Health check |

---

## [v1.3.0] - 2026-05-20 - Fase 3: Frontend React + Bootstrap

### Added
- App React 18 com Vite
- Bootstrap 5 para estilos
- Página de formulário do cidadão (`/`)
- Dashboard admin com métricas (`/dashboard`)
- Navegação com React Router
- Estados de loading, erro e sucesso
- Fallback para API mock

### Componentes
```
client/src/
├── App.jsx               # Router + layout
├── main.jsx             # Entry point
├── index.css            # Estilos globais
├── pages/
│   ├── Home.jsx         # Formulário do cidadão
│   └── Dashboard.jsx    # Dashboard admin
└── services/
    └── api.js           # Cliente da API (axios)
```

### Build
- `client/dist/` pronto para deploy
- ~214KB JS (gzip: ~72KB)
- ~232KB CSS (gzip: ~31KB)

## [v1.4.0] - 2026-05-20 - Fase 4: Scripts de Treinamento Python

### Added
- `training/config.py` - configuração centralizada
- `training/download_dataset.py` - download Kaggle + fallback HuggingFace
- `training/dataset.py` - pré-processamento + dados sintéticos
- `training/model.py` - carregamento BERTimbau
- `training/trainer.py` - K-Fold training com métricas
- `training/evaluate_model.py` - avaliação completa
- `training/dashboard.py` - dashboard Gradio (globais, por fold, por classe, matriz confusão)
- `training/hybrid_classifier.py` - fluxo HF Spaces → local → Cohere
- `training/upload_huggingface.py` - upload para HF Hub

### Fluxo Híbrido
1. HuggingFace Spaces
2. Modelo local fine-tuned
3. Cohere API (Zero-Shot fallback)

### Dashboard Gradio (4 abas)
- Resumo Geral: accuracy, f1, precision, recall
- Por Fold: métricas individuais
- Por Classe: métricas por categoria
- Matriz de Confusão: normalizada

---

## Roadmap

- [x] v1.0.0 - Setup do projeto
- [x] v1.1.0 - Backend API
- [x] v1.1.0 - Banco SQLite (sql.js)
- [x] v1.3.0 - Frontend React + Bootstrap
- [x] v1.4.0 - Scripts de Treinamento Python
- [ ] v1.5.0 - Deploy no Render
- [ ] v1.6.0 - Testes E2E