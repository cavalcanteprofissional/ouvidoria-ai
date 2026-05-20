import { useState } from 'react'
import { enviarReclamacao } from '../services/api'

const CORES_CATEGORIA = {
  'Infraestrutura': 'bg-danger',
  'Saúde': 'bg-warning text-dark',
  'Trânsito': 'bg-info',
  'Iluminação': 'bg-secondary',
  'Outros': 'bg-dark'
}

const CORES_URGENCIA = {
  alta: 'urgencia-alta',
  media: 'urgencia-media',
  baixa: 'urgencia-baixa'
}

function Home() {
  const [texto, setTexto] = useState('')
  const [loading, setLoading] = useState(false)
  const [resultado, setResultado] = useState(null)
  const [erro, setErro] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErro('')
    setResultado(null)

    if (texto.trim().length < 10) {
      setErro('Por favor, descreva o problema com mais detalhes (mínimo 10 caracteres).')
      return
    }

    setLoading(true)

    try {
      const data = await enviarReclamacao(texto)
      setResultado(data)
    } catch (err) {
      setErro(err.response?.data?.erro || 'Erro ao processar. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const limpar = () => {
    setTexto('')
    setResultado(null)
    setErro('')
  }

  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header bg-white">
              <h4 className="mb-0">Registrar Reclamação</h4>
              <p className="text-muted small mb-0">
                Descreva seu problema e encaminharemos ao setor responsável.
              </p>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="texto" className="form-label fw-semibold">
                    Descrição do Problema
                  </label>
                  <textarea
                    id="texto"
                    className="form-control"
                    rows="4"
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Ex: Tem um buraco enorme na Av. Principal, perto do posto de saúde, já faz 3 dias..."
                    disabled={loading}
                  />
                  <div className="form-text">
                    {texto.length}/5000 caracteres
                  </div>
                </div>

                {erro && (
                  <div className="alert alert-danger" role="alert">
                    {erro}
                  </div>
                )}

                <div className="d-flex gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || texto.trim().length < 10}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        Processando...
                      </>
                    ) : (
                      'Enviar Reclamação'
                    )}
                  </button>
                  {resultado && (
                    <button type="button" className="btn btn-outline-secondary" onClick={limpar}>
                      Nova Reclamação
                    </button>
                  )}
                </div>
              </form>

              {resultado && (
                <div className="result-card mt-4 p-4 bg-light rounded">
                  <div className="d-flex align-items-center gap-3 mb-3">
                    <span className={`badge ${CORES_CATEGORIA[resultado.categoria]} categoria-badge`}>
                      {resultado.categoria}
                    </span>
                    <span className="text-muted">
                      Confiança: {(resultado.confianca * 100).toFixed(0)}%
                    </span>
                  </div>

                  <h5 className="mb-2">
                    Encaminhado para: <strong>{resultado.secretaria_sugerida}</strong>
                  </h5>

                  <hr />

                  <div className="row">
                    <div className="col-md-6">
                      <strong className="text-muted">Localização:</strong>
                      <p className="mb-2">
                        {resultado.entidades.localizacao?.length > 0
                          ? resultado.entidades.localizacao.join(', ')
                          : 'Não identificada'}
                      </p>

                      <strong className="text-muted">Organização:</strong>
                      <p className="mb-2">
                        {resultado.entidades.organizacao?.length > 0
                          ? resultado.entidades.organizacao.join(', ')
                          : 'Não mencionada'}
                      </p>

                      <strong className="text-muted">Equipamento:</strong>
                      <p className="mb-0">
                        {resultado.entidades.equipamento?.length > 0
                          ? resultado.entidades.equipamento.join(', ')
                          : 'Não mencionado'}
                      </p>
                    </div>
                    <div className="col-md-6">
                      <strong className="text-muted">Urgência:</strong>
                      <p className={`mb-2 ${CORES_URGENCIA[resultado.entidades.urgencia]}`}>
                        {resultado.entidades.urgencia.toUpperCase()}
                      </p>

                      <strong className="text-muted">Data:</strong>
                      <p className="mb-2">
                        {resultado.entidades.data?.length > 0
                          ? resultado.entidades.data.join(', ')
                          : 'Não mencionada'}
                      </p>

                      <strong className="text-muted">Horário:</strong>
                      <p className="mb-0">
                        {new Date(resultado.timestamp).toLocaleString('pt-BR')}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home