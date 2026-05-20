🏛️ Ouvidoria Triagem Municipal
Sistema inteligente de triagem para ouvidoria municipal que usa Inteligência Artificial para classificar automaticamente reclamações de cidadãos e direcioná-las para a secretaria responsável.

✨ O que este projeto faz?
Imagine que um cidadão envia uma mensagem como:

"Tem um buraco enorme na Av. Principal, perto do posto de saúde, já faz 3 dias"

O sistema automaticamente:

Classifica a categoria (Infraestrutura)
Extrai entidades (localização, equipamento, data, urgência)
Direciona para a Secretaria de Obras e Infraestrutura
Tudo isso com IA, sem necessidade de triagem manual!

🚀 Funcionalidades
Feature	Descrição
🔍 Classificação Automática	Categoriza reclamações em 5 categorias (Infraestrutura, Saúde, Trânsito, Iluminação, Outros)
🏷️ Extração de Entidades (NER)	Identifica localização, equipamentos, nomes de servidores, datas e urgência
🔐 Autenticação Segura	API Key + Rate Limiting + Helmet headers
📊 Dashboard de Métricas	Interface Gradio com KPIs do modelo
🔄 Sistema Híbrido	Suporte a múltiplos modelos (pronto para HuggingFace + Cohere)
🌐 Interface Web	Frontend React responsivo
🔄 Fluxos de Dados (Mermaid)
1. Visão Geral do Projeto
ML

Backend

Cliente


























2. Fluxo de Classificação (Zero-Shot com Cohere)
Output

Classificação

Input











3. Fluxo de Extração de Entidades (NER)
Saída

Processamento

Entrada












4. Fluxo de Treinamento (Fine-tuning BERTimbau)
Output

Training

Data





















5. Fluxo de Tokenização
Tensor Output

Tokenizer

Entrada










6. Fluxo do Sistema Híbrido (Fallback)
















7. Fluxo de Requisição Completo
📁 DB/Arquivo
🤖 Modelo
🔐 Auth
⚙️ API
🌐 Frontend
👤 Usuário
📁 DB/Arquivo
🤖 Modelo
🔐 Auth
⚙️ API
🌐 Frontend
👤 Usuário
"Categoria: Infraestrutura
Secretaria: Obras"
Envia reclamação
POST /api/triagem
{texto, x-api-key}
Verifica API Key
✅ Validado
Envia texto para classificação
Processa (classificação + NER)
Retorna resultado
JSON com categoria + entidades
+ secretaria sugerida
Exibe resultado
🛠️ Tecnologias
Backend
Node.js + Express
Cohere API (Zero-Shot Classification + Chat)
BERTimbau (Fine-tuned para classificação)
Frontend
React 18 + Vite
Bootstrap 5
Machine Learning
Transformers (HuggingFace)
BERTimbau (Modelo português)
K-Fold Cross-Validation
📚 Dataset Utilizado
Fonte
Nome: Multilingual Customer Support Tickets
Plataforma: Kaggle
URL: https://www.kaggle.com/datasets/bitext/llm-legal-constraint-training
Formato: CSV
Características do Dataset
Propriedade	Valor
Total de amostras	~20.000 tickets
Idiomas	Alemão (de), Inglês (en)
Colunas	subject, body, answer, type, queue, priority, language, tag_1-8
Tipos de tickets	Incident, Request
Filas	General Inquiry, Customer Service
Prioridades	low, medium, high
Categorias (mapped from tags)
O dataset original possui tags em múltiplas colunas. Para este projeto, mapeamos para 5 categorias de ouvidoria municipal:

Categoria Original	Categoria Mapeada
Crash, Bug, Technical, Hardware	Infraestrutura
Maintenance, Security, Breach	Saúde
Performance, Incident	Trânsito
Documentation, Feedback	Iluminação
Resolution, Feature, Sales, Product	Outros
Pré-processamento
Filtragem por idioma: English (en) + German (de) → Português simulado
Mapeamento de categorias: 8 tags → 5 categorias de ouvidoria
Seleção de subconjunto: 1000 amostras (para treinamento em CPU)
Divisão: 80% treino, 10% validação, 10% teste
K-Fold: k=2 para validação cruzada
🤖 Modelos HuggingFace
Modelos Utilizados
1. Treinamento (Fine-tuning)
Modelo	Descrição	Uso
neuralmind/bert-base-portuguese-cased	BERTimbau Base - Modelo BERT pré-treinado em português brasileiro	Pré-treinado para fine-tuning
neuralmind/bert-base-portuguese-cased	Same	Tokenizador oficial
HuggingFace Hub: https://huggingface.co/neuralmind/bert-base-portuguese-cased
Vocabulário: 29.794 tokens
Arquitetura: 12 layers, 768 hidden, 12 attention heads
2. Inferência (Classification + NER)
Modelo	Provider	Uso
Cohere command-r	Cohere API	Classificação Zero-Shot + NER
neuralmind/bert-base-portuguese-cased	Local (fine-tuned)	Classificação com modelo treinado
Pipeline de Inferência
# Classificação local
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained('./models/checkpoints/fold_0')
tokenizer = AutoTokenizer.from_pretrained('./models/checkpoints/fold_0')
Modelos Alternativos (Futuro)
Modelo	potential Uso
distilbert-base-portuguese-cased	Versão leve do BERTimbau (~40% menor)
bert-base-multilingual-cased	Suporte multilíngue (inclui PT)
cardiffnlp/twitter-roberta-base-sentiment	Análise de sentimento
📋 Pré-requisitos
Node.js 18+
Python 3.9+ (para treinamento)
Conta no HuggingFace
Conta no Cohere (gratuito)
⚡ Instalação Rápida
1. Clone o projeto
git clone https://github.com/seu-usuario/ouvidoria-triagem.git
cd ouvidoria-triagem
2. Configure as variáveis de ambiente
Crie o arquivo .env.local na raiz:

