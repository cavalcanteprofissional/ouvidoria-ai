import os
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
KAGGLE_KEY = os.getenv('KAGGLE_KEY')
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME', 'cavalcanteprofissional')
HF_TOKEN = os.getenv('HF_TOKEN')

MODEL_CONFIG = {
    'name': 'neuralmind/bert-base-portuguese-cased',
    'num_labels': 5,
    'max_length': 256
}

TRAINING_CONFIG = {
    'learning_rate': 2e-5,
    'epochs': 1,
    'batch_size': 4,
    'warmup_steps': 10,
    'weight_decay': 0.01,
    'k_folds': 2,
    'max_samples': 200
}

CATEGORIES = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros']

CATEGORY_MAPPING = {
    'Crash': 'Infraestrutura', 'Bug': 'Infraestrutura', 'Technical': 'Infraestrutura', 'Hardware': 'Infraestrutura',
    'Maintenance': 'Saúde', 'Security': 'Saúde', 'Breach': 'Saúde',
    'Performance': 'Trânsito', 'Incident': 'Trânsito',
    'Documentation': 'Iluminação', 'Feedback': 'Iluminação',
    'Resolution': 'Outros', 'Feature': 'Outros', 'Sales': 'Outros', 'Product': 'Outros'
}

HF_SPACES_URL = "https://cavalcanteprofissional-ouvidoria-ai.hf.space"
HF_MODEL_ID = "cavalcanteprofissional/ouvidoria-ai"

ROUTING_MAP = {
    'Infraestrutura': 'Secretaria de Obras e Infraestrutura',
    'Saúde': 'Secretaria Municipal de Saúde',
    'Trânsito': 'DETRAN / Secretaria de Mobilidade',
    'Iluminação': 'Secretaria de Serviços Urbanos',
    'Outros': 'Ouvidoria Geral'
}