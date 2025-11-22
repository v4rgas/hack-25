import { Link } from 'react-router-dom'
import './Landing.css'

export function Landing() {
  return (
    <div className="landing">
      <div className="landing-content">
        <div className="logo">
          <div className="logo-t">
            <div className="t-horizontal"></div>
            <div className="t-vertical"></div>
            <span className="dot dot-left"></span>
            <span className="dot dot-right"></span>
            <span className="dot dot-center"></span>
            <span className="dot dot-bottom"></span>
          </div>
        </div>
        <h1 className="title">Themis</h1>
        <p className="tagline">
          Sistema automatizado de exploración y auditoría de licitaciones públicas sospechosas o que incumplen normativas
        </p>
        <Link to="/explore" className="cta-button">
          Explorar Licitaciones
        </Link>
      </div>
    </div>
  )
}
