from agents.kyc_agent import KycAgent
from agents.sales_agent import SalesAgent
from agents.pricing_agent import PricingAgent
from agents.underwriting_agent import UnderwritingAgent
from agents.sanction_letter_agent import SanctionLetterAgent
from utils.memory import SharedMemory

class LoanWorkflowOrchestrator:
    def __init__(self):
        self.memory = SharedMemory()
        self.sales_agent = SalesAgent(self.memory)
        self.kyc_agent = KycAgent(self.memory)
        self.pricing_agent = PricingAgent(self.memory)
        self.underwriting_agent = UnderwritingAgent(self.memory)
        self.sanction_agent = SanctionLetterAgent(self.memory)

    def handle_user_message(self, message):
        intent = self._detect_intent(message)

        if intent == "start_loan":
            return self.sales_agent.start_conversation()

        if intent == "kyc":
            return self.kyc_agent.verify_kyc()

        if intent == "underwrite":
            return self.underwriting_agent.process()

        if intent == "pricing":
            return self.pricing_agent.compute_pricing()

        if intent == "sanction":
            return self.sanction_agent.generate_pdf()

        return "I can help you with loan application, KYC, pricing, underwriting or sanction letter."

    def _detect_intent(self, msg):
        msg = msg.lower()

        if "loan" in msg:
            return "start_loan"
        if "kyc" in msg:
            return "kyc"
        if "underwrite" in msg or "eligibility" in msg:
            return "underwrite"
        if "rate" in msg or "emi" in msg:
            return "pricing"
        if "sanction" in msg:
            return "sanction"

        return "unknown"
