import os

from dotenv import load_dotenv

from groq import Groq


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


api_key = os.getenv(
    "GROQ_API_KEY"
)


if not api_key:

    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=api_key
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# JARVIS PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, a personal AI assistant.

Your personality:

- Intelligent
- Helpful
- Calm
- Friendly
- Professional

Rules:

- Give accurate and useful answers.
- Keep answers reasonably concise unless the user asks for detail.
- Explain technical concepts clearly.
- If you don't know something, say so instead of inventing information.
- Do not claim that you performed an action when you did not.

You may receive information about the user from JARVIS's
long-term memory.

Use that information naturally when relevant.

Do not mention the internal memory system unless the user
specifically asks about it.
"""


# ============================================================
# BUILD SYSTEM PROMPT
# ============================================================

def build_system_prompt(memory_context=""):

    system_prompt = SYSTEM_PROMPT

    if memory_context:

        system_prompt += """

The following information is remembered about the user:

""" + memory_context

    return system_prompt


# ============================================================
# GENERATE NORMAL RESPONSE
# ============================================================

def generate_response(
    messages,
    memory_context=""
):

    system_prompt = build_system_prompt(
        memory_context
    )


    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",

                "content": system_prompt
            },

            *messages
        ],

        temperature=0.7
    )


    return response.choices[0].message.content


# ============================================================
# GENERATE STREAMING RESPONSE
# ============================================================

def generate_stream(
    messages,
    memory_context=""
):

    system_prompt = build_system_prompt(
        memory_context
    )


    stream = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",

                "content": system_prompt
            },

            *messages
        ],

        temperature=0.7,

        stream=True
    )


    for chunk in stream:

        if not chunk.choices:

            continue


        delta = chunk.choices[0].delta


        if delta.content:

            yield delta.content