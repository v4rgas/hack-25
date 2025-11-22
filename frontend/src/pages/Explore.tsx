import { useEffect, useState } from 'react'
import { EmbeddingAtlas } from "embedding-atlas/react"
import { Coordinator, wasmConnector } from '@uwdata/vgplot'
import { loadParquet } from '@uwdata/mosaic-sql'
import { useTheme } from '../context/ThemeContext'

export function Explore() {
  const { theme } = useTheme()
  const [coordinator, setCoordinator] = useState<Coordinator | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function init() {
      try {
        // Create coordinator and connect to DuckDB-WASM
        const coord = new Coordinator()
        coord.databaseConnector(wasmConnector())

        // Load parquet file into DuckDB
        // Use fetch to get the file URL that works with Vite's dev server
        await coord.exec([
          loadParquet("data", `${window.location.origin}/data/lic_2020-1_umap.parquet`)
        ])

        // Add unique row ID (CodigoExterno has duplicates)
        await coord.exec("ALTER TABLE data ADD COLUMN _row_id INTEGER")
        await coord.exec("UPDATE data SET _row_id = rowid")

        // Add category column based on MontoEstimado ranges
        await coord.exec("ALTER TABLE data ADD COLUMN _category VARCHAR")
        await coord.exec(`
          UPDATE data
          SET _category = CASE
            WHEN MontoEstimado IS NULL THEN 'Unknown'
            WHEN MontoEstimado < 1000000 THEN '< $1M'
            WHEN MontoEstimado < 5000000 THEN '$1M - $5M'
            WHEN MontoEstimado < 10000000 THEN '$5M - $10M'
            WHEN MontoEstimado < 50000000 THEN '$10M - $50M'
            WHEN MontoEstimado < 100000000 THEN '$50M - $100M'
            WHEN MontoEstimado < 500000000 THEN '$100M - $500M'
            ELSE '> $500M'
          END
        `)

        // Get table info to find columns
        const result = await coord.query("DESCRIBE data")
        console.log("Table schema:", result)

        setCoordinator(coord)
        setLoading(false)
      } catch (err) {
        console.error("Failed to initialize:", err)
        setError(err instanceof Error ? err.message : String(err))
        setLoading(false)
      }
    }

    init()
  }, [])

  if (loading) {
    return (
      <div className="app loading-screen">
        <div className="loader"></div>
        <p className="loading-text">Calculando...</p>
      </div>
    )
  }

  if (error) {
    return <div className="app">Error: {error}</div>
  }

  if (!coordinator) {
    return <div className="app">Failed to initialize coordinator</div>
  }

  return (
    <div className="app">
      <EmbeddingAtlas
        coordinator={coordinator}
        colorScheme={theme}
        data={{
          table: "data",
          id: "_row_id",
          projection: { x: "x", y: "y" },
          text: "tender_name"
        }}
        defaultChartsConfig={{
          embedding: {
            type: "embedding",
            title: "Embedding View",
            data: {
              x: "x",
              y: "y",
              category: "_category",
              text: "CodigoExterno"
            }
          },
          override: {
            "sql_predicates": {
              type: "predicates",
              title: "SQL Filters",
              items: [
                {
                  name: "Quick Award (<150 days)",
                  predicate: "date_diff('day', first_activity_date, FechaAdjudicacion) < 150"
                }
              ]
            }
          }
        }}
        chartTheme={{
          scheme: theme,
          categoryColors: () => {
            // Color scale for MontoEstimado ranges (low to high)
            return [
              '#808080', // NULL/Unknown
              '#2ecc71', // < 1M
              '#3498db', // 1M-5M
              '#9b59b6', // 5M-10M
              '#f39c12', // 10M-50M
              '#e67e22', // 50M-100M
              '#e74c3c', // 100M-500M
              '#c0392b'  // > 500M
            ]
          }
        }}
        embeddingViewConfig={{
          autoLabelEnabled: false
        }}
      />
    </div>
  )
}
