import os
import json

from dotenv import load_dotenv
from groq import Groq

from computer_tools import (
    open_app,
    close_app,
    open_website,
    type_text,
    press_key,
    move_cursor,
    click_mouse,
    double_click,
    right_click,
    get_screen_size,
    get_mouse_position,
    take_screenshot,
    click_on_screen,
    wait_for_element
)

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, an intelligent personal AI assistant running
on the user's Windows computer.

You can answer normal questions and control the user's computer
using the available tools.

============================================================
COMPUTER CAPABILITIES
============================================================

You can:

1. Open applications
2. Close applications
3. Open websites
4. Type text
5. Press keyboard keys
6. Move the mouse
7. Click at exact coordinates
8. Double-click
9. Right-click
10. Get screen size
11. Get mouse position
12. Take screenshots
13. Visually locate UI elements
14. Visually click UI elements
15. Wait for UI elements to appear

============================================================
APPLICATION CONTROL
============================================================

If the user asks:

"Open Spotify"

use:

open_app("Spotify")

If the user asks:

"Close Spotify"

use:

close_app("Spotify")

============================================================
WEBSITE CONTROL
============================================================

If the user asks:

"Open YouTube"

use:

open_website("youtube.com")

If the user gives a website URL, use open_website.

============================================================
KEYBOARD CONTROL
============================================================

Use type_text when the user asks you to type something.

Example:

User:
"Type hello world"

Use:

type_text("hello world")

Use press_key for keys such as:

Enter
Escape
Tab
Backspace
Space
Ctrl
Alt
Shift
Arrow keys

============================================================
EXACT MOUSE CONTROL
============================================================

If the user gives exact coordinates:

"Click at 500, 300"

use:

click_mouse(500, 300)

If the user says:

"Move the mouse to 800, 400"

use:

move_cursor(800, 400)

Do NOT invent coordinates.

============================================================
VISION-BASED COMPUTER CONTROL
============================================================

If the user describes a UI element rather than giving
coordinates, use:

click_on_screen()

Examples:

"Click the Spotify play button."

Use:

click_on_screen("Spotify play button")

"Click the Chrome address bar."

Use:

click_on_screen("Chrome address bar")

"Click the VS Code terminal."

Use:

click_on_screen("VS Code terminal")

"Click the YouTube search box."

Use:

click_on_screen("YouTube search box")

NEVER randomly guess coordinates.

The vision system will inspect the current screenshot and
determine the coordinates.

============================================================
WAITING FOR UI ELEMENTS
============================================================

After opening an application or website, the screen may need
time to load.

Use:

wait_for_element()

when you need to wait for a specific element to appear.

Example:

1. open_website("youtube.com")
2. wait_for_element("YouTube search box")
3. click_on_screen("YouTube search box")

Another example:

1. open_app("Spotify")
2. wait_for_element("Spotify play button")
3. click_on_screen("Spotify play button")

Do not blindly assume that a page has loaded.

============================================================
MULTI-STEP TASKS
============================================================

You can perform multiple tool calls for one user request.

Example:

User:

"Open YouTube and search for Believer."

Possible sequence:

1. open_website("youtube.com")
2. wait_for_element("YouTube search box")
3. click_on_screen("YouTube search box")
4. type_text("Believer")
5. press_key("enter")

Example:

User:

"Open Spotify and play music."

Possible sequence:

1. open_app("Spotify")
2. wait_for_element("Spotify play button")
3. click_on_screen("Spotify play button")

For complex tasks:

OBSERVE → ACT → WAIT → OBSERVE → ACT

Do not assume the screen changed successfully.

Always inspect tool results before deciding the next action.

============================================================
YOUTUBE / BROWSER TASKS
============================================================

For a request such as:

"Open YouTube and play Believer by Imagine Dragons."

Break the task into steps.

Example:

1. open_website("youtube.com")
2. wait_for_element("YouTube search box")
3. click_on_screen("YouTube search box")
4. type_text("Believer Imagine Dragons")
5. press_key("enter")
6. wait_for_element("Believer Imagine Dragons video")
7. click_on_screen("Believer Imagine Dragons video")

