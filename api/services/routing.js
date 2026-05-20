const ROUTING = {
  'Infraestrutura': 'Secretaria de Obras e Infraestrutura',
  'Saúde': 'Secretaria Municipal de Saúde',
  'Trânsito': 'DETRAN / Secretaria de Mobilidade',
  'Iluminação': 'Secretaria de Serviços Urbanos',
  'Outros': 'Ouvidoria Geral'
};

function getSecretaria(categoria) {
  return ROUTING[categoria] || 'Ouvidoria Geral';
}

module.exports = { getSecretaria, ROUTING };