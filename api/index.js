const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, '..', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, '..', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

require('dotenv').config({ path: path.join(__dirname, '..', '.env.local') });
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');

const { initDb } = require('./db');
const triagemRouter = require('./routes/triagem');
const metricasRouter = require('./routes/metricas');

const app = express();
const PORT = process.env.PORT || 3000;

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { erro: 'Limite de requisições excedido. Tente novamente em 15 minutos.' }
});

app.use(helmet());
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173'
}));
app.use(express.json());
app.use(limiter);

const clientDistPath = path.join(__dirname, '..', 'client', 'dist');
if (fs.existsSync(clientDistPath)) {
  app.use(express.static(clientDistPath));
}

app.get('/health', (_, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.use('/api/triagem', triagemRouter);
app.use('/api/metricas', metricasRouter);

app.get('*', (_, res) => {
  const indexPath = path.join(clientDistPath, 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(503).json({
      erro: 'Frontend não disponível',
      message: 'Execute "cd client && npm run build" primeiro'
    });
  }
});

app.use((err, req, res, next) => {
  console.error('[Error]', err);
  res.status(500).json({ erro: 'Erro interno no servidor.' });
});

app.listen(PORT, async () => {
  await initDb();
  console.log(`Servidor rodando na porta ${PORT}`);
});

module.exports = app;