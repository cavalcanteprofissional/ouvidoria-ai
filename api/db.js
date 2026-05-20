const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'data', 'ouvidoria.db');
let db = null;

async function initDb() {
  const SQL = await initSqlJs();

  if (fs.existsSync(dbPath)) {
    const buffer = fs.readFileSync(dbPath);
    db = new SQL.Database(buffer);
  } else {
    db = new SQL.Database();
  }

  db.run(`
    CREATE TABLE IF NOT EXISTS reclamacoes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      texto TEXT NOT NULL,
      categoria TEXT,
      confianca REAL,
      localizacao TEXT,
      organizacao TEXT,
      equipamento TEXT,
      data_text TEXT,
      urgencia TEXT,
      secretaria TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS metricas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      data DATE UNIQUE,
      total_requisicoes INTEGER DEFAULT 0,
      acuracia_media REAL DEFAULT 0,
      categoria_mais_frequente TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  db.run('CREATE INDEX IF NOT EXISTS idx_reclamacoes_categoria ON reclamacoes(categoria)');
  db.run('CREATE INDEX IF NOT EXISTS idx_reclamacoes_urgencia ON reclamacoes(urgencia)');

  salvarDb();
  return db;
}

function salvarDb() {
  if (!db) return;
  const data = db.export();
  const buffer = Buffer.from(data);
  fs.writeFileSync(dbPath, buffer);
}

function salvarReclamacao(dados) {
  if (!db) return;

  db.run(`
    INSERT INTO reclamacoes (texto, categoria, confianca, localizacao, organizacao, equipamento, data_text, urgencia, secretaria)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `, [
    dados.texto,
    dados.categoria,
    dados.confianca,
    JSON.stringify(dados.localizacao || []),
    JSON.stringify(dados.organizacao || []),
    JSON.stringify(dados.equipamento || []),
    JSON.stringify(dados.data || []),
    dados.urgencia,
    dados.secretaria_sugerida
  ]);

  atualizarMetricas(dados.categoria);
  salvarDb();
}

function atualizarMetricas(categoria) {
  if (!db) return;

  const hoje = new Date().toISOString().split('T')[0];
  const existente = db.exec(`SELECT total_requisicoes FROM metricas WHERE data = '${hoje}'`);

  if (existente.length > 0 && existente[0].values.length > 0) {
    db.run(`UPDATE metricas SET total_requisicoes = total_requisicoes + 1, categoria_mais_frequente = ? WHERE data = ?`, [categoria, hoje]);
  } else {
    db.run(`INSERT INTO metricas (data, total_requisicoes, categoria_mais_frequente) VALUES (?, 1, ?)`, [hoje, categoria]);
  }
}

function getMetricas() {
  if (!db) {
    return { total: 0, porCategoria: {}, porUrgencia: { alta: 0, media: 0, baixa: 0 } };
  }

  const totalResult = db.exec('SELECT COUNT(*) as count FROM reclamacoes');
  const total = totalResult.length > 0 ? totalResult[0].values[0][0] : 0;

  const porCategoria = {};
  const catResult = db.exec('SELECT categoria, COUNT(*) as count FROM reclamacoes GROUP BY categoria');
  if (catResult.length > 0) {
    catResult[0].values.forEach(row => {
      porCategoria[row[0]] = row[1];
    });
  }

  const porUrgencia = { alta: 0, media: 0, baixa: 0 };
  const urgResult = db.exec('SELECT urgencia, COUNT(*) as count FROM reclamacoes GROUP BY urgencia');
  if (urgResult.length > 0) {
    urgResult[0].values.forEach(row => {
      if (['alta', 'media', 'baixa'].includes(row[0])) {
        porUrgencia[row[0]] = row[1];
      }
    });
  }

  return { total, porCategoria, porUrgencia };
}

module.exports = { initDb, salvarReclamacao, getMetricas };