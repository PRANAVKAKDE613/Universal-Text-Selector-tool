import pyautogui
import pytesseract
import pyperclip
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab, Image
from plyer import notification
import winsound
import time
import tkinter as tk

# Set Tesseract OCR Path (Update this if needed)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Global variables for selection
start_x = start_y = end_x = end_y = 0
root = None
canvas = None

def start_selection():
    """Opens a transparent overlay to select text area."""
    global root, canvas

    # Create a fullscreen transparent window
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)  # Always stay on top
    root.attributes("-alpha", 0.3)  # Semi-transparent
    root.configure(bg="black")

    canvas = tk.Canvas(root, cursor="cross", bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Bind mouse events
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.mainloop()

def on_press(event):
    """Record starting position of mouse selection."""
    global start_x, start_y
    start_x, start_y = event.x, event.y

def on_drag(event):
    """Draw a rectangle while dragging.""" 
    global canvas, start_x, start_y
    canvas.delete("rect")
    canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red", width=6, tags="rect")  # Increased width to 6

def on_release(event):
    """Record end position, close the window, and extract text."""
    global end_x, end_y, root
    end_x, end_y = event.x, event.y
    root.destroy()  # Close overlay window

    # Process the captured area
    capture_screen()

def capture_screen():
    """Capture selected screen area and extract text."""
    global start_x, start_y, end_x, end_y

    # Ensure coordinates are correct
    x1, y1 = min(start_x, end_x), min(start_y, end_y)
    x2, y2 = max(start_x, end_x), max(start_y, end_y)

    time.sleep(0.2)  # Small delay to ensure proper capture
    image = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Convert image to OpenCV format
    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to improve text detection
    processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Extract text using Tesseract OCR
    extracted_text = pytesseract.image_to_string(processed_image)

    if extracted_text.strip():
        # Copy text to clipboard
        pyperclip.copy(extracted_text)

        # Show notification
        notification.notify(
            title="Text Extracted!",
            message="Text copied to clipboard.",
            timeout=3
        )

        # Play a beep sound
        winsound.Beep(1000, 200)

        print("\nExtracted Text:\n", extracted_text)
    else:
        print("No text detected. Try again.")

# Change hotkey to `Ctrl + Caps Lock` to start text selection
keyboard.add_hotkey("ctrl+caps lock", start_selection)

# Automatically exit after text selection and extraction
keyboard.add_hotkey("esc", lambda: exit_program())

def exit_program():
    """Function to exit the program."""
    print("Exiting program...")
    exit()

# Keep script running, waiting for the hotkey
keyboard.wait("esc")
