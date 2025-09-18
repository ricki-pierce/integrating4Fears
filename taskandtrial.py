"""
Integrated QTM + Arduino (Seesaw Buttons) + Excel Logger + Task Manager

Workflow:
---------
1. Launch script → GUI appears.
2. Click "Start Task" → prompted for Task Name (e.g., "Cup Grab").
3. Message appears: "Ready to begin Cup Grab trials".
4. GUI shows Start Trial, Stop Trial, End Task.
5. Start Trial → QTM starts recording, beep plays, random LED lights.
6. Stop Trial → QTM stops, automatically saves as "Cup Grab 1", "Cup Grab 2", etc.
   - QTM resets so you can immediately run another trial.
7. End Task → resets task state. You can start a new task (e.g., "LED Buttons").
   Trials save as "LED Buttons 1", "LED Buttons 2", etc.
8. End & Save → closes GUI and exports Excel log.
"""

# --- Integrated QTM + Arduino (Seesaw Buttons) + Excel Logger ---
import asyncio
import threading
import serial
import time
import random
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import simpledialog, messagebox
from openpyxl import Workbook
from datetime import datetime
import qtm
import os
import soundfile as sf
import subprocess
import pytz

# ------------------ CONFIG ------------------
SERIAL_PORT = 'COM10'
BAUD_RATE = 115200
WORK_DIR = r"C:\Users\AoMV Lab\ricki projects"
os.chdir(WORK_DIR)

def sync_windows_time():
    try:
        output = subprocess.check_output(['w32tm', '/resync'],
                                         shell=True,
                                         stderr=subprocess.STDOUT,
                                         text=True)
        print(f"Time sync success:\n{output}")
    except subprocess.CalledProcessError as e:
        print(f"Time sync failed:\n{e.output}")

CENTRAL_TZ = pytz.timezone('America/Chicago')
def now_central():
    return datetime.now(CENTRAL_TZ)

# ------------------ GLOBALS ------------------
qtm_connection = None
loop = asyncio.new_event_loop()

arduino = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
time.sleep(2)

event_log = []
press_times = {}

# Task + trial state
task_name = None
trial_number = 0
button_pool = []
current_button = None
num_buttons = 0

# ------------------ EVENT LOOP ------------------
def start_event_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_event_loop, daemon=True).start()

# ------------------ QTM CONTROL ------------------
async def start_qtm_recording():
    global qtm_connection
    try:
        qtm_connection = await qtm.connect("127.0.0.1")
        print("Connected to QTM.")
        await qtm_connection.take_control("")
        await qtm_connection.start()
        print("Recording started.")
    except Exception as e:
        print(f"Failed to start QTM recording: {e}")
        qtm_connection = None

async def stop_qtm_recording():
    global qtm_connection, task_name, trial_number
    if qtm_connection:
        try:
            await qtm_connection.stop()
            print("Recording stopped.")

            # Save automatically with task + trial number
            save_name = f"{task_name} {trial_number}"
            await qtm_connection.save(save_name)
            print(f"Recording saved as {save_name}.")

            await qtm_connection.release_control()
            qtm_connection.disconnect()
            print("QTM reset and ready for next trial.")
            qtm_connection = None
        except Exception as e:
            print(f"Failed to stop/save QTM recording: {e}")
            def show_error():
                messagebox.showerror("Error", "Failed to stop/save recording.")
            root.after(0, show_error)

# ------------------ BEEP ------------------
def play_beep_blocking():
    filename = r"C:\Users\AoMV Lab\ricki projects\Silenceplus500hz1000mstone.wav"
    data, fs = sf.read(filename, dtype='float32')
    event_log.append((trial_number, current_button, now_central().strftime('%H:%M:%S.%f')[:-3],
                      "Beep Started", None))
    sd.play(data, fs)
    sd.wait()

# ------------------ SERIAL READER ------------------
def read_serial():
    global trial_number, current_button
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode(errors='ignore').strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue

            event = parts[0]
            arduino_ms = int(parts[1])
            system_time = now_central().strftime('%H:%M:%S.%f')[:-3]

            if "_pressed" in event:
                button = event.split("_")[1]
                press_times[button] = arduino_ms
                event_text = f"#{button} - pressed"
                event_log.append((trial_number, current_button, system_time, event_text, None))
                print(f"[Trial {trial_number}] Button {current_button} [{system_time}] {event_text}")
                if current_button is not None:
                    arduino.write(f"LED_{current_button}_OFF\n".encode())

            elif "_released" in event:
                button = event.split("_")[1]
                if button in press_times:
                    duration = arduino_ms - press_times[button]
                    event_text = f"#{button} - released"
                    event_log.append((trial_number, current_button, system_time, event_text, duration))
                    print(f"[Trial {trial_number}] Button {current_button} [{system_time}] {event_text} (Duration: {duration} ms)")
                    del press_times[button]

serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# ------------------ TRIAL CONTROL ------------------
async def start_recording_and_trial():
    global trial_number, current_button, button_pool

    if not button_pool:
        messagebox.showinfo("Done", "All buttons have been used.")
        return

    trial_number += 1
    event_log.append((trial_number, None, now_central().strftime('%H:%M:%S.%f')[:-3],
                      "QTM Start Command Sent", None)) 

    await start_qtm_recording()
    if qtm_connection is None:
        def show_error():
            messagebox.showerror("Error", "Failed to start recording.")
        root.after(0, show_error)
        return
        
    event_log.append((trial_number, None, now_central().strftime('%H:%M:%S.%f')[:-3],
                      "QTM Recording Started", None))

    await asyncio.sleep(0.5)

    current_button = random.choice(button_pool)
    button_pool.remove(current_button)

    beep_thread = threading.Thread(target=play_beep_blocking, daemon=True)
    beep_thread.start()

    await asyncio.sleep(0.01)
    arduino.write(f"LED_{current_button}_ON\n".encode())
    arduino.flush()
    
    event_log.append((trial_number, current_button, now_central().strftime('%H:%M:%S.%f')[:-3],
                      f"LED_{current_button}_Lit", None))

    print(f"Trial {trial_number}: Beep played & Button {current_button} lit")

# GUI button actions
def on_start_task():
    global task_name, trial_number, button_pool, num_buttons
    task_name = simpledialog.askstring("Start Task", "Enter task name:")
    if not task_name:
        return
    trial_number = 0
    num_buttons = simpledialog.askinteger("Setup", "How many Seesaw buttons are connected? (1-4)", minvalue=1, maxvalue=4)
    button_pool = list(range(1, num_buttons + 1))
    messagebox.showinfo("Task Ready", f"Ready to begin {task_name} trials.")

def on_start_trial():
    if not task_name:
        messagebox.showwarning("No Task", "Start a task first.")
        return
    asyncio.run_coroutine_threadsafe(start_recording_and_trial(), loop)

def on_stop_trial():
    asyncio.run_coroutine_threadsafe(stop_qtm_recording(), loop)

def on_end_task():
    global task_name, trial_number
    task_name = None
    trial_number = 0
    messagebox.showinfo("Task Ended", "You can start a new task.")

def on_end_button():
    export_to_excel()
    loop.call_soon_threadsafe(loop.stop)
    root.destroy()

# ------------------ EXCEL EXPORT ------------------
def export_to_excel():
    if not event_log:
        messagebox.showwarning("No Data", "No events to export.")
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "Trials"
    ws.append(["Trial", "Button Lit", "Timestamp", "Event", "Duration (ms)"])
    for trial, button, timestamp, event, duration in event_log:
        ws.append([trial, button, timestamp, event, duration])
    filename = f"trial_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    messagebox.showinfo("Export Successful", f"Saved as {filename}")

# ------------------ GUI ------------------
def build_gui():
    global root
    root = tk.Tk()
    root.title("QTM + Seesaw Trial Controller")

    task_btn = tk.Button(root, text="Start Task", command=on_start_task, width=25, height=3)
    task_btn.pack(pady=10, padx=20)

    start_btn = tk.Button(root, text="Start Trial", command=on_start_trial, width=25, height=3)
    start_btn.pack(pady=10, padx=20)

    stop_btn = tk.Button(root, text="Stop Trial", command=on_stop_trial, width=25, height=3)
    stop_btn.pack(pady=10, padx=20)

    endtask_btn = tk.Button(root, text="End Task", command=on_end_task, width=25, height=3)
    endtask_btn.pack(pady=10, padx=20)

    end_btn = tk.Button(root, text="End & Save", command=on_end_button, width=25, height=3)
    end_btn.pack(pady=10, padx=20)

    root.protocol("WM_DELETE_WINDOW", on_end_button)
    root.mainloop()

# ------------------ MAIN ------------------
if __name__ == "__main__":
    sync_windows_time()
    build_gui()
