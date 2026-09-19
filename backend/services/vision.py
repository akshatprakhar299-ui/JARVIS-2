import os
import base64
import json
import pyautogui

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VISION_MODEL = "qwen/qwen3.8-27b"


def take_screen_base64():

    screenshot = pyautogui.screenshot()

    screenshot_path = "jarvis_screen.png"

    screenshot.save(screenshot_path)

    with open(screenshot_path, "rb") as image_file:

        image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    return image_base64, screenshot.size


def analyze_screen(target: str):

    try:

        image_base64, image_size = take_screen_base64()

        screen_width, screen_height = image_size

        prompt = f"""
You are the visual perception system of a Windows computer-use agent.

Analyze the screenshot carefully.

SCREENSHOT DIMENSIONS:

Width: {screen_width}
Height: {screen_height}

The requested target is:

"{target}"

Your task is to locate the EXACT visible UI element requested.

IMPORTANT:

- Only report the target if it is actually visible.
- Do NOT guess.
- Do NOT use the center of the screen unless the target itself
  is actually there.
- Do NOT interpret the user's requested target as the target's
  location.
- Carefully inspect the screenshot before answering.
- Coordinates must refer to the screenshot's pixel coordinate system.
- Origin (0,0) is the TOP-LEFT corner.
- x increases toward the RIGHT.
- y increases toward the BOTTOM.

Return the bounding box of the target.

The bounding box must contain:

left
top
right
bottom

The coordinates must be absolute pixel coordinates within:

0 <= x <= {screen_width}
0 <= y <= {screen_height}

Then provide your confidence.

Return ONLY valid JSON:

{{
    "found": true,
    "left": 100,
    "top": 200,
    "right": 300,
    "bottom": 400,
    "confidence": 0.95,
    "description": "Exact description of the detected element"
}}

If the target is NOT visible, return:

{{
    "found": false,
    "left": null,
    "top": null,
    "right": null,
    "bottom": null,
    "confidence": 0.0,
    "description": "Target not visible"
}}
"""

        response = client.chat.completions.create(

            model=VISION_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],

            temperature=0,

            response_format={
                "type": "json_object"
            }
        )

        result = response.choices[0].message.content

        data = json.loads(result)

        # ----------------------------------------------------
        # VALIDATE RESULT
        # ----------------------------------------------------

        if not data.get("found"):

            return {
                "found": False,
                "confidence": 0,
                "description": data.get(
                    "description",
                    "Target not found"
                )
            }

        left = data.get("left")
        top = data.get("top")
        right = data.get("right")
        bottom = data.get("bottom")

        confidence = float(
            data.get("confidence", 0)
        )

        # ----------------------------------------------------
        # VALIDATE COORDINATES
        # ----------------------------------------------------

        coordinates = [
            left,
            top,
            right,
            bottom
        ]

        if any(value is None for value in coordinates):

            return {
                "found": False,
                "confidence": 0,
                "description": "Vision returned incomplete coordinates"
            }

        left = int(left)
        top = int(top)
        right = int(right)
        bottom = int(bottom)

        if (
            left < 0
            or top < 0
            or right > screen_width
            or bottom > screen_height
            or left >= right
            or top >= bottom
        ):

            return {
                "found": False,
                "confidence": 0,
                "description": "Vision returned invalid coordinates"
            }

        # ----------------------------------------------------
        # CALCULATE CENTER OURSELVES
        # ----------------------------------------------------

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        return {
            "found": True,
            "x": center_x,
            "y": center_y,
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "confidence": confidence,
            "description": data.get(
                "description",
                "Target detected"
            )
        }

    except Exception as error:

        return {
            "found": False,
            "confidence": 0,
            "description": "Vision error",
            "error": str(error)
        }