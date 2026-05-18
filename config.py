from dotenv import dotenv_values


class Config:
    ENVIRONMENT_FILE_NAME = ".env"

    OPENAI_API_KEY = "OPENAI_API_KEY"

    GEMINI_API_KEY = "GEMINI_API_KEY"

    @staticmethod
    def load_api_key() -> dict:
        config = dotenv_values(Config.ENVIRONMENT_FILE_NAME)
        return config
