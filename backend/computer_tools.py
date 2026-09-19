import subprocess
import webbrowser
import pyautogui
import json
import time
from services.vision import analyze_screen


# ============================================================
# OPEN ANY INSTALLED WINDOWS APP
# ============================================================

def open_app(app: str):

    app = app.strip().lower()

    try:

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-StartApps | ConvertTo-Json -Compress"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return "Unable to search installed Windows applications."

        if not result.stdout.strip():
            return "No installed applications were found."

        apps = json.loads(result.stdout)

        if isinstance(apps, dict):
            apps = [apps]

        best_match = None

        # Exact match
        for item in apps:

            name = item.get("Name", "")
            app_id = item.get("AppID", "")

            if name.lower().strip() == app:

                best_match = item
                break

        # Partial match
        if not best_match:

            for item in apps:

                name = item.get("Name", "")
                app_id = item.get("AppID", "")

                if app in name.lower():

                    best_match = item
                    break

        if best_match:

            app_name = best_match.get("Name", "")
            app_id = best_match.get("AppID", "")

            try:

                subprocess.Popen(
                    [
                        "explorer.exe",
                        f"shell:AppsFolder\\{app_id}"
                    ]
                )

                return f"Opened {app_name}"

            except Exception as error:

                return (
                    f"Found {app_name}, but could not launch it: "
                    f"{str(error)}"
                )

        # Fallback
        try:

            subprocess.Popen(
                ["cmd", "/c", "start", "", app],
                shell=False
            )

            time.sleep(1)

            return f"Attempted to open {app}"

        except Exception:

            return (
                f"I could not find an installed application "
                f"called {app}."
            )

    except json.JSONDecodeError:

        return "Windows returned an invalid application list."

    except subprocess.TimeoutExpired:

        return "Searching installed applications timed out."

    except Exception as error:

        return f"Failed to open {app}: {str(error)}"


# ============================================================
# CLOSE RUNNING WINDOWS APP
# ============================================================

