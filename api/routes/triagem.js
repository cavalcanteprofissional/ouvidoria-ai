const express = require('express');
const { classify } = require('../services/classify');
const { extractEntities } = require('../services/ner');
const { getSecretaria } = require('../services/routing');
const { salvarReclamacao } = require('../db');

const router = express.Router();

const CATEGORIAS_VALIDAS = ['Infraestrutura', 'Saúde', 'Trânsito', 'Iluminação', 'Outros'];

router.post('/', async (req, res) => {
  const { texto } = req.body;

  if (!texto || typeof texto !== 'string') {
    return res.status(400).json({ erro: 'Campo "texto" é obrigatório.' });
  }

  const textoLimpo = texto.trim();

  if (textoLimpo.length < 10) {
    return res.status(400).json({
      erro: 'Texto muito curto. Descreva melhor o problema (mínimo 10 caracteres).'
    });
  }

  if (textoLimpo.length > 5000) {
    return res.status(400).json({
      erro: 'Texto muito longo. Máximo 5000 caracteres.'
    });
  }

  try {
    const [classificacao, entidades] = await Promise.all([
      classify(textoLimpo),
      extractEntities(textoLimpo)
    ]);

    if (!CATEGORIAS_VALIDAS.includes(classificacao.categoria)) {
      classificacao.categoria = 'Outros';
    }

    entidades.urgencia = ['alta', 'media', 'baixa'].includes(entidades.urgencia)
      ? entidades.urgencia
      : 'media';

    try {
      salvarReclamacao({
        texto: textoLimpo,
        categoria: classificacao.categoria,
        confianca: classificacao.confianca,
        localizacao: entidades.localizacao,
        organizacao: entidades.organizacao,
        equipamento: entidades.equipamento,
        data: entidades.data,
        urgencia: entidades.urgencia,
        secretaria_sugerida: getSecretaria(classificacao.categoria)
      });
    } catch (dbErr) {
      console.error('[triagem] Erro ao salvar no banco:', dbErr.message);
    }

    return res.json({
      texto: textoLimpo,
      categoria: classificacao.categoria,
      confianca: classificacao.confianca,
      entidades: {
        localizacao: entidades.localizacao || [],
        organizacao: entidades.organizacao || [],
        equipamento: entidades.equipamento || [],
        data: entidades.data || [],
        urgencia: entidades.urgencia
      },
      secretaria_sugerida: getSecretaria(classificacao.categoria),
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    console.error('[triagem] Erro:', err);
    return res.status(500).json({ erro: 'Erro interno ao processar a reclamação.' });
  }
});

module.exports = router;