import { useEffect, useState } from 'react'
import { EmbeddingAtlas } from "embedding-atlas/react"
import { Coordinator, wasmConnector } from '@uwdata/vgplot'
import { loadParquet } from '@uwdata/mosaic-sql'

export function Explore() {
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
        <p className="loading-text">Estamos procesando los datos solo para ti</p>
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
        data={{
          table: "data",
          id: "_row_id",
          projection: { x: "x", y: "y" },
          text: "CodigoExterno"
        }}
      />
    </div>
  )
}