def close_app(app: str):

    app = app.strip().lower()

    process_aliases = {

        "spotify": ["spotify"],
        "chrome": ["chrome"],
        "google chrome": ["chrome"],
        "edge": ["msedge"],
        "microsoft edge": ["msedge"],
        "firefox": ["firefox"],
        "discord": ["discord"],
        "vscode": ["code"],
        "vs code": ["code"],
        "visual studio code": ["code"],
        "notepad": ["notepad"],
        "calculator": ["calculator", "calc"],
        "calc": ["calculator", "calc"],
        "whatsapp": ["whatsapp"],
        "telegram": ["telegram"],
        "steam": ["steam"],
        "word": ["winword"],
        "microsoft word": ["winword"],
        "excel": ["excel"],
        "microsoft excel": ["excel"],
        "powerpoint": ["powerpnt"],
        "microsoft powerpoint": ["powerpnt"],
        "outlook": ["outlook"],
        "teams": ["ms-teams", "teams"],
        "pycharm": ["pycharm64", "pycharm"],
        "intellij": ["idea64", "idea"],
        "intellij idea": ["idea64", "idea"]
    }

    try:

        processes = process_aliases.get(app)

        if processes:

            closed = False

            for process in processes:

                result = subprocess.run(
                    [
                        "taskkill",
                        "/IM",
                        f"{process}.exe",
                        "/T",
                        "/F"
                    ],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:

                    closed = True

            if closed:

                return f"Closed {app}"

        # Dynamic process search

        powershell_command = f"""
        Get-Process |
        Where-Object {{
            $_.ProcessName -like "*{app}*"
        }} |
        Select-Object -ExpandProperty Id
        """

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                powershell_command
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():

            process_ids = result.stdout.strip().splitlines()

            closed_any = False

            for process_id in process_ids:

                process_id = process_id.strip()

                if process_id.isdigit():

                    kill_result = subprocess.run(
                        [
                            "taskkill",
                            "/PID",
                            process_id,
                            "/T",
                            "/F"
                        ],
                        capture_output=True,
                        text=True
                    )

                    if kill_result.returncode == 0:

                        closed_any = True

            if closed_any:

                return f"Closed {app}"

        return (
            f"I could not find a running application "
            f"called {app}."
        )

    except subprocess.TimeoutExpired:

        return f"Closing {app} timed out."

    except Exception as error:

        return f"Failed to close {app}: {str(error)}"


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(url: str):

    try:

        if not url.startswith(
            ("http://", "https://")
        ):

            url = "https://" + url

        webbrowser.open(url)

        return f"Opened {url}"

    except Exception as error:

        return f"Failed to open website: {str(error)}"


# ============================================================
# TYPE TEXT
# ============================================================

def type_text(text: str):

    try:

        pyautogui.write(
            text,
            interval=0.02
        )

        return "Text typed successfully"

    except Exception as error:

        return f"Failed to type text: {str(error)}"


# ============================================================
# PRESS KEY
# ============================================================

def press_key(key: str):

    try:

        pyautogui.press(key)

        return f"Pressed {key}"

    except Exception as error:

        return f"Failed to press {key}: {str(error)}"


# ============================================================
# MOVE MOUSE
# ============================================================

def move_cursor(x: int, y: int):

    try:

        screen_width, screen_height = pyautogui.size()

        if x < 0 or x > screen_width:
            return "X coordinate is outside the screen."

        if y < 0 or y > screen_height:
            return "Y coordinate is outside the screen."

        pyautogui.moveTo(
            x,
            y,
            duration=0.2
        )

        return f"Moved cursor to ({x}, {y})"

    except Exception as error:

        return f"Failed to move cursor: {str(error)}"


# ============================================================
# LEFT CLICK
# ============================================================

def click_mouse(x: int, y: int):

    try:

        screen_width, screen_height = pyautogui.size()

        if x < 0 or x > screen_width:
            return "X coordinate is outside the screen."

        if y < 0 or y > screen_height:
            return "Y coordinate is outside the screen."

        pyautogui.click(
            x,
            y
        )

        return f"Clicked at ({x}, {y})"

    except Exception as error:

        return f"Failed to click: {str(error)}"


# ============================================================
# DOUBLE CLICK
# ============================================================

def double_click(x: int, y: int):

    try:

        screen_width, screen_height = pyautogui.size()

        if x < 0 or x > screen_width:
            return "X coordinate is outside the screen."

        if y < 0 or y > screen_height:
            return "Y coordinate is outside the screen."

        pyautogui.doubleClick(
            x,
            y
        )

        return f"Double-clicked at ({x}, {y})"

    except Exception as error:

        return f"Failed to double-click: {str(error)}"


# ============================================================
# RIGHT CLICK
# ============================================================

def right_click(x: int, y: int):

    try:

        screen_width, screen_height = pyautogui.size()

        if x < 0 or x > screen_width:
            return "X coordinate is outside the screen."

        if y < 0 or y > screen_height:
            return "Y coordinate is outside the screen."

        pyautogui.rightClick(
            x,
            y
        )

        return f"Right-clicked at ({x}, {y})"

    except Exception as error:

        return f"Failed to right-click: {str(error)}"


# ============================================================
# GET SCREEN SIZE
# ============================================================

def get_screen_size():

    try:

        width, height = pyautogui.size()

        return f"Screen size is {width}x{height}"

    except Exception as error:

        return f"Could not get screen size: {str(error)}"


# ============================================================
# GET CURRENT MOUSE POSITION
# ============================================================

def get_mouse_position():

    try:

        x, y = pyautogui.position()

        return f"Current mouse position is ({x}, {y})"

    except Exception as error:

        return f"Could not get mouse position: {str(error)}"


# ============================================================
# TAKE SCREENSHOT
# ============================================================

def take_screenshot():

    try:

        screenshot = pyautogui.screenshot()

        screenshot.save(
            "jarvis_screen.png"
        )

        return "Screenshot saved as jarvis_screen.png"

    except Exception as error:

        return f"Screenshot failed: {str(error)}"

def click_on_screen(target: str):
    """
    Finds a visual element on the screen and clicks its center.
    """

    try:
        result = analyze_screen(target)

        if not result.get("found"):
            return f"I could not find '{target}' on the screen."

        x = result.get("x")
        y = result.get("y")
        confidence = float(result.get("confidence", 0))

        if x is None or y is None:
            return f"I found '{target}' but could not determine its coordinates."

        if confidence < 0.70:
            return (
                f"I found something that may be '{target}', "
                f"but confidence is too low ({confidence:.2f}). "
                f"I did not click it."
            )

        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return "Vision returned coordinates outside the screen."

        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click(x, y)

        return (
            f"Clicked '{target}' at ({x}, {y}) "
            f"with confidence {confidence:.2f}."
        )

    except Exception as error:
        return f"Failed to click '{target}': {str(error)}"

def wait_for_element(target: str, timeout: int = 10, interval: float = 1.0):
    """
    Repeatedly analyzes the screen until the requested element
    appears or the timeout is reached.
    """

    start_time = time.time()

    while time.time() - start_time < timeout:

        result = analyze_screen(target)

        if result.get("found"):

            confidence = float(
                result.get("confidence", 0)
            )

            if confidence >= 0.70:

                return {
                    "found": True,
                    "x": result.get("x"),
                    "y": result.get("y"),
                    "confidence": confidence,
                    "description": result.get("description"),
                    "message": f"Found '{target}'"
                }

        time.sleep(interval)

    return {
        "found": False,
        "message": f"Could not find '{target}' within {timeout} seconds."
    }