import './TaskCard.css'

interface TaskEvent {
  type: 'log' | 'result' | 'error'
  message: string
  timestamp: string
}

interface TaskResult {
  task_id: number
  task_code: string
  task_name: string
  validation_passed: boolean
  findings_count: number
  investigation_summary?: string
}

interface TaskCardProps {
  taskCode: string
  taskId: number
  taskName: string
  severity: string
  events: TaskEvent[]
  result?: TaskResult
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
}

export function TaskCard({
  taskCode,
  taskId,
  taskName,
  severity,
  events,
  result,
  status,
}: TaskCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'var(--text-secondary)'
      case 'in_progress':
        return 'var(--accent-primary)'
      case 'completed':
        return '#27ae60'
      case 'failed':
        return '#e74c3c'
      default:
        return 'var(--text-secondary)'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pendiente'
      case 'in_progress':
        return 'En Progreso'
      case 'completed':
        return 'Completado'
      case 'failed':
        return 'Fallido'
      default:
        return 'Desconocido'
    }
  }

  const getSeverityColor = () => {
    switch (severity) {
      case 'Crítico':
      case 'Muy Alto':
        return '#e74c3c'
      case 'Alto':
        return '#e67e22'
      case 'Medio':
        return '#f39c12'
      case 'Bajo':
        return '#27ae60'
      default:
        return 'var(--text-secondary)'
    }
  }

  return (
    <div className="task-card">
      <div className="task-card-header">
        <div className="task-card-title">
          <span className="task-code">{taskCode}</span>
          <span className="task-severity" style={{ color: getSeverityColor() }}>
            {severity}
          </span>
        </div>
        <div className="task-card-status" style={{ color: getStatusColor() }}>
          <span className="status-dot" style={{ backgroundColor: getStatusColor() }}></span>
          {getStatusText()}
        </div>
      </div>
      
      <div className="task-card-name">{taskName}</div>
      
      {events.length > 0 && (
        <div className="task-card-events">
          <div className="task-card-events-header">
            Eventos ({events.length})
          </div>
          <div className="task-card-events-list">
            {events.map((event, index) => (
              <div key={index} className={`task-event task-event-${event.type}`}>
                <span className="task-event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                <span className="task-event-message">{event.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result && (
        <div className="task-card-result">
          <div className={`task-result-status ${result.validation_passed ? 'passed' : 'failed'}`}>
            {result.validation_passed ? '✓ APROBADO' : '✗ FALLADO'}
          </div>
          <div className="task-result-findings">
            Hallazgos: {result.findings_count}
          </div>
          {result.investigation_summary && (
            <div className="task-result-summary">
              {result.investigation_summary}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

