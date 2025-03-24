import tkinter as tk
from tkinter import messagebox
import subprocess
from datetime import datetime, timedelta
import json
import os
import socket

# Constants
DEFAULT_MAX_MINUTES = 180  # Default slider max (3 hours)
TICK_INTERVAL = 30  # minutes between markers
SLIDER_LENGTH = 440  # length for the slider widget
MARGIN = 30  # extra space on the sides to ensure text is not cut off
DETECTION_RADIUS = 200  # extra pixels around the window for mouse detection

# Global variables
invisibility_enabled = False
current_theme = "dark_grey"  # Default theme
slider_max = DEFAULT_MAX_MINUTES  # Initial slider max
using_custom_time = False  # Track if we're using custom time input
current_shutdown_minutes = 0  # Track current shutdown time

# Configuration file to save preferences
CONFIG_FILE = "config.json"


def get_device_name():
    try:
        return socket.gethostname()
    except:
        return "User"


def load_config():
    global current_theme
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            current_theme = config.get("theme", "dark_grey")


def save_config():
    with open(CONFIG_FILE, "w") as file:
        json.dump({"theme": current_theme}, file)


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

    root.configure(bg=bg_color)
    greeting_label.configure(bg=bg_color, fg=fg_color)
    main_frame.configure(bg=bg_color)
    instr_label.configure(bg=bg_color, fg=fg_color)
    slider_frame.configure(bg=bg_color)
    tick_canvas.configure(bg=bg_color)
    if hasattr(slider, 'winfo_exists') and slider.winfo_exists():
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
    toggle_time_button.configure(bg=trough_color, fg=fg_color)

    save_config()


def toggle_time_input():
    global using_custom_time
    if not using_custom_time:
        using_custom_time = True
        slider_frame.pack_forget()
        custom_time_frame.pack(pady=(10, 20))
        toggle_time_button.config(text="Use Preset Slider Time")
        # Clear and focus the hours entry
        hours_entry.delete(0, tk.END)
        minutes_entry.delete(0, tk.END)
        hours_entry.focus_set()
    else:
        using_custom_time = False
        custom_time_frame.pack_forget()
        slider_frame.pack()
        toggle_time_button.config(text="Use Custom Time")
        update_time_display(slider.get())


def set_custom_time():
    try:
        hours = int(hours_entry.get() or 0)
        minutes = int(minutes_entry.get() or 0)
        total_minutes = hours * 60 + minutes
        if total_minutes < 0:
            raise ValueError("Time cannot be negative")
        update_time_display(total_minutes)
    except ValueError as e:
        messagebox.showerror(
            "Invalid Input", f"Please enter valid numbers for hours and minutes.\nError: {e}")


def update_time_display(minutes):
    global current_shutdown_minutes
    current_shutdown_minutes = minutes
    future_time = datetime.now() + timedelta(minutes=minutes)
    time_label.config(
        text=f"Shutdown at: {future_time.strftime('%I:%M:%S %p')}")


def cancel_shutdown():
    subprocess.call("shutdown -a", shell=True)
    messagebox.showinfo("Cancelled", "Shutdown has been cancelled.")
    schedule_button.config(state=tk.NORMAL)
    if not using_custom_time:
        slider.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)


def prompt_cancel():
    answer = messagebox.askyesno("Cancel Shutdown?",
                                 "Shutdown is scheduled soon.\nDo you want to cancel it?")
    if answer:
        cancel_shutdown()


def schedule_shutdown():
    global current_shutdown_minutes

    try:
        if using_custom_time:
            hours = int(hours_entry.get() or 0)
            minutes = int(minutes_entry.get() or 0)
            current_shutdown_minutes = hours * 60 + minutes
        else:
            current_shutdown_minutes = int(slider.get())
    except ValueError:
        current_shutdown_minutes = 0

    total_seconds = current_shutdown_minutes * 60

    if total_seconds == 0:
        if not messagebox.askyesno("Confirm", "Shut down immediately?"):
            return

    schedule_button.config(state=tk.DISABLED)
    if not using_custom_time:
        slider.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)

    if total_seconds > 180:
        delay_before_prompt = (total_seconds - 180) * 1000
        root.after(delay_before_prompt, prompt_cancel)

    command = f"shutdown -s -t {total_seconds}"
    try:
        subprocess.Popen(command, shell=True)
        update_time_display(current_shutdown_minutes)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to schedule shutdown: {e}")
        schedule_button.config(state=tk.NORMAL)
        if not using_custom_time:
            slider.config(state=tk.NORMAL)
        cancel_button.config(state=tk.DISABLED)


def check_mouse():
    if invisibility_enabled:
        pointer_x, pointer_y = root.winfo_pointerx(), root.winfo_pointery()
        win_x = root.winfo_rootx()
        win_y = root.winfo_rooty()
        win_w = root.winfo_width()
        win_h = root.winfo_height()

        if (win_x - DETECTION_RADIUS <= pointer_x <= win_x + win_w + DETECTION_RADIUS and
                win_y - DETECTION_RADIUS <= pointer_y <= win_y + win_h + DETECTION_RADIUS):
            root.attributes("-alpha", 1.0)
        else:
            root.attributes("-alpha", 0.0)
    root.after(300, check_mouse)


