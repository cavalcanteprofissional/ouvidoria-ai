const { CohereClient } = require('cohere-ai');

const cohere = new CohereClient({
  token: process.env.COHERE_API_KEY
});

const PREAMBLE = `Você é um extrator de entidades de reclamações municipais brasileiras.
Retorne APENAS um objeto JSON válido, sem explicações, sem markdown, sem backticks.
Formato obrigatório:
{
  "localizacao": ["lista de ruas, bairros, pontos de referência mencionados"],
  "organizacao": ["postos de saúde, escolas, órgãos públicos citados"],
  "equipamento": ["equipamentos mencionados (semáforo, poste, bomba d'água, etc)"],
  "data": ["datas e prazos mencionados"],
  "urgencia": "alta | media | baixa"
}
Critério de urgência: alta = risco à vida ou segurança; media = impacto no cotidiano; baixa = informativo.`;

async function extractEntities(text) {
  if (!process.env.COHERE_API_KEY) {
    return mockExtractEntities(text);
  }

  try {
    const res = await cohere.chat({
      model: 'command-r',
      message: text,
      preamble: PREAMBLE
    });

    const clean = res.text().replace(/```json|```/g, '').trim();
    return JSON.parse(clean);
  } catch (err) {
    console.error('[ner] Erro:', err.message);
    return mockExtractEntities(text);
  }
}

function mockExtractEntities(text) {
  const result = {
    localizacao: [],
    organizacao: [],
    equipamento: [],
    data: [],
    urgencia: 'media'
  };

  const lower = text.toLowerCase();

  const ruas = lower.match(/\b(rua|avenida|av\.|travessa|alameda|praça|viela)\s+[\w\s]+/gi);
  if (ruas) {
    result.localizacao = ruas.map(r => r.replace(/^\w/, c => c.toUpperCase()));
  }

  if (lower.includes('posto') || lower.includes('ubs') || lower.includes('hospital') || lower.includes('clínica')) {
    result.organizacao.push('Unidade de Saúde');
  }
  if (lower.includes('escola') || lower.includes('colégio')) {
    result.organizacao.push('Instituição de Ensino');
  }

  if (lower.includes('semáforo')) result.equipamento.push('Semáforo');
  if (lower.includes('poste')) result.equipamento.push('Poste de luz');
  if (lower.includes('ônibus')) result.equipamento.push('Ônibus');

  const dias = lower.match(/\d+\s*dias?/g);
  if (dias) result.data = dias;

  if (lower.includes('urgente') || lower.includes('emergência') || lower.includes('risco') || lower.includes('perigoso')) {
    result.urgencia = 'alta';
  } else if (lower.includes('semana') || lower.includes('mês')) {
    result.urgencia = 'baixa';
  }

  return result;
}

module.exports = { extractEntities };