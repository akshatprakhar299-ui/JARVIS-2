from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from pydantic import BaseModel


from services.llm import (
    generate_response,
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


from services.firebase_auth import (
    verify_token
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="JARVIS AI",
    description="Personal AI assistant powered by GPT-OSS",
    version="3.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
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
# AUTHENTICATION
# ============================================================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:

        decoded_token = verify_token(
            credentials.credentials
        )

        return decoded_token

    except Exception as error:

        print(
            f"Authentication error: {error}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )


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

        "version": "3.0.0",

        "authentication": "enabled",

        "user_memory": "enabled"

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

        "authentication": "enabled"

    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Get Firebase UID
    # --------------------------------------------------------

    user_id = current_user["uid"]


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
        user_id,
        "user",
        user_message
    )


    # --------------------------------------------------------
    # Process long-term memory
    # --------------------------------------------------------

    try:

        process_memory(
            user_id,
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
        user_id,
        limit=20
    )


    # --------------------------------------------------------
    # Get user's long-term memories
    # --------------------------------------------------------

    try:

        memory_context = get_memory_context(
            user_id
        )

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

            "error":
                "JARVIS could not generate a response."

        }


    # --------------------------------------------------------
    # Save JARVIS response
    # --------------------------------------------------------

    save_message(
        user_id,
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
# CONVERSATION HISTORY
# ============================================================

@app.get("/history")
async def history(
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["uid"]


    messages = get_messages(
        user_id,
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
async def delete_history(
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["uid"]


    clear_messages(
        user_id
    )


    return {

        "success": True,

        "message": "Conversation history cleared"

    }


# ============================================================
# GET LONG-TERM MEMORY
# ============================================================

@app.get("/memory")
async def memory(
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["uid"]


    memories = get_memories(
        user_id
    )


    return {

        "success": True,

        "memories": memories

    }


# ============================================================
# DELETE SPECIFIC MEMORY
# ============================================================

@app.delete("/memory/{key}")
async def delete_specific_memory(
    key: str,
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["uid"]


    delete_memory(
        user_id,
        key
    )


    return {

        "success": True,

        "message":
            f"Memory '{key}' deleted"

    }


# ============================================================
# DELETE ALL LONG-TERM MEMORY
# ============================================================

@app.delete("/memory")
async def delete_all_memory(
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["uid"]


    clear_memories(
        user_id
    )


    return {

        "success": True,

        "message": "All memories cleared"

    }