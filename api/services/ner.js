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
  "nome_servidor": ["nomes de servidores públicos mencionados"],
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

    const rawText = typeof res.text === 'function' ? res.text() : res.text;
    const clean = rawText.replace(/```json|```/g, '').trim();
    const parsed = JSON.parse(clean);

    return {
      localizacao: parsed.localizacao || [],
      organizacao: parsed.organizacao || [],
      nome_servidor: parsed.nome_servidor || [],
      equipamento: parsed.equipamento || [],
      data: parsed.data || [],
      urgencia: normalizeUrgencia(parsed.urgencia)
    };
  } catch (err) {
    console.error('[ner] Erro Cohere:', err.message);
    return mockExtractEntities(text);
  }
}

function normalizeUrgencia(urgencia) {
  const map = { alta: 'alta', alta: 'alta', média: 'media', media: 'media', baixa: 'baixa', baixa: 'baixa' };
  return map[urgencia?.toLowerCase()] || 'media';
}

function extractNames(text) {
  const names = [];
  const patterns = [
    /\b(doutor|dra|dr| Sr\.?|Sra\.?| professor|prof\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/gi,
    /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(disse|mencionou|atendeu|servidor|funcionário)/gi,
    /\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b/g
  ];

  const stopWords = ['Prefeitura', 'Municipal', 'Secretaria', 'Governo', 'Estado', 'Cidade', 'Bairro', 'Rua', 'Av'];

  for (const pattern of patterns) {
    const matches = text.matchAll(pattern);
    for (const match of matches) {
      const name = (match[2] || match[1]).trim();
      if (name.length > 3 && !stopWords.some(sw => name.includes(sw))) {
        names.push(name);
      }
    }
  }

  return [...new Set(names)];
}

function mockExtractEntities(text) {
  const result = {
    localizacao: [],
    organizacao: [],
    nome_servidor: [],
    equipamento: [],
    data: [],
    urgencia: 'media'
  };

  const lower = text.toLowerCase();

  const ruaPattern = /\b(rua|avenida|av\.|travessa|alameda|praça|viela|estrada|rodovia)\s+[\w\s]+/gi;
  const ruas = text.match(ruaPattern);
  if (ruas) {
    result.localizacao = ruas.map(r => r.replace(/^\w/, c => c.toUpperCase()));
  }

  const numberPattern = /\b(número|nº)\s*\d+/gi;
  const numbers = text.match(numberPattern);
  if (numbers) {
    result.localizacao.push(...numbers.map(n => n.replace(/^\w/, c => c.toUpperCase())));
  }

  const orgPatterns = [
    { pattern: /(?:posto|ubs|unidade\s+de\s+saúde|hospital|clínica|farmácia)\s+[\w\s]+/gi, label: 'Unidade de Saúde' },
    { pattern: /(?:escola|colégio|creche|instituto)\s+[\w\s]+/gi, label: 'Instituição de Ensino' },
    { pattern: /(?:prefeitura|secretaria|câmara)\s+[\w\s]+/gi, label: 'Órgão Público' },
    { pattern: /(?:posto\s+de\s+gasolina|posto\s+petrobras|bandeira)\s+[\w\s]*/gi, label: 'Posto de Gasolina' }
  ];

  for (const { pattern, label } of orgPatterns) {
    const matches = text.match(pattern);
    if (matches) {
      result.organizacao.push(...matches.map(m => m.trim()));
    }
  }

  const names = extractNames(text);
  result.nome_servidor = names;

  const equipPatterns = [
    { words: ['semáforo'], label: 'Semáforo' },
    { words: ['poste', 'luz', 'lâmpada'], label: 'Postes de Iluminação' },
    { words: ['ônibus', 'ônibus'], label: 'Linha de Ônibus' },
    { words: ['bomba', 'água'], label: 'Bomba d\'Água' },
    { words: ['radar'], label: 'Radar' },
    { words: ['placa'], label: 'Placa de Trânsito' },
    { words: ['ponte'], label: 'Ponte' },
    { words: ['calçada', 'calcada'], label: 'Calçada' },
    { words: ['bueiro'], label: 'Bueiro' }
  ];

  for (const { words, label } of equipPatterns) {
    if (words.some(w => lower.includes(w))) {
      result.equipamento.push(label);
    }
  }

  const datePatterns = [
    { pattern: /\d+\s*dias?/gi, label: 'dias' },
    { pattern: /\d+\s*semanas?/gi, label: 'semanas' },
    { pattern: /\d+\s*mêses?/gi, label: 'meses' },
    { pattern: /\d{1,2}\/\d{1,2}\/\d{2,4}/g, label: 'data' },
    { pattern: /há\s+\d+\s*(?:dia|dias?|semana|semanas?)/gi, label: 'tempo' }
  ];

  for (const { pattern } of datePatterns) {
    const matches = text.match(pattern);
    if (matches) {
      result.data.push(...matches);
    }
  }

  const urgencyHigh = ['urgente', 'emergência', 'risco', 'perigoso', 'grave', 'crítico', 'acidente', 'morte', 'ferido', 'socorro'];
  const urgencyLow = ['semana', 'mês', 'há muito', 'faz tempo', 'antigo', 'velho'];

  if (urgencyHigh.some(w => lower.includes(w))) {
    result.urgencia = 'alta';
  } else if (urgencyLow.some(w => lower.includes(w))) {
    result.urgencia = 'baixa';
  }

  result.localizacao = [...new Set(result.localizacao)];
  result.organizacao = [...new Set(result.organizacao)];
  result.nome_servidor = [...new Set(result.nome_servidor)];
  result.equipamento = [...new Set(result.equipamento)];
  result.data = [...new Set(result.data)];

  return result;
}

module.exports = { extractEntities };