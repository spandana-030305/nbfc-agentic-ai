"""
Loan Workflow Orchestrator
Coordinates all worker agents in the loan approval process
"""

from agents.sales_agent import sales_agent_task
from agents.kyc_agent import kyc_agent_task
from agents.crm_agent import crm_agent_task
from agents.income_agent import income_agent_task
from agents.compliance_agent import compliance_agent_task
from agents.underwriting_agent import UnderwritingAgent
from agents.pricing_agent import PricingAgent
from agents.sanction_letter_agent import SanctionLetterAgent
from agents.esign_agent import esign_agent_task
from agents.disbursement_agent import disbursement_agent_task
from utils.memory import get_shared_memory
from typing import Dict, Any, Optional


class LoanWorkflowOrchestrator:
    """
    Master orchestrator for loan workflow.
    Manages transitions between stages and coordinates worker agents.
    """

    def __init__(self):
        self.memory = get_shared_memory()
        self.workflow_stages = [
            "INITIAL_GREETING",
            "LOAN_NEGOTIATION",
            "KYC_VERIFICATION",
            "CRM_VERIFICATION",
            "INCOME_VERIFICATION",
            "COMPLIANCE_CHECK",
            "UNDERWRITING_REVIEW",
            "PRICING_CALCULATION",
            "DOCUMENT_PREPARATION",
            "DIGITAL_SIGNATURE",
            "FUND_DISBURSEMENT",
            "COMPLETION"
        ]
        self.current_stage = 0

    def process_user_message(self, customer_id: str, message: str) -> Dict[str, Any]:
        """
        Main entry point for processing customer messages.
        Routes to appropriate workflow stage.
        """
        # Store message in memory
        self.memory.add_message("user", message)

        # Intent detection
        intent = self._detect_intent(message)

        # Route to appropriate handler
        if intent == "start_loan":
            return self._handle_loan_start()

        elif intent == "kyc":
            return self._handle_kyc_verification(customer_id)

        elif intent == "crm":
            return self._handle_crm_verification(customer_id)

        elif intent == "income":
            return self._handle_income_verification(customer_id)

        elif intent == "underwriting":
            return self._handle_underwriting(customer_id)

        elif intent == "pricing":
            return self._handle_pricing(customer_id)

        elif intent == "sign":
            return self._handle_digital_signature(customer_id)

        elif intent == "disburse":
            return self._handle_disbursement(customer_id)

        else:
            return {"reply": "How can I help you with your loan application today?"}

    def execute_full_workflow(self, customer_id: str) -> Dict[str, Any]:
        """
        Execute complete loan workflow from verification to disbursement
        """
        workflow_results = {}

        try:
            # Stage 1: KYC Verification
            kyc_result = self._handle_kyc_verification(customer_id)
            workflow_results["kyc"] = kyc_result
            if not kyc_result.get("success"):
                return {"status": "REJECTED", "reason": "KYC verification failed", "details": workflow_results}

            # Stage 2: CRM Verification
            crm_result = self._handle_crm_verification(customer_id)
            workflow_results["crm"] = crm_result
            if not crm_result.get("success"):
                return {"status": "REJECTED", "reason": "CRM verification failed", "details": workflow_results}

            # Stage 3: Income Verification
            income_result = self._handle_income_verification(customer_id)
            workflow_results["income"] = income_result
            if not income_result.get("success"):
                return {"status": "REJECTED", "reason": "Income verification failed", "details": workflow_results}

            # Stage 4: Compliance Check
            compliance_result = self._handle_compliance_check(customer_id)
            workflow_results["compliance"] = compliance_result
            if not compliance_result.get("success"):
                return {"status": "REJECTED", "reason": "Compliance check failed", "details": workflow_results}

            # Stage 5: Underwriting
            underwriting_result = self._handle_underwriting(customer_id)
            workflow_results["underwriting"] = underwriting_result
            if underwriting_result.get("decision") != "APPROVED":
                return {"status": "REJECTED", "reason": "Underwriting not approved", "details": workflow_results}

            # Stage 6: Pricing
            pricing_result = self._handle_pricing(customer_id)
            workflow_results["pricing"] = pricing_result
            if not pricing_result.get("success"):
                return {"status": "REJECTED", "reason": "Pricing calculation failed", "details": workflow_results}

            # Stage 7: Digital Signature
            signature_result = self._handle_digital_signature(customer_id)
            workflow_results["signature"] = signature_result
            if signature_result.get("status") != "SIGNED":
                return {"status": "REJECTED", "reason": "Digital signature failed", "details": workflow_results}

            # Stage 8: Disbursement
            disbursement_result = self._handle_disbursement(customer_id)
            workflow_results["disbursement"] = disbursement_result
            if disbursement_result.get("status") != "SUCCESS":
                return {"status": "PENDING", "reason": "Disbursement processing", "details": workflow_results}

            # Update memory
            self.memory.update_workflow_state("sanction_generated", True)

            return {
                "status": "APPROVED_AND_DISBURSED",
                "message": "Loan approval and disbursement completed successfully!",
                "details": workflow_results
            }

        except Exception as e:
            return {"status": "ERROR", "error": str(e), "details": workflow_results}

    def _handle_loan_start(self) -> Dict[str, Any]:
        """Handle loan negotiation start"""
        reply = "Great! I'd love to help you get a personal loan. Can you tell me what amount you're looking for and what you'll use it for?"
        self.memory.add_message("bot", reply, agent_name="sales")
        return {"success": True, "reply": reply}

    def _handle_kyc_verification(self, customer_id: str) -> Dict[str, Any]:
        """Handle KYC verification"""
        result = kyc_agent_task(
            pan="AAAPA1234A",
            name="Test User",
            dob="1995-01-15"
        )
        self.memory.update_workflow_state("kyc_verified", result.get("kyc_status") == "VERIFIED")
        self.memory.store_agent_result("kyc_agent", result)
        return {
            "success": result.get("kyc_status") == "VERIFIED",
            "result": result
        }

    def _handle_crm_verification(self, customer_id: str) -> Dict[str, Any]:
        """Handle CRM verification (phone, address)"""
        result = crm_agent_task(customer_id)
        success = result.get("crm_status") == "VERIFIED"
        self.memory.update_workflow_state("crm_verified", success)
        self.memory.store_agent_result("crm_agent", result)
        if success:
            self.memory.set_customer_profile({
                "phone": result.get("phone"),
                "address": result.get("address"),
                "city": result.get("city")
            })
        return {"success": success, "result": result}

    def _handle_income_verification(self, customer_id: str) -> Dict[str, Any]:
        """Handle income verification"""
        result = income_agent_task(customer_id)
        success = result.get("income_status") == "VERIFIED"
        self.memory.update_workflow_state("income_verified", success)
        self.memory.store_agent_result("income_agent", result)
        return {"success": success, "result": result}

    def _handle_compliance_check(self, customer_id: str) -> Dict[str, Any]:
        """Handle compliance check"""
        result = compliance_agent_task(customer_id)
        success = result.get("compliance_status") == "APPROVED"
        self.memory.update_workflow_state("compliance_passed", success)
        self.memory.store_agent_result("compliance_agent", result)
        return {"success": success, "result": result}

    def _handle_underwriting(self, customer_id: str) -> Dict[str, Any]:
        """Handle underwriting evaluation"""
        # This would be called with actual loan amount from negotiation
        result = {
            "decision": "APPROVED",
            "credit_score": 750,
            "remarks": "Loan approved"
        }
        self.memory.update_workflow_state("underwriting_decision", result.get("decision"))
        self.memory.store_agent_result("underwriting_agent", result)
        return result

    def _handle_pricing(self, customer_id: str) -> Dict[str, Any]:
        """Handle pricing calculation"""
        result = {
            "pricing_status": "APPROVED",
            "interest_rate": 12.5,
            "eligible_loan_amount": 200000,
            "tenure_months": 60,
            "estimated_emi": 4500,
            "remarks": "Pricing approved"
        }
        self.memory.update_workflow_state("pricing_approved", result.get("pricing_status") == "APPROVED")
        self.memory.store_agent_result("pricing_agent", result)
        return {"success": result.get("pricing_status") == "APPROVED", "result": result}

    def _handle_digital_signature(self, customer_id: str) -> Dict[str, Any]:
        """Handle digital signature of documents"""
        result = esign_agent_task(
            customer_id=customer_id,
            customer_name="Test User",
            loan_amount=200000,
            sanction_id="SAN-ABC12345"
        )
        self.memory.update_workflow_state("documents_signed", result.get("esign_status") == "SIGNED")
        self.memory.store_agent_result("esign_agent", result)
        return result

    def _handle_disbursement(self, customer_id: str) -> Dict[str, Any]:
        """Handle fund disbursement"""
        result = disbursement_agent_task(
            customer_id=customer_id,
            customer_name="Test User",
            loan_amount=200000,
            sanction_id="SAN-ABC12345",
            signature_id="SIG-XYZ78901"
        )
        self.memory.update_workflow_state("disbursement_completed", result.get("disbursement_status") == "SUCCESS")
        self.memory.store_agent_result("disbursement_agent", result)
        return result

    def _detect_intent(self, msg: str) -> str:
        """Detect user intent from message"""
        msg = msg.lower()

        if any(word in msg for word in ["loan", "personal", "amount", "borrow"]):
            return "start_loan"

        if any(word in msg for word in ["kyc", "verification", "pan", "identity"]):
            return "kyc"

        if any(word in msg for word in ["crm", "phone", "address", "location"]):
            return "crm"

        if any(word in msg for word in ["income", "salary", "bank", "statement"]):
            return "income"

        if any(word in msg for word in ["underwriting", "eligibility", "eligible"]):
            return "underwriting"

        if any(word in msg for word in ["pricing", "rate", "interest", "emi"]):
            return "pricing"

        if any(word in msg for word in ["sign", "signature", "agreement"]):
            return "sign"

        if any(word in msg for word in ["disburse", "money", "transfer", "credit"]):
            return "disburse"

        return "unknown"

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_stage": self.workflow_stages[self.current_stage] if self.current_stage < len(self.workflow_stages) else "UNKNOWN",
            "workflow_state": self.memory.get_workflow_state(),
            "is_complete": self.memory.is_workflow_complete()
        }

