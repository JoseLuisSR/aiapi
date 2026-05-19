from aiapi import AIAPIFactory


def main():
    print("Hello from aiapi!")


if __name__ == "__main__":
    main()

    model_openai = "gpt-5.2"
    model_gemini = "gemini-2.5-flash"
    model_claude = "claude-sonnet-4-6"
    prompt = "Search on internet about Jose Luis Sastoque Rey, give me a short summary"
    temperature = 0
    top_p = 0.95
    top_k = 20
    params: dict = {
        "max_tokens": 1024,
        "model": model_openai,
        "prompt": prompt,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
    }
    # instructions = "You are a coding assistant that talks like a pirate."
    prompt = "Search on internet about Jose Luis Sastoque Rey, give a short summary"
    instance = AIAPIFactory()
    client_openai = instance.create_aiapi(AIAPIFactory.OPENAI_API)
    client_gemini = instance.create_aiapi(AIAPIFactory.GEMINI_API)
    client_claude = instance.create_aiapi(AIAPIFactory.CLAUDE_API)
    response_openAI = client_openai.generate_content(params)
    params.update({"model": model_gemini})
    response_gemini = client_gemini.generate_content(params)
    params.update({"model": model_claude})
    response_claude = client_claude.generate_content(params)
    print(f"The OpenAI response is: {response_openAI} \n")
    # print(f"The Gemini response is: {response_gemini} \n")
    print(f"The Claude response is: {response_claude} \n")
    client_openai.close_client()
    client_gemini.close_client()
    client_claude.close_client()
