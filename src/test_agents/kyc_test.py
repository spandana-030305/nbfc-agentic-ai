from agents.kyc_agent import kyc_agent_task

if __name__ == "__main__":
    result = kyc_agent_task(
        pan="ABCDE1234F",
        name="Sai Spandana",
        dob="2003-05-14"
    )
    print(result)