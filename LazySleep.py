import tkinter as tk
from tkinter import messagebox
import subprocess
from datetime import datetime, timedelta
import json
import os

# Constants
SLIDER_MIN = 0
SLIDER_MAX = 180  # minutes (3 hours)
TICK_INTERVAL = 30  # minutes between markers
SLIDER_LENGTH = 440  # length for the slider widget
MARGIN = 30  # extra space on the sides to ensure text is not cut off
# canvas width includes extra space for labels
CANVAS_WIDTH = SLIDER_LENGTH + 2 * MARGIN
PIXELS_PER_MINUTE = SLIDER_LENGTH / (SLIDER_MAX - SLIDER_MIN)
DETECTION_RADIUS = 200  # extra pixels around the window for mouse detection

# Global variables
invisibility_enabled = False
current_theme = "dark_grey"  # Default theme

# Configuration file to save preferences
CONFIG_FILE = "config.json"

# Load saved preferences


def load_config():
    global current_theme
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            current_theme = config.get("theme", "dark_grey")

# Save preferences


def save_config():
    with open(CONFIG_FILE, "w") as file:
        json.dump({"theme": current_theme}, file)

# Apply the selected theme


def apply_theme(theme):
    global current_theme
    current_theme = theme
    if theme == "white":
        bg_color = "#FFFFFF"
        fg_color = "#000000"
        trough_color = "#DDDDDD"
    elif theme == "light_grey":
        bg_color = "#F0F0F0"
        fg_color = "#000000"
        trough_color = "#CCCCCC"
    elif theme == "dark_grey":
        bg_color = "#2E2E2E"
        fg_color = "#FFFFFF"
        trough_color = "#404040"
    elif theme == "black":
        bg_color = "#000000"
        fg_color = "#FFFFFF"
        trough_color = "#333333"

    # Apply colors to all widgets
    root.configure(bg=bg_color)
    main_frame.configure(bg=bg_color)
    instr_label.configure(bg=bg_color, fg=fg_color)
    slider_frame.configure(bg=bg_color)
    tick_canvas.configure(bg=bg_color)
    slider.configure(bg=bg_color, fg=fg_color, troughcolor=trough_color)
    marker_canvas.configure(bg=bg_color)
    label_canvas.configure(bg=bg_color)
    time_label.configure(bg=bg_color, fg=fg_color)
    btn_frame.configure(bg=bg_color)
    schedule_button.configure(bg=trough_color, fg=fg_color)
    cancel_button.configure(bg=trough_color, fg=fg_color)
    toggle_button.configure(bg=trough_color, fg=fg_color)
    invisibility_label.configure(bg=bg_color, fg=fg_color)
    theme_menu.configure(bg=trough_color, fg=fg_color)
    custom_time_frame.configure(bg=bg_color)
    hours_label.configure(bg=bg_color, fg=fg_color)
    minutes_label.configure(bg=bg_color, fg=fg_color)
    hours_entry.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    minutes_entry.configure(bg=bg_color, fg=fg_color,
                            insertbackground=fg_color)
    set_custom_button.configure(bg=trough_color, fg=fg_color)

    save_config()

# Function to update the time label


def update_time_label(value):
    try:
        minutes = int(value)
    except ValueError:
        minutes = 0
    future_time = datetime.now() + timedelta(minutes=minutes)
    # 12-hour format with AM/PM
    time_label.config(
        text=f"Shutdown at: {future_time.strftime('%I:%M:%S %p')}")

# Function to cancel the shutdown


def cancel_shutdown():
    subprocess.call("shutdown -a", shell=True)
    messagebox.showinfo("Cancelled", "Shutdown has been cancelled.")
    schedule_button.config(state=tk.NORMAL)
    slider.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)

# Function to prompt for shutdown cancellation


def prompt_cancel():
    answer = messagebox.askyesno("Cancel Shutdown?",
                                 "Shutdown is scheduled in 3 minutes.\nDo you want to cancel it?")
    if answer:
        cancel_shutdown()

# Function to schedule the shutdown


