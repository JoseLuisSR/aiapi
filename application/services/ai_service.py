from application.ports.ai_provider_port import AIProviderPort


class AIService:
    def __init__(self, ai_provider: AIProviderPort):
        self.ai_provider = ai_provider

    def generate_content(self, params: dict) -> str:
        return self.ai_provider.generate_content(params)
