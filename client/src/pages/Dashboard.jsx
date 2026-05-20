import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    porCategoria: {},
    porUrgencia: { alta: 0, media: 0, baixa: 0 }
  })
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/metricas`)
      setStats(response.data)
    } catch (err) {
      setErro('Não foi possível carregar as métricas.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container text-center py-5">
        <div className="spinner-border text-primary" role="status" />
        <p className="mt-3 text-muted">Carregando métricas...</p>
      </div>
    )
  }

  return (
    <div className="container">
      <h2 className="mb-4">Dashboard de Métricas</h2>

      {erro && (
        <div className="alert alert-info">
          {erro} Exibindo métricas vazias.
        </div>
      )}

      <div className="row g-4 mb-4">
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body text-center">
              <h3 className="display-4 text-primary">{stats.total}</h3>
              <p className="text-muted mb-0">Total de Reclamações</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body text-center">
              <h3 className="display-4 text-warning">{stats.porUrgencia?.alta || 0}</h3>
              <p className="text-muted mb-0">Urgência Alta</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body text-center">
              <h3 className="display-4 text-success">{stats.porUrgencia?.media || 0}</h3>
              <p className="text-muted mb-0">Urgência Média</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Reclamações por Categoria</h5>
        </div>
        <div className="card-body">
          {Object.keys(stats.porCategoria || {}).length > 0 ? (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Categoria</th>
                    <th className="text-center">Quantidade</th>
                    <th className="text-center">Percentual</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(stats.porCategoria).map(([categoria, quantidade]) => (
                    <tr key={categoria}>
                      <td>{categoria}</td>
                      <td className="text-center">{quantidade}</td>
                      <td className="text-center">
                        {((quantidade / stats.total) * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted text-center mb-0">
              Nenhum dado disponível ainda.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard