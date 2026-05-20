const { CohereClient } = require('cohere-ai');

const cohere = new CohereClient({
  token: process.env.COHERE_API_KEY
});

const LABELS = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros'];

const EXAMPLES = [
  { text: 'Tem um buraco gigante na avenida principal perto do posto de saúde', label: 'Infraestrutura' },
  { text: 'Calçada quebrada na frente da escola municipal já faz uma semana', label: 'Infraestrutura' },
  { text: 'Falta de água no bairro inteiro há 3 dias, situação crítica', label: 'Infraestrutura' },
  { text: 'Falta dipirona e soro no posto de saúde do bairro centro', label: 'Saúde' },
  { text: 'Médico não apareceu na UBS hoje de manhã, atendimento cancelado', label: 'Saúde' },
  { text: 'Farmácia do posto está sem medicamentos há semanas', label: 'Saúde' },
  { text: 'Semáforo quebrado na esquina da rua 7 com a rua 15, perigoso', label: 'Trânsito' },
  { text: 'Ônibus 302 não passa há dois dias no meu bairro, sem informação', label: 'Trânsito' },
  { text: ' много транспорта на дороге', label: 'Trânsito' },
  { text: 'Poste apagado há três noites na rua das flores, escuridão total', label: 'Iluminação' },
  { text: 'Toda a praça central está sem luz, inseguro à noite', label: 'Iluminação' },
  { text: 'Lâmpada do poste em frente ao número 45 está queimada há dias', label: 'Iluminação' },
  { text: 'Quero elogiar o atendimento do servidor João da ouvidoria', label: 'Outros' },
  { text: 'Preciso de informação sobre como tirar alvará de funcionamento', label: 'Outros' },
  { text: 'Denúncia sobre irregularities na administração pública', label: 'Outros' }
];

async function classify(text) {
  if (!process.env.COHERE_API_KEY) {
    return mockClassify(text);
  }

  try {
    const res = await cohere.classify({
      inputs: [text],
      examples: EXAMPLES
    });

    const result = res.classifications[0];
    return {
      categoria: result.prediction,
      confianca: parseFloat(result.confidence.toFixed(2))
    };
  } catch (err) {
    console.error('[classify] Erro:', err.message);
    return mockClassify(text);
  }
}

function mockClassify(text) {
  const lower = text.toLowerCase();
  let categoria = 'Outros';
  let confianca = 0.5;

  if (lower.includes('buraco') || lower.includes('rua') || lower.includes('avenida') || lower.includes('calçada')) {
    categoria = 'Infraestrutura';
    confianca = 0.75;
  } else if (lower.includes('posto') || lower.includes('saúde') || lower.includes('médico') || lower.includes('hospital')) {
    categoria = 'Saúde';
    confianca = 0.8;
  } else if (lower.includes('ônibus') || lower.includes('semáforo') || lower.includes('trânsito')) {
    categoria = 'Trânsito';
    confianca = 0.7;
  } else if (lower.includes('luz') || lower.includes('poste') || lower.includes('iluminação')) {
    categoria = 'Iluminação';
    confianca = 0.7;
  }

  return { categoria, confianca };
}

module.exports = { classify };