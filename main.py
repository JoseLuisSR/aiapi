from aiapi import AIAPIGemini, AIAPIOpenAI


def main():
    print("Hello from aiapi!")


if __name__ == "__main__":
    main()

    model_openai = "gpt-5.2"
    model_gemini = "gemini-2.5-flash"
    prompt = "Search on internet about Jose Luis Sastoque Rey, give a short summary"
    temperature = 0
    top_p = 0.95
    top_k = 20
    params: dict = {
        "model": model_openai,
        "prompt": prompt,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
    }
    # instructions = "You are a coding assistant that talks like a pirate."
    prompt = "Search on internet about Jose Luis Sastoque Rey, give a short summary"
    client_openai = AIAPIOpenAI()
    client_gemini = AIAPIGemini()
    response_openAI = client_openai.generate_content(params)
    params.update({"model": model_gemini})
    response_gemini = client_gemini.generate_content(params)
    print(f"The OpenAI response is: {response_openAI} \n")
    print(f"The Gemini response is: {response_gemini} \n")
