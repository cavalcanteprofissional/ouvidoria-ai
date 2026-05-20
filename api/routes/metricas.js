const express = require('express');
const { getMetricas } = require('../db');

const router = express.Router();

router.get('/', (req, res) => {
  try {
    const metricas = getMetricas();
    return res.json(metricas);
  } catch (err) {
    console.error('[metricas]', err);
    return res.status(500).json({ erro: 'Erro ao buscar métricas.' });
  }
});

module.exports = router;