def toggle_invisibility():
    global invisibility_enabled
    invisibility_enabled = not invisibility_enabled
    if invisibility_enabled:
        toggle_button.config(text="Disable Invisibility")
        invisibility_label.config(
            text="Move your mouse away to make me invisible")
    else:
        toggle_button.config(text="Enable Invisibility")
        root.attributes("-alpha", 1.0)
        invisibility_label.config(text="")


# Main window setup
root = tk.Tk()
root.title("Lazy Shutdown")
root.geometry("700x550")
root.attributes("-topmost", True)

# Add greeting label
greeting_label = tk.Label(root,
                          text=f"Hello, {get_device_name()}!",
                          font=("Helvetica", 14, "bold"),
                          bg="#2E2E2E",
                          fg="white",
                          pady=10)
greeting_label.pack(fill=tk.X)

load_config()

# Main frame
main_frame = tk.Frame(root, padx=20, pady=20, bg="#2E2E2E")
main_frame.pack(fill=tk.BOTH, expand=True)

# Instruction label
instr_label = tk.Label(main_frame, text="Select delay for shutdown:", font=(
    "Helvetica", 12), bg="#2E2E2E", fg="white")
instr_label.pack(pady=(0, 10))

# Slider frame
slider_frame = tk.Frame(main_frame, bg="#2E2E2E")
slider_frame.pack()

# Slider widgets
tick_canvas = tk.Canvas(slider_frame, width=SLIDER_LENGTH +
                        2*MARGIN, height=30, bg="#2E2E2E", highlightthickness=0)
tick_canvas.pack()

slider = tk.Scale(slider_frame, from_=0, to=DEFAULT_MAX_MINUTES, orient=tk.HORIZONTAL,
                  length=SLIDER_LENGTH, showvalue=0, command=update_time_display,
                  bg="#2E2E2E", fg="white", troughcolor="#404040")
slider.pack(pady=5)

marker_canvas = tk.Canvas(slider_frame, width=SLIDER_LENGTH +
                          2*MARGIN, height=20, bg="#2E2E2E", highlightthickness=0)
marker_canvas.pack()

label_canvas = tk.Canvas(slider_frame, width=SLIDER_LENGTH +
                         2*MARGIN, height=20, bg="#2E2E2E", highlightthickness=0)
label_canvas.pack()


def update_slider_ticks():
    tick_canvas.delete("all")
    marker_canvas.delete("all")
    label_canvas.delete("all")
    pixels_per_minute = SLIDER_LENGTH / slider_max

    for minute in range(0, slider_max + 1, TICK_INTERVAL):
        x = MARGIN + minute * pixels_per_minute
        tick_canvas.create_text(x, 10, text=str(minute), font=(
            "Helvetica", 10), anchor=tk.CENTER, fill="white")
        marker_canvas.create_line(x, 0, x, 20, width=2, fill="white")

    for hour in range(0, (slider_max // 60) + 1):
        minutes = hour * 60
        x = MARGIN + minutes * pixels_per_minute
        label_text = f"{hour} hour{'s' if hour != 1 else ''}"
        label_canvas.create_text(x, 10, text=label_text, font=(
            "Helvetica", 10), anchor=tk.CENTER, fill="white")


update_slider_ticks()

# Time display label
time_label = tk.Label(main_frame, text="Shutdown at: Not scheduled", font=(
    "Helvetica", 14), bg="#2E2E2E", fg="white")
time_label.pack(pady=(15, 10))

# Custom time frame (initially hidden)
custom_time_frame = tk.Frame(main_frame, bg="#2E2E2E")

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

# Button frame
btn_frame = tk.Frame(main_frame, bg="#2E2E2E")
btn_frame.pack(pady=10)

schedule_button = tk.Button(btn_frame, text="Schedule Shutdown",
                            command=schedule_shutdown, width=18, bg="#404040", fg="white")
schedule_button.grid(row=0, column=0, padx=5)

cancel_button = tk.Button(btn_frame, text="Cancel Shutdown", command=cancel_shutdown,
                          state=tk.DISABLED, width=18, bg="#404040", fg="white")
cancel_button.grid(row=0, column=1, padx=5)

toggle_time_button = tk.Button(btn_frame, text="Use Custom Time",
                               command=toggle_time_input, width=18, bg="#404040", fg="white")
toggle_time_button.grid(row=1, column=0, padx=5, pady=5)

toggle_button = tk.Button(btn_frame, text="Enable Invisibility",
                          command=toggle_invisibility, width=18, bg="#404040", fg="white")
toggle_button.grid(row=1, column=1, padx=5, pady=5)

invisibility_label = tk.Label(btn_frame, text="", font=(
    "Helvetica", 10), bg="#2E2E2E", fg="white")
invisibility_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))

# Theme selection
themes = ["white", "light_grey", "dark_grey", "black"]
theme_var = tk.StringVar(value=current_theme)


def on_theme_select(*args):
    selected_theme = theme_var.get()
    apply_theme(selected_theme)


theme_menu = tk.OptionMenu(btn_frame, theme_var, *
                           themes, command=on_theme_select)
theme_menu.config(width=15, bg="#404040", fg="white")
theme_menu.grid(row=3, column=0, padx=5, pady=5)

# Apply initial theme
apply_theme(current_theme)

# Start mouse checking
check_mouse()

root.mainloop()
