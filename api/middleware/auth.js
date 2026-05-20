const apiKey = process.env.API_KEY;

if (!apiKey) {
  console.warn('[auth] Aviso: API_KEY não configurada no .env');
}

function authMiddleware(req, res, next) {
  if (!apiKey) {
    return next();
  }

  const key = req.headers['x-api-key'];

  if (!key) {
    return res.status(401).json({ erro: 'API Key não fornecida.' });
  }

  if (key !== apiKey) {
    return res.status(403).json({ erro: 'API Key inválida.' });
  }

  next();
}

module.exports = { authMiddleware };