import { useState, useEffect } from 'react'
import { Zap, BarChart3, Search, Building2, User, Clock, FileEdit, Trophy, ChevronLeft, ChevronRight } from 'lucide-react'
import './App.css'

interface Tender {
  id: string
  name: string
  organization: string
  amount: number
  date: string
  flags: string[]
}

interface Flag {
  id: string
  label: string
  description: string
  active: boolean
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

function App() {
  const [step, setStep] = useState<'overview' | 'filter' | 'select'>('overview')
  const [totalTenders, setTotalTenders] = useState<number | null>(null)
  const [tenders, setTenders] = useState<Tender[]>([])
  const [filteredCount, setFilteredCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [selectedTender, setSelectedTender] = useState<Tender | null>(null)

  const [flags, setFlags] = useState<Flag[]>([
    {
      id: 'new_company',
      label: 'Empresa reciente',
      description: 'Empresa constituida menos de 30 dias antes de la licitacion',
      active: false
    },
    {
      id: 'single_bidder',
      label: 'Oferente unico',
      description: 'Solo una empresa presento oferta',
      active: false
    },
    {
      id: 'price_anomaly',
      label: 'Precio anomalo',
      description: 'Precio significativamente diferente al estimado',
      active: false
    },
    {
      id: 'short_deadline',
      label: 'Plazo reducido',
      description: 'Tiempo de presentacion menor a 5 dias',
      active: false
    },
    {
      id: 'modified_specs',
      label: 'Bases modificadas',
      description: 'Especificaciones tecnicas modificadas durante el proceso',
      active: false
    },
    {
      id: 'same_winner',
      label: 'Ganador recurrente',
      description: 'Mismo proveedor gano multiples licitaciones similares',
      active: false
    }
  ])

  const flagIcons: Record<string, React.ReactNode> = {
    new_company: <Building2 size={16} />,
    single_bidder: <User size={16} />,
    price_anomaly: <BarChart3 size={16} />,
    short_deadline: <Clock size={16} />,
    modified_specs: <FileEdit size={16} />,
    same_winner: <Trophy size={16} />
  }

  useEffect(() => {
    fetchTotalTenders()
  }, [])

  // Transform backend tender to frontend format
  const transformTender = (backendTender: any): Tender => {
    // Extract buyer organization from parties JSON
    let organization = 'Organización no especificada'
    let amount = 0

    if (backendTender.parties && Array.isArray(backendTender.parties)) {
      const buyer = backendTender.parties.find((p: any) =>
        p.roles && p.roles.includes('buyer')
      )
      if (buyer && buyer.name) {
        organization = buyer.name
      }

      // Get amount from supplier/tenderer if available
      const supplier = backendTender.parties.find((p: any) =>
        p.roles && (p.roles.includes('supplier') || p.roles.includes('tenderer'))
      )
      if (supplier && supplier.value && supplier.value.amount) {
        amount = supplier.value.amount
      }
    }

    return {
      id: String(backendTender.id),
      name: backendTender.title || 'Sin título',
      organization,
      amount,
      date: backendTender.published_date ?
        new Date(backendTender.published_date).toISOString().split('T')[0] : '',
      flags: [] // Backend doesn't have flags yet
    }
  }

  const fetchTotalTenders = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/tenders`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setTotalTenders(data.total || 0)
    } catch (error) {
      console.error('Error fetching tenders:', error)
      setTotalTenders(null)
    }
    setLoading(false)
  }

  const toggleFlag = (id: string) => {
    setFlags(flags.map(f =>
      f.id === id ? { ...f, active: !f.active } : f
    ))
  }

  const applyFilters = async () => {
    setLoading(true)
    // Note: Backend doesn't support flag filtering yet, fetching all tenders
    try {
      const res = await fetch(`${API_URL}/api/tenders?limit=100`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()

      const transformedTenders = (data.tenders || []).map(transformTender)
      setTenders(transformedTenders)
      setFilteredCount(data.total || transformedTenders.length)
    } catch (error) {
      console.error('Error filtering tenders:', error)
      setTenders([])
      setFilteredCount(0)
    }
    setLoading(false)
    setStep('select')
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount)
  }

  const startAnalysis = (tender: Tender) => {
    setSelectedTender(tender)
    // Here you would navigate to analysis view
    alert(`Iniciando análisis de: ${tender.name}`)
  }

  const activeCount = flags.filter(f => f.active).length

  return (
    <div className="app">
      <header className="header">
        <h1 className="logo" onClick={() => setStep('overview')} style={{ cursor: 'pointer' }}>
          Themis
        </h1>
        <div className="steps">
          <span className={`step ${step === 'overview' ? 'active' : ''}`}>1. Vista general</span>
          <span className="step-arrow"><ChevronRight size={14} /></span>
          <span className={`step ${step === 'filter' ? 'active' : ''}`}>2. Filtrar</span>
          <span className="step-arrow"><ChevronRight size={14} /></span>
          <span className={`step ${step === 'select' ? 'active' : ''}`}>3. Analizar</span>
        </div>
      </header>

      <main className="main">
        {step === 'overview' && (
          <section className="overview">
            <div className="stat-card">
              <span className="stat-label">Licitaciones en base de datos</span>
              <span className="stat-value">
                {loading ? '...' : totalTenders?.toLocaleString('es-CL')}
              </span>
            </div>
            <p className="overview-text">
              Analiza irregularidades en procesos de licitacion publica usando inteligencia artificial
            </p>
            <button className="cta-button" onClick={() => setStep('filter')}>
              Comenzar filtrado
            </button>
          </section>
        )}

        {step === 'filter' && (
          <section className="filter">
            <h2>Selecciona indicadores de riesgo</h2>
            <p className="filter-subtitle">
              Filtra licitaciones por criterios sospechosos
            </p>

            <div className="flags-grid">
              {flags.map(flag => (
                <div
                  key={flag.id}
                  className={`flag-card ${flag.active ? 'active' : ''}`}
                  onClick={() => toggleFlag(flag.id)}
                >
                  <div className="flag-header">
                    <span className="flag-icon">{flagIcons[flag.id]}</span>
                    <span className="flag-label">{flag.label}</span>
                  </div>
                  <p className="flag-description">{flag.description}</p>
                </div>
              ))}
            </div>

            <div className="filter-actions">
              <span className="filter-count">
                {activeCount} {activeCount === 1 ? 'filtro seleccionado' : 'filtros seleccionados'}
              </span>
              <button
                className="cta-button"
                onClick={applyFilters}
                disabled={activeCount === 0}
              >
                {loading ? 'Buscando...' : 'Aplicar filtros'}
              </button>
            </div>
          </section>
        )}

        {step === 'select' && (
          <section className="select">
            <div className="select-header">
              <h2>Licitaciones flaggeadas</h2>
              <span className="result-count">{filteredCount} resultados</span>
            </div>

            <div className="tenders-list">
              {tenders.map(tender => (
                <div key={tender.id} className="tender-card">
                  <div className="tender-main">
                    <h3 className="tender-name">{tender.name}</h3>
                    <p className="tender-org">{tender.organization}</p>
                    <div className="tender-meta">
                      <span className="tender-amount">{formatCurrency(tender.amount)}</span>
                      <span className="tender-date">{tender.date}</span>
                    </div>
                  </div>
                  <div className="tender-flags">
                    {tender.flags.map(flagId => {
                      const flag = flags.find(f => f.id === flagId)
                      return flag ? (
                        <span key={flagId} className="tender-flag">{flag.label}</span>
                      ) : null
                    })}
                  </div>
                  <button
                    className="analyze-button"
                    onClick={() => startAnalysis(tender)}
                  >
                    Analizar
                  </button>
                </div>
              ))}
            </div>

            <div className="pagination">
              <button
                className="page-button"
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                <ChevronLeft size={16} /> Anterior
              </button>
              <span className="page-info">Pagina {page}</span>
              <button
                className="page-button"
                onClick={() => setPage(p => p + 1)}
              >
                Siguiente <ChevronRight size={16} />
              </button>
            </div>

            <button className="back-button" onClick={() => setStep('filter')}>
              <ChevronLeft size={14} /> Modificar filtros
            </button>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Themis — Vigilancia ciudadana con IA</p>
      </footer>
    </div>
  )
}

export default App
