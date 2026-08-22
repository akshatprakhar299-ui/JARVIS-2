from services.database import (
    save_memory,
    get_memories,
    delete_memory
)


# ============================================================
# MEMORY KEYWORDS
# ============================================================

MEMORY_PATTERNS = {

    "name": [
        "my name is ",
        "i am ",
        "i'm "
    ],

    "favorite_language": [
        "my favorite programming language is ",
        "my favourite programming language is "
    ],

    "college": [
        "i study at ",
        "i am studying at ",
        "my college is "
    ],

    "location": [
        "i live in ",
        "i am from "
    ]
}


# ============================================================
# EXTRACT MEMORY
# ============================================================

def extract_memory(user_message):

    text = user_message.strip()

    lower_text = text.lower()


    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    for pattern in MEMORY_PATTERNS["name"]:

        if lower_text.startswith(pattern):

            value = text[len(pattern):].strip()

            if value:

                return "name", value


    # --------------------------------------------------------
    # FAVORITE PROGRAMMING LANGUAGE
    # --------------------------------------------------------

    for pattern in MEMORY_PATTERNS["favorite_language"]:

        if lower_text.startswith(pattern):

            value = text[len(pattern):].strip()

            if value:

                return "favorite_language", value


    # --------------------------------------------------------
    # COLLEGE
    # --------------------------------------------------------

    for pattern in MEMORY_PATTERNS["college"]:

        if lower_text.startswith(pattern):

            value = text[len(pattern):].strip()

            if value:

                return "college", value


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    for pattern in MEMORY_PATTERNS["location"]:

        if lower_text.startswith(pattern):

            value = text[len(pattern):].strip()

            if value:

                return "location", value


    return None, None


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

def process_memory(user_message):

    key, value = extract_memory(
        user_message
    )

    if key and value:

        save_memory(
            key,
            value
        )

        return True

    return False


# ============================================================
# BUILD MEMORY CONTEXT
# ============================================================

def get_memory_context():

    memories = get_memories()


    if not memories:

        return ""


    lines = []

    for memory in memories:

        lines.append(
            f"- {memory['key']}: {memory['value']}"
        )


    return "\n".join(lines)