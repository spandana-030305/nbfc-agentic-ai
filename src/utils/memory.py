"""
Shared Memory System for Master Agent & Worker Agents
Persists conversation context, workflow state, and customer details
across multiple agent interactions
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import os


class SharedMemory:
    """
    Central memory store for conversation context and workflow state.
    Shared across Master Agent and all Worker Agents.
    """

    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.customer_profile: Dict[str, Any] = {}
        self.workflow_state: Dict[str, Any] = {
            "kyc_verified": False,
            "income_verified": False,
            "compliance_passed": False,
            "underwriting_decision": None,
            "pricing_approved": False,
            "sanction_generated": False,
            "salary_slip_uploaded": False,
        }
        self.agent_results: Dict[str, Any] = {}
        self.loan_details: Dict[str, Any] = {}
        self.documents: Dict[str, str] = {}  # Document name -> file path
        self.created_at = datetime.now().isoformat()

    def add_message(self, role: str, content: str, agent_name: Optional[str] = None):
        """Add message to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "agent": agent_name,
            "content": content,
        })

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retrieve full conversation history"""
        return self.conversation_history

    def set_customer_profile(self, customer_data: Dict[str, Any]):
        """Store customer profile information"""
        self.customer_profile = {
            **self.customer_profile,
            **customer_data,
        }

    def get_customer_profile(self) -> Dict[str, Any]:
        """Retrieve customer profile"""
        return self.customer_profile

    def update_workflow_state(self, key: str, value: Any):
        """Update workflow state for a specific step"""
        self.workflow_state[key] = value

    def get_workflow_state(self) -> Dict[str, Any]:
        """Get complete workflow state"""
        return self.workflow_state

    def is_workflow_complete(self) -> bool:
        """Check if entire workflow is complete"""
        return (
            self.workflow_state.get("kyc_verified", False)
            and self.workflow_state.get("income_verified", False)
            and self.workflow_state.get("compliance_passed", False)
            and self.workflow_state.get("underwriting_decision") == "APPROVED"
            and self.workflow_state.get("pricing_approved", False)
            and self.workflow_state.get("sanction_generated", False)
        )

    def store_agent_result(self, agent_name: str, result: Dict[str, Any]):
        """Store result from any agent"""
        self.agent_results[agent_name] = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }

    def get_agent_result(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored agent result"""
        if agent_name in self.agent_results:
            return self.agent_results[agent_name]["result"]
        return None

    def set_loan_details(self, details: Dict[str, Any]):
        """Store negotiated loan details"""
        self.loan_details = {
            **self.loan_details,
            **details,
        }

    def get_loan_details(self) -> Dict[str, Any]:
        """Retrieve loan details"""
        return self.loan_details

    def store_document(self, doc_name: str, file_path: str):
        """Store document reference"""
        self.documents[doc_name] = file_path

    def get_document(self, doc_name: str) -> Optional[str]:
        """Retrieve document file path"""
        return self.documents.get(doc_name)

    def get_all_documents(self) -> Dict[str, str]:
        """Get all stored documents"""
        return self.documents

    def get_context_summary(self) -> str:
        """Generate summary for LLM context"""
        summary = f"""
=== CONVERSATION CONTEXT ===
Customer: {self.customer_profile.get('name', 'N/A')}
Customer ID: {self.customer_profile.get('customer_id', 'N/A')}

=== WORKFLOW STATUS ===
KYC Verified: {self.workflow_state.get('kyc_verified')}
Income Verified: {self.workflow_state.get('income_verified')}
Compliance Passed: {self.workflow_state.get('compliance_passed')}
Underwriting Decision: {self.workflow_state.get('underwriting_decision')}
Pricing Approved: {self.workflow_state.get('pricing_approved')}
Sanction Generated: {self.workflow_state.get('sanction_generated')}
Salary Slip Uploaded: {self.workflow_state.get('salary_slip_uploaded')}

=== LOAN DETAILS ===
{json.dumps(self.loan_details, indent=2)}

=== RECENT CONVERSATION ===
{self._get_recent_messages(5)}
"""
        return summary

    def _get_recent_messages(self, count: int = 5) -> str:
        """Get recent messages for context"""
        recent = self.conversation_history[-count:] if self.conversation_history else []
        return "\n".join(
            [
                f"{msg['role'].upper()}: {msg['content'][:100]}..."
                for msg in recent
            ]
        )

    def reset(self):
        """Reset memory for new conversation"""
        self.conversation_history = []
        self.agent_results = {}
        self.workflow_state = {
            "kyc_verified": False,
            "income_verified": False,
            "compliance_passed": False,
            "underwriting_decision": None,
            "pricing_approved": False,
            "sanction_generated": False,
            "salary_slip_uploaded": False,
        }
        self.loan_details = {}
        self.documents = {}

    def export_session(self) -> Dict[str, Any]:
        """Export full session data"""
        return {
            "created_at": self.created_at,
            "customer": self.customer_profile,
            "workflow": self.workflow_state,
            "loan": self.loan_details,
            "messages": self.conversation_history,
            "agent_results": self.agent_results,
            "documents": self.documents,
        }

    def save_to_file(self, filepath: str):
        """Save session to JSON file"""
        with open(filepath, "w") as f:
            json.dump(self.export_session(), f, indent=2)

    def load_from_file(self, filepath: str):
        """Load session from JSON file"""
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as f:
            data = json.load(f)

        self.customer_profile = data.get("customer", {})
        self.workflow_state = data.get("workflow", {})
        self.loan_details = data.get("loan", {})
        self.conversation_history = data.get("messages", [])
        self.agent_results = data.get("agent_results", {})
        self.documents = data.get("documents", {})

        return True


# Global memory instance (shared across agents)
_shared_memory = None


def get_shared_memory() -> SharedMemory:
    """Get or create global shared memory instance"""
    global _shared_memory
    if _shared_memory is None:
        _shared_memory = SharedMemory()
    return _shared_memory


def reset_shared_memory():
    """Reset shared memory"""
    global _shared_memory
    if _shared_memory:
        _shared_memory.reset()
