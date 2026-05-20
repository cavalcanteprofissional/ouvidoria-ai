const axios = require('axios');

const HF_SPACES_URL = process.env.HF_SPACES_URL || 'https://cavalcanteprofissional-ouvidoria-ai.hf.space';
const HF_MODEL_ID = process.env.HF_MODEL_ID || 'cavalcanteprofissional/ouvidoria-ai';

async function classifyHFSpaces(text) {
  try {
    const res = await axios.post(
      `${HF_SPACES_URL}/predict`,
      { text },
      { timeout: 30000 }
    );
    return {
      categoria: res.data.categoria || res.data.category || 'Outros',
      confianca: parseFloat(res.data.confianca || res.data.confidence || 0.5),
      source: 'hf_spaces'
    };
  } catch (err) {
    console.log('[classify] HF Spaces não disponível:', err.message);
    return null;
  }
}

function classifyLocalMock(text) {
  const lower = text.toLowerCase();
  let categoria = 'Outros';
  let confianca = 0.6;

  if (lower.includes('buraco') || lower.includes('rua') || lower.includes('avenida') || lower.includes('calçada') || lower.includes('ponte') || lower.includes('água')) {
    categoria = 'Infraestrutura';
    confianca = 0.75;
  } else if (lower.includes('posto') || lower.includes('saúde') || lower.includes('médico') || lower.includes('hospital') || lower.includes('enfermeira') || lower.includes('farmácia')) {
    categoria = 'Saúde';
    confianca = 0.8;
  } else if (lower.includes('ônibus') || lower.includes('semáforo') || lower.includes('trânsito') || lower.includes('placa') || lower.includes('transporte')) {
    categoria = 'Trânsito';
    confianca = 0.7;
  } else if (lower.includes('luz') || lower.includes('poste') || lower.includes('iluminação') || lower.includes('lâmpada')) {
    categoria = 'Iluminação';
    confianca = 0.7;
  }

  return { categoria, confianca, source: 'local' };
}

async function classifyCohere(text) {
  if (!process.env.COHERE_API_KEY) {
    return null;
  }

  try {
    const { CohereClient } = require('cohere-ai');
    const cohere = new CohereClient({ token: process.env.COHERE_API_KEY });

    const EXAMPLES = [
      { text: 'Tem um buraco gigante na avenida principal', label: 'Infraestrutura' },
      { text: 'Calçada quebrada na frente da escola municipal', label: 'Infraestrutura' },
      { text: 'Falta dipirona no posto de saúde do bairro', label: 'Saúde' },
      { text: 'Médico não apareceu na UBS hoje de manhã', label: 'Saúde' },
      { text: 'Semáforo quebrado na esquina da rua 7', label: 'Trânsito' },
      { text: 'Ônibus 302 não passa há dois dias', label: 'Trânsito' },
      { text: 'Poste apagado há três noites na rua das flores', label: 'Iluminação' },
      { text: 'Toda a praça central está sem luz', label: 'Iluminação' },
      { text: 'Quero elogiar o atendimento do servidor João', label: 'Outros' },
      { text: 'Preciso de informação sobre alvará', label: 'Outros' }
    ];

    const res = await cohere.classify({
      inputs: [text],
      examples: EXAMPLES
    });

    const result = res.classifications[0];
    return {
      categoria: result.prediction,
      confianca: parseFloat(result.confidence.toFixed(2)),
      source: 'cohere'
    };
  } catch (err) {
    console.error('[classify] Cohere erro:', err.message);
    return null;
  }
}

async function classify(text) {
  let result = await classifyHFSpaces(text);
  if (result) return result;

  result = classifyLocalMock(text);
  if (result && result.confianca > 0.65) return result;

  result = await classifyCohere(text);
  if (result) return result;

  return { ...classifyLocalMock(text), source: 'fallback' };
}

module.exports = { classify };