def schedule_shutdown():
    try:
        minutes = int(slider.get())
    except ValueError:
        minutes = 0
    total_seconds = minutes * 60
    if total_seconds == 0:
        messagebox.showinfo("Shutdown", "Shutting down immediately!")
    schedule_button.config(state=tk.DISABLED)
    slider.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)

    # Schedule the prompt 3 minutes before shutdown if applicable
    if total_seconds > 180:
        delay_before_prompt = (total_seconds - 180) * 1000  # milliseconds
        root.after(delay_before_prompt, prompt_cancel)

    command = f"shutdown -s -t {total_seconds}"
    try:
        subprocess.Popen(command, shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to schedule shutdown: {e}")

# Function to set custom time from entry fields


def set_custom_time():
    try:
        hours = int(hours_entry.get())
        minutes = int(minutes_entry.get())
        total_minutes = hours * 60 + minutes
        if total_minutes < 0:
            raise ValueError("Time cannot be negative")
        slider.set(total_minutes)
        update_time_label(total_minutes)
    except ValueError as e:
        messagebox.showerror(
            "Invalid Input", f"Please enter valid numbers for hours and minutes.\nError: {e}")

# Function to check mouse position for invisibility feature


def check_mouse():
    if invisibility_enabled:
        # Get global pointer coordinates
        pointer_x, pointer_y = root.winfo_pointerx(), root.winfo_pointery()
        # Get window geometry (top-left and dimensions)
        win_x = root.winfo_rootx()
        win_y = root.winfo_rooty()
        win_w = root.winfo_width()
        win_h = root.winfo_height()

        # Define an extended detection area (window bounds plus extra margin)
        if (win_x - DETECTION_RADIUS <= pointer_x <= win_x + win_w + DETECTION_RADIUS and
                win_y - DETECTION_RADIUS <= pointer_y <= win_y + win_h + DETECTION_RADIUS):
            root.attributes("-alpha", 1.0)
        else:
            root.attributes("-alpha", 0.0)
    root.after(300, check_mouse)

# Function to toggle invisibility


def toggle_invisibility():
    global invisibility_enabled
    invisibility_enabled = not invisibility_enabled
    if invisibility_enabled:
        toggle_button.config(text="Disable Invisibility")
        invisibility_label.config(
            text="Move your mouse away to make me invisible")  # Show the label
    else:
        toggle_button.config(text="Enable Invisibility")
        # Ensure the window is visible when disabling
        root.attributes("-alpha", 1.0)
        invisibility_label.config(text="")  # Hide the label


# Create main window and set a larger geometry
root = tk.Tk()
root.title("Lazy Shutdown")
root.geometry("700x500")  # Increased height to accommodate new features

# Load saved preferences
load_config()

# Make the window always on top by default (and remove the ability to turn it off)
root.attributes("-topmost", True)

# Main frame with padding
main_frame = tk.Frame(root, padx=20, pady=20,
                      bg="#2E2E2E")  # Dark grey background
main_frame.pack(fill=tk.BOTH, expand=True)

# Instruction label
instr_label = tk.Label(main_frame, text="Select delay (in minutes) for shutdown:", font=(
    "Helvetica", 12), bg="#2E2E2E", fg="white")
instr_label.pack(pady=(0, 10))

# Frame to hold the slider and custom markers
slider_frame = tk.Frame(main_frame, bg="#2E2E2E")  # Dark grey background
slider_frame.pack()

# Canvas for numeric tick markers above the slider
tick_canvas = tk.Canvas(slider_frame, width=CANVAS_WIDTH,
                        height=30, bg="#2E2E2E", highlightthickness=0)
tick_canvas.pack()

# Draw numeric tick markers every 30 minutes (0, 30, 60, ... 180)
for minute in range(SLIDER_MIN, SLIDER_MAX + 1, TICK_INTERVAL):
    x = MARGIN + (minute - SLIDER_MIN) * PIXELS_PER_MINUTE
    tick_canvas.create_text(x, 10, text=str(minute), font=(
        "Helvetica", 10), anchor=tk.CENTER, fill="white")  # White text

# The slider (Scale widget)
slider = tk.Scale(slider_frame, from_=SLIDER_MIN, to=SLIDER_MAX, orient=tk.HORIZONTAL,
                  length=SLIDER_LENGTH, showvalue=0, command=update_time_label, bg="#2E2E2E", fg="white", troughcolor="#404040")
slider.pack(pady=5)

# Canvas overlay for marker lines inside the slider
marker_canvas = tk.Canvas(slider_frame, width=CANVAS_WIDTH,
                          height=20, bg="#2E2E2E", highlightthickness=0)
marker_canvas.pack()

# Draw marker lines inside the slider
for minute in range(SLIDER_MIN, SLIDER_MAX + 1, TICK_INTERVAL):
    x = MARGIN + (minute - SLIDER_MIN) * PIXELS_PER_MINUTE
    marker_canvas.create_line(x, 0, x, 20, width=2,
                              fill="white")  # White lines

# Canvas for hour labels below the slider (0, 1, 2, 3 hours)
label_canvas = tk.Canvas(slider_frame, width=CANVAS_WIDTH,
                         height=20, bg="#2E2E2E", highlightthickness=0)
label_canvas.pack()
for minute, label in zip([0, 60, 120, 180], ["0 hours", "1 hour", "2 hours", "3 hours"]):
    x = MARGIN + (minute - SLIDER_MIN) * PIXELS_PER_MINUTE
    label_canvas.create_text(x, 10, text=label, font=(
        "Helvetica", 10), anchor=tk.CENTER, fill="white")  # White text

# Label to display the expected shutdown time
time_label = tk.Label(main_frame, text="Shutdown at:", font=(
    "Helvetica", 14), bg="#2E2E2E", fg="white")  # White text
time_label.pack(pady=(15, 10))

# Custom time input frame
custom_time_frame = tk.Frame(main_frame, bg="#2E2E2E")
custom_time_frame.pack(pady=(10, 20))

hours_label = tk.Label(custom_time_frame, text="Hours:",
                       bg="#2E2E2E", fg="white")
hours_label.pack(side=tk.LEFT, padx=5)
hours_entry = tk.Entry(custom_time_frame, width=5,
                       bg="#2E2E2E", fg="white", insertbackground="white")
hours_entry.pack(side=tk.LEFT, padx=5)

minutes_label = tk.Label(
    custom_time_frame, text="Minutes:", bg="#2E2E2E", fg="white")
minutes_label.pack(side=tk.LEFT, padx=5)
minutes_entry = tk.Entry(custom_time_frame, width=5,
                         bg="#2E2E2E", fg="white", insertbackground="white")
minutes_entry.pack(side=tk.LEFT, padx=5)

set_custom_button = tk.Button(custom_time_frame, text="Set Custom Time",
                              command=set_custom_time, bg="#404040", fg="white")
set_custom_button.pack(side=tk.LEFT, padx=10)

# Buttons frame
btn_frame = tk.Frame(main_frame, bg="#2E2E2E")  # Dark grey background
btn_frame.pack(pady=10)

schedule_button = tk.Button(btn_frame, text="Schedule Shutdown",
                            command=schedule_shutdown, width=18, bg="#404040", fg="white")
schedule_button.grid(row=0, column=0, padx=5)

cancel_button = tk.Button(btn_frame, text="Cancel Shutdown", command=cancel_shutdown,
                          state=tk.DISABLED, width=18, bg="#404040", fg="white")
cancel_button.grid(row=0, column=1, padx=5)

# Toggle invisibility button (default is OFF)
toggle_button = tk.Button(btn_frame, text="Enable Invisibility",
                          command=toggle_invisibility, width=18, bg="#404040", fg="white")
toggle_button.grid(row=1, column=0, padx=5, pady=5)

# Label to describe the invisibility feature (initially hidden)
invisibility_label = tk.Label(btn_frame, text="", font=(
    "Helvetica", 10), bg="#2E2E2E", fg="white")  # White text
invisibility_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))

# Theme selection drop-down
themes = ["white", "light_grey", "dark_grey", "black"]
theme_var = tk.StringVar(value=current_theme)  # Default theme

# Function to handle theme selection from the drop-down


def on_theme_select(*args):
    selected_theme = theme_var.get()
    apply_theme(selected_theme)


# Create the OptionMenu widget
theme_menu = tk.OptionMenu(btn_frame, theme_var, *
                           themes, command=on_theme_select)
theme_menu.config(width=15, bg="#404040", fg="white")
theme_menu.grid(row=3, column=0, padx=5, pady=5)

# Apply the initial theme after all widgets are created
apply_theme(current_theme)

# Start checking the mouse position
check_mouse()

# Start the GUI loop
root.mainloop()
