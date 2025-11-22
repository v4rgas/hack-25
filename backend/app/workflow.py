"""
LangGraph Workflow for Fraud Detection - Orchestrates ranking and parallel investigation
"""
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Send, Command
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.ranking_agent import RankingAgent
from app.agents.fraud_detection_agent import FraudDetectionAgent
from app.schemas import (
    RankingInput,
    RankingOutput,
    RankedItem,
    FraudDetectionInput,
    FraudDetectionOutput,
    Anomaly
)


class WorkflowState(TypedDict):
    """State definition for the fraud detection workflow"""
    # Input data
    input_data: RankingInput

    # Ranking results
    ranked_items: List[RankedItem]
    ranking_summary: str

    # Investigation results (accumulated from parallel processing)
    investigation_results: Annotated[List[FraudDetectionOutput], add_messages]

    # Final output
    confirmed_fraud_cases: List[FraudDetectionOutput]
    workflow_summary: str

    # Error tracking
    errors: List[str]


class FraudDetectionWorkflow:
    """
    LangGraph workflow that coordinates fraud detection through ranking and parallel investigation.

    Workflow structure:
    1. Entry Node: RankingAgent analyzes tender and produces top 5 risk items
    2. Command & Send: Launches 5 parallel FraudDetectionAgents
    3. Investigation Nodes: Each agent investigates one tender in parallel
    4. Aggregation Node: Collects results and filters confirmed fraud cases
    5. Output: Returns all confirmed fraud cases with detailed anomalies

    Usage:
        workflow = FraudDetectionWorkflow()
        input_data = RankingInput(
            tender_id="1234-56-LR22",
            tender_name="IT Services",
            tender_date="2024-01-15",
            bases="General requirements...",
            bases_tecnicas="Technical specs..."
        )
        result = workflow.run(input_data)
        for case in result["confirmed_fraud_cases"]:
            print(f"Fraud detected in {case.tender_id}")
    """

    def __init__(
        self,
        ranking_model: str = "claude-haiku-4-5",
        detection_model: str = "claude-haiku-4-5",
        temperature: float = 0.7
    ):
        """
        Initialize the workflow with agent configurations.

        Args:
            ranking_model: Model for ranking agent
            detection_model: Model for detection agents
            temperature: Temperature for all agents
        """
        self.ranking_agent = RankingAgent(
            model_name=ranking_model,
            temperature=temperature
        )
        self.detection_model = detection_model
        self.temperature = temperature

        # Build the workflow graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow graph"""

        # Create the graph with state schema
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("ranking_node", self._ranking_node)
        graph.add_node("distribute_investigations", self._distribute_investigations)
        graph.add_node("investigate_tender", self._investigate_tender)
        graph.add_node("aggregate_results", self._aggregate_results)

        # Add edges
        graph.add_edge(START, "ranking_node")
        graph.add_edge("ranking_node", "distribute_investigations")
        graph.add_edge("distribute_investigations", "aggregate_results")
        graph.add_edge("aggregate_results", END)

        return graph

    def _ranking_node(self, state: WorkflowState) -> WorkflowState:
        """
        Entry node that runs the ranking agent.

        Analyzes tender context and produces ranked items by fraud risk.
        """
        print("Starting ranking analysis...")

        try:
            # Run ranking agent
            ranking_result: RankingOutput = self.ranking_agent.run(state["input_data"])

            # Update state with ranking results
            state["ranked_items"] = ranking_result.ranked_items[:5]  # Top 5 only
            state["ranking_summary"] = ranking_result.analysis_summary

            print(f"Ranking complete. Found {len(state['ranked_items'])} high-risk items.")

        except Exception as e:
            print(f"Ranking failed: {e}")
            state["errors"].append(f"Ranking error: {str(e)}")
            state["ranked_items"] = []
            state["ranking_summary"] = "Ranking failed"

        return state

    def _distribute_investigations(self, state: WorkflowState) -> Command:
        """
        Distribution node using Command and Send pattern.

        Launches parallel fraud detection agents for each ranked item.
        """
        print(f"Launching {len(state['ranked_items'])} parallel investigations...")

        # Create Send commands for each ranked item
        send_commands = []

        for idx, ranked_item in enumerate(state["ranked_items"]):
            # Prepare input for fraud detection agent
            detection_input = {
                "tender_id": ranked_item.tender_id,
                "risk_indicators": ranked_item.risk_indicators,
                "full_context": ranked_item.full_context,
                "investigation_id": f"inv_{idx}_{uuid.uuid4().hex[:8]}"
            }

            # Create Send command to investigate_tender node
            send_commands.append(
                Send(
                    "investigate_tender",
                    detection_input
                )
            )

        # Return Command with all Send operations
        return Command(
            goto=send_commands,
            update=state
        )

    def _investigate_tender(self, inputs: Dict[str, Any]) -> FraudDetectionOutput:
        """
        Investigation node that runs fraud detection on a single tender.

        This node is called in parallel for each tender.
        """
        investigation_id = inputs.get("investigation_id", "unknown")
        print(f"Investigation {investigation_id} starting for tender {inputs['tender_id']}...")

        try:
            # Create fraud detection agent
            agent = FraudDetectionAgent(
                model_name=self.detection_model,
                temperature=self.temperature
            )

            # Prepare input
            detection_input = FraudDetectionInput(
                tender_id=inputs["tender_id"],
                risk_indicators=inputs["risk_indicators"],
                full_context=inputs["full_context"]
            )

            # Run investigation
            result = agent.run(detection_input)

            print(f"Investigation {investigation_id} complete. Fraud detected: {result.is_fraudulent}")

            return result

        except Exception as e:
            print(f"Investigation {investigation_id} failed: {e}")
            # Return error result
            return FraudDetectionOutput(
                tender_id=inputs["tender_id"],
                is_fraudulent=False,
                anomalies=[],
                investigation_summary=f"Investigation failed: {str(e)}"
            )

    def _aggregate_results(self, state: WorkflowState) -> WorkflowState:
        """
        Aggregation node that collects all investigation results.

        Filters and organizes confirmed fraud cases.
        """
        print(f"Aggregating {len(state.get('investigation_results', []))} investigation results...")

        # Filter for confirmed fraud cases
        confirmed_cases = [
            result for result in state.get("investigation_results", [])
            if result.is_fraudulent
        ]

        state["confirmed_fraud_cases"] = confirmed_cases

        # Generate workflow summary
        total_investigated = len(state.get("investigation_results", []))
        total_fraud = len(confirmed_cases)

        if total_fraud > 0:
            anomaly_summary = []
            for case in confirmed_cases:
                anomaly_count = len(case.anomalies)
                high_confidence = sum(1 for a in case.anomalies if a.confidence >= 0.8)
                anomaly_summary.append(
                    f"  - {case.tender_id}: {anomaly_count} anomalies ({high_confidence} high confidence)"
                )

            state["workflow_summary"] = f"""
Fraud Detection Workflow Complete:
- Tenders investigated: {total_investigated}
- Fraud cases detected: {total_fraud}

Confirmed fraud cases:
{chr(10).join(anomaly_summary)}
"""
        else:
            state["workflow_summary"] = f"""
Fraud Detection Workflow Complete:
- Tenders investigated: {total_investigated}
- Fraud cases detected: 0
- No significant fraud indicators found in the analyzed tenders.
"""

        print(f"Workflow complete. Found {total_fraud} fraud cases.")
        print(state["workflow_summary"])

        return state

    def run(self, input_data: RankingInput) -> Dict[str, Any]:
        """
        Execute the fraud detection workflow.

        Args:
            input_data: RankingInput with tender context

        Returns:
            Dict containing:
            - confirmed_fraud_cases: List of FraudDetectionOutput for fraudulent tenders
            - workflow_summary: Summary of the investigation
            - all results from state
        """
        # Initialize state
        initial_state: WorkflowState = {
            "input_data": input_data,
            "ranked_items": [],
            "ranking_summary": "",
            "investigation_results": [],
            "confirmed_fraud_cases": [],
            "workflow_summary": "",
            "errors": []
        }

        # Run the workflow
        result = self.app.invoke(initial_state)

        return result

    def stream(self, input_data: RankingInput):
        """
        Stream workflow execution for real-time monitoring.

        Args:
            input_data: RankingInput with tender context

        Yields:
            State updates as the workflow progresses
        """
        # Initialize state
        initial_state: WorkflowState = {
            "input_data": input_data,
            "ranked_items": [],
            "ranking_summary": "",
            "investigation_results": [],
            "confirmed_fraud_cases": [],
            "workflow_summary": "",
            "errors": []
        }

        # Stream the workflow execution
        for state in self.app.stream(initial_state):
            yield state


# Convenience function for quick execution
def detect_fraud(
    tender_id: str,
    tender_name: str,
    tender_date: str,
    bases: str,
    bases_tecnicas: str,
    additional_context: Dict[str, Any] = None
) -> List[FraudDetectionOutput]:
    """
    Convenience function to run fraud detection on a tender.

    Args:
        tender_id: Tender identifier
        tender_name: Name of the tender
        tender_date: Date of the tender
        bases: General requirements
        bases_tecnicas: Technical specifications
        additional_context: Additional context data

    Returns:
        List of confirmed fraud cases with anomalies
    """
    workflow = FraudDetectionWorkflow()

    input_data = RankingInput(
        tender_id=tender_id,
        tender_name=tender_name,
        tender_date=tender_date,
        bases=bases,
        bases_tecnicas=bases_tecnicas,
        additional_context=additional_context or {}
    )

    result = workflow.run(input_data)

    return result["confirmed_fraud_cases"]