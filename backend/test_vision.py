import pyautogui

from services.vision import analyze_screen


screenshot = pyautogui.screenshot()

print("\nSCREENSHOT SIZE:", screenshot.size)
print("PYAUTOGUI SIZE:", pyautogui.size())

result = analyze_screen("the VS Code icon in the Windows taskbar")

print("\nVISION RESULT:")
print(result)