COHERE_API_KEY=sua_chave_cohere_aqui
API_KEY=sua_api_key_para_autenticacao
PORT=3000
No diretório client/, crie .env.local:

VITE_API_KEY=sua_api_key_para_autenticacao
3. Instale as dependências
# Backend
npm install

# Frontend
cd client && npm install
🎯 Como Executar
Modo Desenvolvimento (2 terminais)
Terminal 1 - Backend:

npm run dev
# Servidor: http://localhost:3000
Terminal 2 - Frontend:

cd client && npm run dev
# Frontend: http://localhost:5173
Modo Produção
# Build do frontend
npm run build

# Iniciar servidor
npm start
📡 Endpoints da API
Método	Rota	Descrição
POST	/api/triagem	Classifica e extrai entidades
GET	/health	Health check
Exemplo de Requisição
curl -X POST http://localhost:3000/api/triagem \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua_api_key_aqui" \
  -d '{"texto": "Buraco enorme na Av. Principal, já faz 3 dias"}'
Resposta
{
  "texto": "Buraco enorme na Av. Principal, já faz 3 dias",
  "categoria": "Infraestrutura",
  "confianca": 0.94,
  "entidades": {
    "localizacao": ["Av. Principal"],
    "organizacao": [],
    "nome_servidor": [],
    "equipamento": [],
    "data": ["3 dias"],
    "urgencia": "media"
  },
  "secretaria_sugerida": "Secretaria de Obras e Infraestrutura",
  "timestamp": "2026-05-19T20:00:00.000Z"
}
📁 Estrutura do Projeto
ouvidoria-triagem/
├── api/                          # Backend Node.js
│   ├── index.js                 # Servidor Express
│   ├── middleware/auth.js      # Autenticação + Rate Limit
│   ├── routes/triagem.js        # Endpoint de triagem
│   └── services/
│       ├── classify.js         # Zero-Shot (Cohere)
│       └── ner.js              # Extração de entidades
│
├── client/                       # Frontend React
│   ├── src/
│   │   ├── App.jsx             # Componente principal
│   │   ├── App.css             # Estilos
│   │   └── main.jsx            # Entry point
│   └── dist/                   # Build production
│
├── training/                    # Machine Learning
│   ├── config.py              # Hiperparâmetros
│   ├── dataset.py             # Preparação de dados
│   ├── model.py               # Modelo BERTimbau
│   ├── trainer.py             # K-Fold training
│   ├── evaluate_model.py      # Avaliação
│   ├── dashboard.py          # Dashboard Gradio
│   └── upload_huggingface.py  # Upload para HF
│
├── models/                      # Modelos treinados
│   └── checkpoints/
│       └── fold_0/            # Modelo BERTimbau fine-tuned
│
├── results/                    # Métricas e logs
│   └── evaluation.json        # Métricas completas
│
├── data/                       # Dados
│   └── raw/                   # Dataset original
│
└── README.md
📊 Métricas do Modelo (Fine-tuned)
Resultados K-Fold (2 folds)
Métrica	Valor
Accuracy	45.30% ± 0.10%
F1-Score	28.25% ± 0.11%
Precision	20.52%
Recall	45.30%
Nota: Métricas podem ser melhoradas com mais dados e treinamento em GPU.

Categorias do Modelo
Categoria	Secretaria Responsável
Infraestrutura	Secretaria de Obras e Infraestrutura
Saúde	Secretaria Municipal de Saúde
Trânsito	DETRAN / Secretaria de Mobilidade
Iluminação	Secretaria de Serviços Urbanos
Outros	Ouvidoria Geral
📈 Dashboard de Métricas
Para visualizar as métricas do modelo treinado:

cd training
python dashboard.py
Acesse: http://localhost:7860 (ou 7861 se estiver em uso)

O dashboard inclui:

📋 Resumo das métricas (Accuracy, F1, Precision, Recall)
📈 Matriz de confusão visual
🎯 Métricas por classe
🔄 Comparação entre folds
📂 Detalhes por fold
🔧 Configuração Avançada
Variáveis de Ambiente
Variável	Descrição	Padrão
COHERE_API_KEY	Chave da API Cohere	Obrigatório
API_KEY	Chave para autenticação	Obrigatório
PORT	Porta do servidor	3000
CLIENT_URL	URL do frontend (CORS)	http://localhost:5173
🚀 Próximos Passos (Roadmap)
 API REST com Express
 Frontend React
 Classificação Cohere (Zero-Shot)
 Fine-tuning BERTimbau
 Dashboard de métricas
 Upload modelo para HuggingFace
 Sistema híbrido (HF + Cohere fallback)
 Deploy (Render/Railway)
📖 Documentação Adicional
Roadmap completo
Changelog
🤝 Como Contribuir
Fork o projeto
Crie uma branch (git checkout -b feature/nova-feature)
Commit suas mudanças (git commit -m 'Add nova feature')
Push para a branch (git push origin feature/nova-feature)
Abra um Pull Request
📄 Licença
MIT License - sinta-se livre para usar!

💡 Dúvidas?
Para dúvidas ou sugestões, abra uma issue no repositório!

Made with ❤️ using Node.js, React, BERTimbau and Cohere