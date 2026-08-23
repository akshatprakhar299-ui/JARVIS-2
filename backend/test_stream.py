from services.llm import generate_stream


messages = [
    {
        "role": "user",
        "content": "Explain artificial intelligence in simple terms."
    }
]


print("\nJARVIS:\n")


for chunk in generate_stream(messages):

    print(
        chunk,
        end="",
        flush=True
    )


print("\n")