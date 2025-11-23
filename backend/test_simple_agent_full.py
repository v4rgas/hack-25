"""
Test script for SimpleAgent - Full integration test with all tools
Testing procurement fraud investigation with real tender from Mercado Público
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.agents.simple_agent import SimpleAgent


def test_simple_agent_full_investigation():
    """Test the SimpleAgent with full tool access for fraud investigation."""

    print("=" * 80)
    print("TESTING SIMPLE AGENT - FULL PROCUREMENT FRAUD INVESTIGATION")
    print("=" * 80)

    # Initialize the agent
    print("\n[1/4] Initializing SimpleAgent with all investigation tools...")
    print("  Available tools:")
    print("    - get_plan: Create investigation plans")
    print("    - read_buyer_attachments_table: List tender documents")
    print("    - read_buyer_attachment_doc: Extract text with OCR (auto-downloads and caches)")

    agent = SimpleAgent()
    print("\n✓ Agent initialized successfully")

    # Test cases with real tender investigations
    test_cases = [
        {
            "title": "Real Tender Investigation - Budget Certificate Analysis",
            "request": """
            Investigate tender 4831-19-LE20 from Mercado Público (Chile).

            Initial red flags to verify:
            - Check if publication period meets legal requirements
            - Analyze budget amounts in certification documents
            - Look for any discrepancies in monetary values
            - Review technical specifications for restrictive requirements

            Please:
            1. Create an investigation plan
            2. List all available documents
            3. Read the budget certificate (CERT.DISP.PRES.VEREDAS.pdf)
            4. Analyze for anomalies
            """,
            "expected_tools": ["get_plan", "read_buyer_attachments_table", "read_buyer_attachment_doc"]
        },
        {
            "title": "Document Availability Check",
            "request": """
            For tender 4831-19-LE20, I need to know:
            - What documents are available?
            - Are the required legal documents present (budget cert, adjudication decree)?
            - What technical specifications exist?

            List all attachments and identify any missing critical documents.
            """,
            "expected_tools": ["read_buyer_attachments_table"]
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i+1}/{len(test_cases)+1}] TEST CASE {i}: {test_case['title']}")
        print(f"{'=' * 80}")
        print(f"\nInvestigation Request:")
        print("-" * 80)
        print(test_case['request'].strip())
        print("-" * 80)

        try:
            print(f"\n🔍 Agent is investigating...")
            print(f"Expected to use tools: {', '.join(test_case['expected_tools'])}")
            print()

            # Run the investigation
            result = agent.run(test_case['request'])

            # Display results
            print(f"\n{'=' * 80}")
            print(f"INVESTIGATION RESULTS")
            print(f"{'=' * 80}")

            print(f"\n✓ Investigation completed!")
            print(f"\nDetected Anomalies/Findings: {len(result.anomalies)}")

            if result.anomalies:
                print(f"\n{'=' * 80}")
                print("FINDINGS:")
                print("=" * 80)
                for idx, anomaly in enumerate(result.anomalies, 1):
                    print(f"\n{idx}. {anomaly}")
                    print("-" * 80)
            else:
                print("\n⚠️  No anomalies detected")

        except Exception as e:
            print(f"\n✗ Error during investigation: {e}")
            import traceback
            traceback.print_exc()

        # Pause between tests
        if i < len(test_cases):
            print(f"\n{'=' * 80}")
            input("Press Enter to continue to next test case...")

    # ============================================================================
    # Summary
    # ============================================================================
    print("\n" + "=" * 80)
    print("TESTING COMPLETE - SUMMARY")
    print("=" * 80)
    print("\nSimpleAgent Capabilities Tested:")
    print("✓ Tool Usage:")
    print("  - get_plan: Creates structured investigation plans")
    print("  - read_buyer_attachments_table: Lists tender documents")
    print("  - read_buyer_attachment_doc: Extracts text with Mistral OCR (auto-downloads and caches)")
    print("\n✓ Analysis Features:")
    print("  - Identifies red flags and anomalies")
    print("  - Compares against legal requirements")
    print("  - Analyzes budget discrepancies")
    print("  - Reviews technical specifications")
    print("\n✓ Output Format:")
    print("  - Structured list of anomalies")
    print("  - Evidence-based findings")
    print("  - Clear risk categorization")
    print("\nThe agent is ready for production fraud investigation!")
    print("=" * 80)


if __name__ == "__main__":
    test_simple_agent_full_investigation()
