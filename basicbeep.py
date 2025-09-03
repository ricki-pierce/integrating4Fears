#This code creates a start button which is to be used outside of QTM. When the start button is clicked, QTM immediately starts recording. At the same time the start button is clicked, there is 500 milliseconds
#of silence. Then there is a beep at 500Hz which plays for 500 milliseconds. This sound corresponds to teh 500 millisecond to 1000 millisecond interval of the QTM file. 
#There is also a stop button which actually works!
#If pre set trial time set (for example, 10 seconds), then that will end the recording if the user does not stop it before then.
#Recommended that QTM set to continuous mode so user can externally stop when trial is done. 

# Import libraries we need
import asyncio  # Allows asynchronous tasks to run without blocking the main thread
import threading  # Lets us run things in the background
import numpy as np  # For math operations, here we use it to create a beep sound
import sounddevice as sd  # Plays audio (used to play the beep)
import tkinter as tk  # For making the graphical user interface (GUI)
from tkinter import messagebox  # Shows popup messages like errors
import qtm  # Controls QTM (Qualisys Track Manager), a motion capture system
import os  # Lets us change the current working directory (file location)

# Set the working directory to where QTM files might be saved (adjust as needed)
os.chdir("C:/Users/Ricki")

# Store the QTM connection globally so we can access it anywhere
qtm_connection = None

# Create a new event loop for running async code (needed for QTM and sound)
loop = asyncio.new_event_loop()

# Define a function that runs the event loop (runs in background forever)
def start_event_loop():
    asyncio.set_event_loop(loop)  # Set this as the current event loop
    loop.run_forever()  # Keep running it so we can send tasks to it anytime

# Start the event loop in the background, so it doesn’t block the GUI
threading.Thread(target=start_event_loop, daemon=True).start()

# ------------------------- QTM Start/Stop -------------------------

# Asynchronously connects to QTM and starts recording
async def start_qtm_recording():
    global qtm_connection  # Access the global connection variable
    try:
        qtm_connection = await qtm.connect("127.0.0.1")  # Connect to QTM on local machine
        print("Connected to QTM.")
        await qtm_connection.take_control("")  # Take control with an empty password
        await qtm_connection.start()  # Start the recording
        print("Recording started.")
    except Exception as e:
        # If something goes wrong, show the error
        print(f"Failed to start QTM recording: {e}")
        qtm_connection = None

# Asynchronously stops the QTM recording and disconnects
async def stop_recording():
    global qtm_connection
    if qtm_connection:  # Only try to stop if we’re connected
        try:
            await qtm_connection.stop()  # Stop the recording
            print("Recording stopped.")
            qtm_connection.disconnect()  # Disconnect from QTM
            print("Disconnected from QTM.")
            qtm_connection = None  # Clear the connection
        except Exception as e:
            # If stopping fails, show an error message in a popup
            print(f"Failed to stop QTM recording: {e}")
            def show_error():
                messagebox.showerror("Error", "Failed to stop recording.")
            root.after(0, show_error)
    else:
        print("No active connection to stop.")  # Nothing to stop

# ------------------------- Beep Logic -------------------------

# This function creates and plays a 500Hz beep for 0.5 seconds (blocking the thread until done)
def play_beep_blocking():
    fs = 44100  # Sample rate (samples per second)
    duration = 0.5  # Beep duration in seconds
    frequency = 500  # Frequency of the beep in Hz
    # Create time values from 0 to 0.5 seconds
    t = np.linspace(0, duration, int(fs * duration), False)
    # Create the beep sound using a sine wave
    beep = 0.5 * np.sin(2 * np.pi * frequency * t)
    # Play the sound
    sd.play(beep, fs)
    # Wait until the beep finishes before continuing
    sd.wait()

# Starts the QTM recording, waits 500 ms, then plays the beep
async def start_recording_and_beep():
    await start_qtm_recording()  # Start the recording
    if qtm_connection is None:
        # If connection failed, show error popup
        def show_error():
            messagebox.showerror("Error", "Failed to start recording.")
        root.after(0, show_error)
        return
    await asyncio.sleep(0.5)  # Wait 500 milliseconds of silence
    await asyncio.to_thread(play_beep_blocking)  # Play the beep in a separate thread

# ------------------------- GUI Logic -------------------------

# Called when the Start button is clicked
def on_start_button():
    # Run the async recording + beep function in the event loop
    asyncio.run_coroutine_threadsafe(start_recording_and_beep(), loop)

# Called when the Stop button is clicked
def on_stop_button():
    # Run the async stop function in the event loop
    asyncio.run_coroutine_threadsafe(stop_recording(), loop)

# Called when the user closes the window
def on_close():
    # Stop the event loop and close the window
    loop.call_soon_threadsafe(loop.stop)
    root.destroy()

# Build the window and buttons
def build_gui():
    global root
    root = tk.Tk()  # Create the main window
    root.title("QTM Controller")  # Title at top of window

    # Create the Start button
    start_btn = tk.Button(root, text="Start Recording", command=on_start_button, width=25, height=3)
    start_btn.pack(pady=10, padx=20)  # Add some space around the button

    # Create the Stop button
    stop_btn = tk.Button(root, text="Stop Recording", command=on_stop_button, width=25, height=3)
    stop_btn.pack(pady=10, padx=20)

    # Make sure the program handles the window close properly
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Start the GUI loop (waits for user interaction)
    root.mainloop()

# ------------------------- Entry Point -------------------------

# If this file is being run directly, build and start the GUI
if __name__ == "__main__":
    build_gui()
