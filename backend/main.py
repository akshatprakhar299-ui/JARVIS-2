from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.llm import (
    generate_response,
    generate_stream,
    MODEL_NAME
)

from services.database import (
    initialize_database,
    save_message,
    get_messages,
    clear_messages,
    get_memories,
    delete_memory,
    clear_memories
)

from services.memory import (
    process_memory,
    get_memory_context
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="JARVIS AI",
    description="Personal AI assistant powered by GPT-OSS",
    version="2.1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    message: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "assistant": "JARVIS",
        "model": MODEL_NAME,
        "version": "2.1.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "llm": MODEL_NAME,
        "memory": "enabled",
        "streaming": "enabled"
    }


# ============================================================
# NORMAL CHAT
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    # --------------------------------------------------------
    # Get user message
    # --------------------------------------------------------

    user_message = request.message.strip()


    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not user_message:

        return {
            "success": False,
            "error": "Message cannot be empty"
        }


    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    save_message(
        "user",
        user_message
    )


    # --------------------------------------------------------
    # Process long-term memory
    # --------------------------------------------------------

    try:

        process_memory(
            user_message
        )

    except Exception as error:

        print(
            f"Memory processing error: {error}"
        )


    # --------------------------------------------------------
    # Get recent conversation
    # --------------------------------------------------------

    messages = get_messages(
        limit=20
    )


    # --------------------------------------------------------
    # Get long-term memories
    # --------------------------------------------------------

    try:

        memory_context = get_memory_context()

    except Exception as error:

        print(
            f"Memory retrieval error: {error}"
        )

        memory_context = ""


    # --------------------------------------------------------
    # Generate JARVIS response
    # --------------------------------------------------------

    try:

        assistant_response = generate_response(
            messages,
            memory_context
        )

    except Exception as error:

        print(
            f"LLM error: {error}"
        )

        return {
            "success": False,
            "error": "JARVIS could not generate a response."
        }


    # --------------------------------------------------------
    # Save JARVIS response
    # --------------------------------------------------------

    save_message(
        "assistant",
        assistant_response
    )


    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {

        "success": True,

        "message": assistant_response,

        "model": MODEL_NAME

    }


# ============================================================
# STREAMING CHAT
# ============================================================

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):

    # --------------------------------------------------------
    # Get user message
    # --------------------------------------------------------

    user_message = request.message.strip()


    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not user_message:

        return {
            "success": False,
            "error": "Message cannot be empty"
        }


    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    save_message(
        "user",
        user_message
    )


    # --------------------------------------------------------
    # Process long-term memory
    # --------------------------------------------------------

    try:

        process_memory(
            user_message
        )

    except Exception as error:

        print(
            f"Memory processing error: {error}"
        )


    # --------------------------------------------------------
    # Get recent conversation
    # --------------------------------------------------------

    messages = get_messages(
        limit=20
    )


    # --------------------------------------------------------
    # Get long-term memories
    # --------------------------------------------------------

    try:

        memory_context = get_memory_context()

    except Exception as error:

        print(
            f"Memory retrieval error: {error}"
        )

        memory_context = ""


    # --------------------------------------------------------
    # Streaming generator
    # --------------------------------------------------------

    def response_generator():

        full_response = ""


        try:

            for chunk in generate_stream(
                messages,
                memory_context
            ):

                full_response += chunk

                yield chunk


            # ------------------------------------------------
            # Save complete response after streaming
            # ------------------------------------------------

            if full_response:

                save_message(
                    "assistant",
                    full_response
                )


        except Exception as error:

            print(
                f"Streaming LLM error: {error}"
            )

            yield "\n\n[JARVIS encountered an error.]"


    # --------------------------------------------------------
    # Return streaming response
    # --------------------------------------------------------

    return StreamingResponse(

        response_generator(),

        media_type="text/plain",

        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }

    )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

@app.get("/history")
async def history():

    messages = get_messages(
        limit=100
    )

    return {

        "success": True,

        "messages": messages

    }


# ============================================================
# CLEAR CONVERSATION HISTORY
# ============================================================

@app.delete("/history")
async def delete_history():

    clear_messages()

    return {

        "success": True,

        "message": "Conversation history cleared"

    }


# ============================================================
# GET LONG-TERM MEMORY
# ============================================================

@app.get("/memory")
async def memory():

    memories = get_memories()

    return {

        "success": True,

        "memories": memories

    }


# ============================================================
# DELETE SPECIFIC MEMORY
# ============================================================

@app.delete("/memory/{key}")
async def delete_specific_memory(key: str):

    delete_memory(
        key
    )

    return {

        "success": True,

        "message": f"Memory '{key}' deleted"

    }


# ============================================================
# DELETE ALL LONG-TERM MEMORY
# ============================================================

@app.delete("/memory")
async def delete_all_memory():

    clear_memories()

    return {

        "success": True,

        "message": "All memories cleared"

    }