from application.ports.ai_provider_port import AIProviderPort


class AIService:
    def __init__(self, ai_provider: AIProviderPort):
        self.ai_provider = ai_provider

    def generate_content(self, params: dict) -> str:
        response = self.ai_provider.generate_content(params)
        self.ai_provider.close_client()
        return response
