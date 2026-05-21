"""
EyeFrameStepper plugin for Neon Player
---------------------------------------
- Shift+Right / Shift+Left steps the 200Hz eye/sensor camera (~5ms per step)
- Toggle "Eye only mode" to replace the scene camera view with the eye camera
- Current eye frame index and timestamp shown as overlay
- Frame index updates automatically on timeline clicks / any seek
"""

import logging
import numpy as np

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter

from pupil_labs.neon_player import Plugin
from pupil_labs.neon_recording.sample import match_ts

ACTION_FWD  = "&Playback/Next scene frame"
ACTION_BACK = "&Playback/Previous scene frame"


class EyeFrameStepper(Plugin):
    label = "Eye Frame Stepper (200Hz)"

    def __init__(self) -> None:
        super().__init__()
        self.render_layer = 100
        self._eye_only_mode = False
        self._current_eye_idx = 0
        self._shortcuts_hooked = False

        self.app.recording_loaded.connect(self._on_recording_loaded)

    def _on_recording_loaded(self, recording) -> None:
        QTimer.singleShot(50, self._hook_shortcuts)

    def _hook_shortcuts(self) -> None:
        if self._shortcuts_hooked:
            return

        mw = self.app.main_window
        try:
            action_fwd  = mw.get_action(ACTION_FWD)
            action_back = mw.get_action(ACTION_BACK)
        except ValueError as e:
            logging.error(f"EyeFrameStepper: could not find action - {e}")
            return

        try:
            action_fwd.triggered.disconnect()
        except RuntimeError:
            pass
        action_fwd.triggered.connect(lambda: self._step_eye(+1))

        try:
            action_back.triggered.disconnect()
        except RuntimeError:
            pass
        action_back.triggered.connect(lambda: self._step_eye(-1))

        self._shortcuts_hooked = True
        logging.info("EyeFrameStepper: Shift+Left / Shift+Right now step the 200Hz eye camera")

    def _unhook_shortcuts(self) -> None:
        if not self._shortcuts_hooked:
            return

        mw = self.app.main_window
        try:
            action_fwd  = mw.get_action(ACTION_FWD)
            action_back = mw.get_action(ACTION_BACK)
        except ValueError:
            return

        try:
            action_fwd.triggered.disconnect()
        except RuntimeError:
            pass
        action_fwd.triggered.connect(lambda: self.app.seek_by_frame(+1))

        try:
            action_back.triggered.disconnect()
        except RuntimeError:
            pass
        action_back.triggered.connect(lambda: self.app.seek_by_frame(-1))

        self._shortcuts_hooked = False

    def on_disabled(self) -> None:
        self._unhook_shortcuts()
        try:
            self.app.recording_loaded.disconnect(self._on_recording_loaded)
        except RuntimeError:
            pass

    # -- Eye stepping ----------------------------------------------------------

    def _get_eye_timestamps(self):
        if self.recording is None:
            return None
        return self.recording.eye.time

    def _eye_index_for_ts(self, ts: int) -> int:
        """Return the eye-camera frame index closest to (but not after) *ts*.

        This is called on every render so the displayed frame number always
        reflects the true playhead position — whether the user stepped with
        Shift+Arrow or clicked anywhere on the timeline.
        """
        ts_array = self._get_eye_timestamps()
        if ts_array is None or len(ts_array) == 0:
            return 0
        result = match_ts([ts], ts_array, "backward", None)[0]
        return 0 if np.isnan(result) else int(result)

    def _step_eye(self, delta: int) -> None:
        ts_array = self._get_eye_timestamps()
        if ts_array is None or len(ts_array) == 0:
            return

        current = self.app.current_ts
        result  = match_ts([current], ts_array, "backward", None)[0]
        idx     = 0 if np.isnan(result) else int(result)

        new_idx = max(0, min(idx + delta, len(ts_array) - 1))
        new_ts  = int(ts_array[new_idx])
        self._current_eye_idx = new_idx

        self.app.seek_to(new_ts)

    # -- Rendering -------------------------------------------------------------

    def render(self, painter: QPainter, time_in_recording: int) -> None:
        if self.recording is None:
            return

        # Always sync the frame index to the current playhead — this makes
        # timeline seeks (clicks, drags, external jumps) update the counter
        # automatically, without breaking Shift+Arrow stepping.
        self._current_eye_idx = self._eye_index_for_ts(time_in_recording)

        if self._eye_only_mode:
            self._render_eye_only(painter, time_in_recording)
        else:
            self._render_overlay_text(painter, time_in_recording)

    def _render_eye_only(self, painter: QPainter, time_in_recording: int) -> None:
        from pupil_labs.neon_player.utilities import qimage_from_frame

        eye_frame = self.recording.eye.sample([time_in_recording])[0]
        if eye_frame is None:
            return

        scene_w = self.recording.scene.width
        scene_h = self.recording.scene.height

        painter.fillRect(0, 0, scene_w, scene_h, QColor("black"))

        img = qimage_from_frame(eye_frame.gray)
        scaled = img.scaled(
            scene_w, scene_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (scene_w - scaled.width())  // 2
        y = (scene_h - scaled.height()) // 2
        painter.drawImage(x, y, scaled)

        ts_array = self._get_eye_timestamps()
        total    = len(ts_array) if ts_array is not None else 0
        ts_ns    = time_in_recording

        painter.setOpacity(0.8)
        painter.fillRect(0, 0, scene_w, 36, QColor("black"))
        painter.setOpacity(1.0)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Monospace", 14))
        painter.drawText(
            8, 24,
            f"EYE CAM  |  frame {self._current_eye_idx} / {total - 1}"
            f"  |  {ts_ns:.2f} ns  |  Shift+Left/Right to step"
        )

    def _render_overlay_text(self, painter: QPainter, time_in_recording: int) -> None:
        """Small status bar in the top-left corner in normal mode."""
        ts_array = self._get_eye_timestamps()
        if ts_array is None:
            return

        total = len(ts_array)
        ts_ms = time_in_recording / 1e6

        painter.setOpacity(0.75)
        painter.fillRect(0, 0, 500, 28, QColor("black"))
        painter.setOpacity(1.0)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Monospace", 13))
        painter.drawText(
            6, 20,
            f"Eye frame {self._current_eye_idx}/{total - 1}  |  {ts_ms:.2f} ms  [200Hz]"
        )

    # -- Plugin panel property -------------------------------------------------

    @property
    def eye_only_mode(self) -> bool:
        """Replace the scene camera with the eye camera view. Uncheck to restore."""
        return self._eye_only_mode

    @eye_only_mode.setter
    def eye_only_mode(self, value: bool) -> None:
        self._eye_only_mode = value
        self.app.main_window.video_widget.update()
