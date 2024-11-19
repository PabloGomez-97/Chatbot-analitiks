import openai

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente de ventas que ayuda a resolver dudas de dispositivos de medición."},
            {"role": "user", "content": question}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()