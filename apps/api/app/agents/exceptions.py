class AgentError(Exception):
    """Raised when an agent fails after retries."""

    def __init__(self, agent_name: str, message: str, user_message: str | None = None):
        self.agent_name = agent_name
        self.user_message = user_message or (
            "We couldn't generate part of your plan. Please try again in a moment."
        )
        super().__init__(f"{agent_name}: {message}")
