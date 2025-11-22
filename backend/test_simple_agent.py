"""
Test script for SimpleAgent - Testing procurement fraud detection
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.agents.simple_agent import SimpleAgent


def test_simple_agent():
    """Test the SimpleAgent with procurement fraud detection scenarios."""

    print("=" * 80)
    print("TESTING SIMPLE AGENT - PROCUREMENT FRAUD DETECTION")
    print("=" * 80)

    # Initialize the agent
    print("\n[1/4] Initializing SimpleAgent...")
    agent = SimpleAgent()
    print("✓ Agent initialized successfully")

    # Test cases with suspicious procurement scenarios
    test_cases = [
        {
            "title": "Single Bidder + Short Publication",
            "request": """
            Analizar licitación ID-2024-5678:
            - Solo 1 oferente (procedimiento competitivo)
            - Período de publicación: 3 días
            - Monto: $500.000.000 CLP
            - Tipo: Licitación Pública (LP)
            """
        },
        {
            "title": "High Concentration + New Company",
            "request": """
            Revisar licitación adjudicada a Constructora XYZ:
            - Empresa ganadora tiene 90 días de antigüedad
            - Ha ganado 8 de 10 licitaciones del mismo comprador (80%)
            - Monto adjudicado: $1.200.000.000 CLP
            - Precio ofertado: 98% del presupuesto estimado
            """
        },
        {
            "title": "Suspicious Disqualifications",
            "request": """
            Evaluar licitación ID-2024-9012:
            - 5 empresas presentaron ofertas
            - 4 empresas descalificadas por "errores administrativos menores"
            - Única empresa calificada: proveedor recurrente del organismo
            - Período de publicación: 6 días (mínimo legal: 20 días)
            """
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i+1}/{len(test_cases)+1}] Test Case {i}: {test_case['title']}")
        print(f"{'=' * 80}")
        print(f"Scenario:\n{test_case['request'].strip()}")
        print("-" * 80)

        try:
            # Analyze the procurement scenario
            result = agent.run(test_case['request'])

            # Display results
            print(f"\n✓ Analysis completed successfully!")
            print(f"\nDetected Anomalies: {len(result.anomalies)}")
            print("\nRed Flags:")
            for idx, anomaly in enumerate(result.anomalies, 1):
                print(f"  {idx}. {anomaly}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_simple_agent()
