from openai import OpenAI

client = OpenAI(api_key="your_api_key_here")

def ai_reply(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful personal AI assistant"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
