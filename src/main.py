from orchestrator.workflow import LoanWorkflowOrchestrator

def main():
    orchestrator = LoanWorkflowOrchestrator()

    print("\n=== NBFC Loan Assistant ===\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = orchestrator.handle_user_message(user_input)
        print("\nAssistant:", response, "\n")


if __name__ == "__main__":
    main()

