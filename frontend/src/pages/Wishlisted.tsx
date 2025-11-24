import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { endpoints } from '../config/api'
import './Wishlisted.css'

interface WishlistEntry {
  id: number
  email: string
  reason: string
  created_at: string
}

export function Wishlisted() {
  const navigate = useNavigate()
  const [apiKey, setApiKey] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [entries, setEntries] = useState<WishlistEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(endpoints.wishlist, {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Invalid API key')
        }
        throw new Error('Error fetching wishlist entries')
      }

      const data = await response.json()
      setEntries(data)
      setIsAuthenticated(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      console.error('Error fetching wishlist:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (!isAuthenticated) {
    return (
      <div className="wishlisted-container">
        <button onClick={() => navigate('/')} className="back-button">
          ← Volver
        </button>
        <div className="wishlisted-content">
          <h1 className="wishlisted-title">Wishlist Admin</h1>
          <form onSubmit={handleSubmit} className="api-key-form">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API key"
              required
              disabled={loading}
            />
            {error && <div className="error-message">{error}</div>}
            <button type="submit" disabled={loading}>
              {loading ? 'Loading...' : 'Access'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="wishlisted-container">
      <button onClick={() => navigate('/')} className="back-button">
        ← Volver
      </button>
      <div className="wishlisted-content">
        <div className="header">
          <h1 className="wishlisted-title">Wishlist ({entries.length})</h1>
          <button
            onClick={() => {
              setIsAuthenticated(false)
              setApiKey('')
              setEntries([])
            }}
            className="logout-button"
          >
            Logout
          </button>
        </div>
        {entries.length === 0 ? (
          <p className="no-entries">No entries</p>
        ) : (
          <table className="wishlist-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Reason</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.id}</td>
                  <td>{entry.email}</td>
                  <td>{entry.reason}</td>
                  <td>{formatDate(entry.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