The exact target description should be as specific as possible.

============================================================
SCREEN INFORMATION
============================================================

Use get_screen_size() if screen dimensions are needed.

Use get_mouse_position() when the current mouse location
is needed.

Use take_screenshot() when the user asks for a screenshot or
when a screenshot is explicitly useful.

============================================================
TOOL FAILURE
============================================================

If a tool fails:

- Do not pretend it succeeded.
- Read the returned error.
- Try another reasonable action if possible.
- If the task cannot continue, explain what failed.

============================================================
VISUAL CLICK SAFETY
============================================================

Do not click if:

- The target was not found.
- Vision confidence is too low.
- Coordinates are invalid.

Do not randomly click unknown locations.

============================================================
IMPORTANT SAFETY
============================================================

For potentially destructive or consequential actions such as:

- deleting files
- deleting accounts
- sending messages
- submitting forms
- making purchases
- sending emails
- posting publicly
- changing important settings

require appropriate user confirmation before performing the
final consequential action.

============================================================
NORMAL QUESTIONS
============================================================

If the user is simply asking a question and no computer
action is required, answer normally.

Do not use computer tools unnecessarily.

Keep normal responses concise and natural.
"""


# ============================================================
# SYSTEM PROMPT + MEMORY
# ============================================================

def build_system_prompt(memory_context=""):
    """
    Build the system prompt and optionally include
    relevant user memory.
    """

    prompt = SYSTEM_PROMPT

    if memory_context:
        prompt += f"""

============================================================
RELEVANT USER MEMORY
============================================================

{memory_context}

