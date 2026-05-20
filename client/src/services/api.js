import axios from 'axios'
import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || ''

async function enviarReclamacao(texto) {
  const response = await axios.post(`${API_URL}/api/triagem`, { texto })
  return response.data
}

export { enviarReclamacao }