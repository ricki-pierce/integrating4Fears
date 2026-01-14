#This is stand alone code to make sure the Neon glasses work properly

import time
import threading
import tkinter as tk
from tkinter import messagebox

from pupil_labs.realtime_api.simple import discover_one_device


class NeonControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Eye Tracking Controller")

        self.device = None
        self.recording_id = None

        # Buttons
        tk.Button(root, text="Connect to Neon", command=self.connect).pack(fill="x")
        tk.Button(root, text="Start Recording", command=self.start_recording).pack(fill="x")
        tk.Button(root, text="Stop & Save Recording", command=self.stop_and_save).pack(fill="x")
        tk.Button(root, text="Cancel Recording", command=self.cancel_recording).pack(fill="x")
        tk.Button(root, text="Send Event", command=self.send_event).pack(fill="x")
        tk.Button(root, text="Check Errors", command=self.check_errors).pack(fill="x")

        self.status = tk.Label(root, text="Status: Disconnected")
        self.status.pack(fill="x")

    def connect(self):
        self.status.config(text="Status: Searching for device...")
        self.root.update()

        self.device = discover_one_device(max_search_duration_seconds=10)

        if self.device is None:
            messagebox.showerror("Error", "No Neon device found")
            self.status.config(text="Status: Disconnected")
        else:
            self.status.config(text="Status: Connected to Neon")

    def start_recording(self):
        if not self.device:
            messagebox.showwarning("Warning", "Connect to device first")
            return

        self.recording_id = self.device.recording_start()
        self.status.config(text=f"Recording started: {self.recording_id}")

    def stop_and_save(self):
        if not self.device:
            return

        self.device.recording_stop_and_save()
        self.status.config(text="Recording stopped & saved")

    def cancel_recording(self):
        if not self.device:
            return

        self.device.recording_cancel()
        self.status.config(text="Recording canceled")

    def send_event(self):
        if not self.device:
            return

        event = self.device.send_event("GUI button pressed")
        self.status.config(text=f"Event sent at {event.datetime}")

    def check_errors(self):
        if not self.device:
            return

        errors = list(self.device.get_errors())
        if not errors:
            messagebox.showinfo("Errors", "No errors reported")
        else:
            messagebox.showerror("Errors", "\n".join(str(e) for e in errors))


if __name__ == "__main__":
    root = tk.Tk()
    app = NeonControllerGUI(root)
    root.mainloop()
