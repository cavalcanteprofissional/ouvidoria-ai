# Ouvidoria Triagem Municipal

## Sistema Inteligente de Triagem com Inteligência Artificial

---

## O Problema

- Reclamações de cidadãos precisam de triagem manual
- Servidores perdem tempo categorizando atendimentos
- Atraso no encaminhamento para secretarias responsáveis
- Dificuldade em identificar urgência e localização dos problemas

---

## Nossa Solução

- **Classificação automática** em 5 categorias
- **Extração de entidades** (localização, urgência, data, equipamento)
- **Encaminhamento inteligente** para a secretaria correta
- Tudo com IA, sem necessidade de triagem manual!

---

## Categorias Suportadas

| Categoria | Secretaria Responsável |
|-----------|------------------------|
| Infraestrutura | Secretaria de Obras e Infraestrutura |
| Saúde | Secretaria Municipal de Saúde |
| Trânsito | DETRAN / Secretaria de Mobilidade |
| Iluminação | Secretaria de Serviços Urbanos |
| Outros | Ouvidoria Geral |

---

## Funcionalidades Principais

- 🔍 Classificação Automática por IA
- 🏷️ Extração de Entidades (NER)
- 🔐 Autenticação Segura (API Key + Rate Limiting)
- 📊 Dashboard de Métricas
- 💾 Persistência de Dados (SQLite)
- 🌐 Interface Web Responsiva

---

## Arquitetura do Sistema

- **Frontend**: React 18 + Vite + Bootstrap 5
- **Backend**: Node.js + Express
- **Banco de Dados**: SQLite (sql.js)
- **Serviços de IA**:
  - HuggingFace Spaces (primário)
  - Classificação local (fallback)
  - Cohere API (último recurso)

---

## Fluxo de Classificação

1. Usuário envia reclamação via frontend
2. API verifica autenticação
3. Pipeline híbrido tenta:
   - HuggingFace Spaces
   - Classificação local por palavras-chave
   - Cohere API como último recurso
4. NER extrai entidades do texto
5. Routing direciona para secretaria
6. Dados salvos no SQLite

---

## Tecnologias Utilizadas

### Backend
- Node.js 18+
- Express.js
- sql.js (SQLite em memória)
- Cohere AI SDK

### Frontend
- React 18
- Vite
- Bootstrap 5

### Machine Learning
- BERTimbau (fine-tuning)
- Transformers (HuggingFace)
- K-Fold Cross-Validation

---

## Dataset

- **Fonte**: Kaggle - Multilingual Customer Support Tickets
- **Total**: ~20.000 tickets
- **Pré-processamento**:
  - Mapeamento de 8 tags para 5 categorias
  - Filtragem por idioma
  - Divisão: 80% treino, 10% validação, 10% teste

---

## Resultados

| Métrica | Valor |
|---------|-------|
| Accuracy | 45.30% ± 0.10% |
| F1-Score | 28.25% ± 0.11% |
| Precision | 20.52% |
| Recall | 45.30% |

**Nota**: Métricas podem melhorar com mais dados e treinamento em GPU

---

## Próximos Passos

- ✅ API REST com Express
- ✅ Frontend React
- ✅ Classificação híbrida
- ✅ Fine-tuning BERTimbau
- ⏳ Deploy em produção (Render/Railway)
- ⏳ Upload modelo para HuggingFace Spaces
- ⏳ Melhoria das métricas com mais dados

---

## Obrigado!

Repositório: github.com/covalcanteprofissional/ouvidoria-ai

Made with ❤️ using Node.js, React, BERTimbau and Cohere