Use this information only when relevant to the current
conversation.
"""

    return prompt


# ============================================================
# BUILD MESSAGES
# ============================================================

def build_messages(messages, memory_context=""):
    """
    Build the message list sent to Groq.
    """

    conversation = [
        {
            "role": "system",
            "content": build_system_prompt(memory_context)
        }
    ]

    for message in messages:

        if isinstance(message, dict):

            role = message.get("role")
            content = message.get("content")

            if role and content:
                conversation.append({
                    "role": role,
                    "content": content
                })

    return conversation


# ============================================================
# TOOLS
# ============================================================

TOOLS = [

    # --------------------------------------------------------
    # OPEN APP
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open an installed Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app": {
                        "type": "string",
                        "description": "Name of the application."
                    }
                },
                "required": ["app"]
            }
        }
    },

    # --------------------------------------------------------
    # CLOSE APP
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Close a running Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app": {
                        "type": "string",
                        "description": "Name of the application."
                    }
                },
                "required": ["app"]
            }
        }
    },

    # --------------------------------------------------------
    # OPEN WEBSITE
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website using the default browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL or domain."
                    }
                },
                "required": ["url"]
            }
        }
    },

    # --------------------------------------------------------
    # TYPE TEXT
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text using the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type."
                    }
                },
                "required": ["text"]
            }
        }
    },

    # --------------------------------------------------------
    # PRESS KEY
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a keyboard key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Keyboard key to press."
                    }
                },
                "required": ["key"]
            }
        }
    },

    # --------------------------------------------------------
    # MOVE CURSOR
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "move_cursor",
            "description": "Move the cursor to exact screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    # --------------------------------------------------------
    # CLICK
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "click_mouse",
            "description": "Click at exact screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    # --------------------------------------------------------
    # DOUBLE CLICK
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "double_click",
            "description": "Double-click at exact screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    # --------------------------------------------------------
    # RIGHT CLICK
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "right_click",
            "description": "Right-click at exact screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    # --------------------------------------------------------
    # SCREEN SIZE
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_screen_size",
            "description": "Get the current screen resolution.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    # --------------------------------------------------------
    # MOUSE POSITION
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_mouse_position",
            "description": "Get the current mouse cursor position.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    # --------------------------------------------------------
    # VISION CLICK
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "click_on_screen",
            "description": (
                "Use computer vision to find a visible UI element "
                "on the current screen and click its center."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": (
                            "Specific visible UI element to find. "
                            "Examples: 'VS Code icon in the taskbar', "
                            "'YouTube search box', "
                            "'Spotify play button'."
                        )
                    }
                },
                "required": ["target"]
            }
        }
    },

    # --------------------------------------------------------
    # WAIT FOR ELEMENT
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "wait_for_element",
            "description": (
                "Wait until a specific visible UI element appears "
                "on the screen. Useful after opening applications "
                "or websites."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "UI element to wait for."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": (
                            "Maximum number of seconds to wait. "
                            "Usually between 5 and 15."
                        ),
                        "default": 10
                    }
                },
                "required": ["target"]
            }
        }
    }
]


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool(name, arguments):
    """
    Execute a tool requested by GPT-OSS.
    """

    try:

        if name == "open_app":

            return open_app(
                arguments["app"]
            )

        elif name == "close_app":

            return close_app(
                arguments["app"]
            )

        elif name == "open_website":

            return open_website(
                arguments["url"]
            )

        elif name == "type_text":

            return type_text(
                arguments["text"]
            )

        elif name == "press_key":

            return press_key(
                arguments["key"]
            )

        elif name == "move_cursor":

            return move_cursor(
                int(arguments["x"]),
                int(arguments["y"])
            )

        elif name == "click_mouse":

            return click_mouse(
                int(arguments["x"]),
                int(arguments["y"])
            )

        elif name == "double_click":

            return double_click(
                int(arguments["x"]),
                int(arguments["y"])
            )

        elif name == "right_click":

            return right_click(
                int(arguments["x"]),
                int(arguments["y"])
            )

        elif name == "get_screen_size":

            return get_screen_size()

        elif name == "get_mouse_position":

            return get_mouse_position()

        elif name == "take_screenshot":

            return take_screenshot()

        elif name == "click_on_screen":

            return click_on_screen(
                arguments["target"]
            )

        elif name == "wait_for_element":

            return wait_for_element(
                arguments["target"],
                int(arguments.get("timeout", 10))
            )

        else:

            return f"Unknown tool: {name}"

    except Exception as error:

        return f"Tool execution failed: {str(error)}"


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(messages, memory_context=""):
    """
    Generate a JARVIS response.

    Supports multiple rounds of tool calls so JARVIS can perform
    complex multi-step computer tasks.
    """

    conversation = build_messages(
        messages,
        memory_context
    )

    # Maximum number of tool-call rounds for one request.
    max_iterations = 8

    for iteration in range(max_iterations):

        try:

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
                stream=False
            )

        except Exception as error:

            return f"LLM request failed: {str(error)}"

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # NO TOOL CALL
        # ----------------------------------------------------

        if not assistant_message.tool_calls:

            return assistant_message.content or ""

        # ----------------------------------------------------
        # ADD ASSISTANT TOOL CALL MESSAGE
        # ----------------------------------------------------

        assistant_tool_message = {
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": []
        }

        for tool_call in assistant_message.tool_calls:

            assistant_tool_message["tool_calls"].append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })

        conversation.append(
            assistant_tool_message
        )

        # ----------------------------------------------------
        # EXECUTE EACH TOOL
        # ----------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            raw_arguments = tool_call.function.arguments

            try:

                arguments = json.loads(
                    raw_arguments
                )

            except json.JSONDecodeError:

                arguments = {}

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            # ------------------------------------------------
            # SEND RESULT BACK TO GPT
            # ------------------------------------------------

            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

    return (
        "I reached the maximum number of computer actions "
        "allowed for this request."
    )


# ============================================================
# STREAMING
# ============================================================

def generate_stream(messages, memory_context=""):
    """
    Generate a streaming text response.

    Computer tool execution remains handled by generate_response().
    """

    conversation = build_messages(
        messages,
        memory_context
    )

    try:

        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=0.7,
            stream=True
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta and delta.content:
                yield delta.content

    except Exception as error:

        yield f"LLM streaming failed: {str(error)}"