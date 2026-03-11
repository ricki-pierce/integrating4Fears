import pupil_labs.neon_recording as nr
import json
import os
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURATION — fill in per trial
# ─────────────────────────────────────────────

trials = [
    {
        "trial_id": "trial_01",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_1",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial1_marjergrounded.json",
        "frame_of_impact_neon": 242,   # from VirtualDub2
        "frame_of_impact_qtm": 954,    # from QTM
        "neon_fps": 30,               # eye camera frame rate
        "qtm_fps": 120,                # QTM capture frame rate
    },
    {
        "trial_id": "trial_02",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_2",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial2_marjergrounded.json",
        "frame_of_impact_neon": 134,
        "frame_of_impact_qtm": 898,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_03",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_3",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial3_marjergrounded.json",
        "frame_of_impact_neon": 201,
        "frame_of_impact_qtm": 806,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_04",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_4",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial4_marjergrounded.json",
        "frame_of_impact_neon": 163,
        "frame_of_impact_qtm": 619,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_05",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_5",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial5_marjergrounded.json",
        "frame_of_impact_neon": 186,
        "frame_of_impact_qtm": 721,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_06",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_7",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial8_marjergrounded.json",
        "frame_of_impact_neon": 195,
        "frame_of_impact_qtm": 746,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_07",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_8",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial9_marjergrounded.json",
        "frame_of_impact_neon": 209,
        "frame_of_impact_qtm": 811,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_08",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_9",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial10_marjergrounded.json",
        "frame_of_impact_neon": 180,
        "frame_of_impact_qtm": 712,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_09",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_10",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial11_marjergrounded.json",
        "frame_of_impact_neon": 207,
        "frame_of_impact_qtm": 785,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_10",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_11",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial12_marjergrounded.json",
        "frame_of_impact_neon": 183,
        "frame_of_impact_qtm": 732,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_11",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_12",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial13_marjergrounded.json",
        "frame_of_impact_neon": 230,
        "frame_of_impact_qtm": 900,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_12",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_13",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial14_marjergrounded.json",
        "frame_of_impact_neon": 207,
        "frame_of_impact_qtm": 808,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_13",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_14",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial15_marjergrounded.json",
        "frame_of_impact_neon": 220,
        "frame_of_impact_qtm": 865,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_14",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_15",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial16_marjergrounded.json",
        "frame_of_impact_neon": 202,
        "frame_of_impact_qtm": 787,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_15",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_16",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial17_marjergrounded.json",
        "frame_of_impact_neon": 218,
        "frame_of_impact_qtm": 855,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_16",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_17",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial18_marjergrounded.json",
        "frame_of_impact_neon": 224,
        "frame_of_impact_qtm": 898,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_17",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_18",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial19_marjergrounded.json",
        "frame_of_impact_neon": 221,
        "frame_of_impact_qtm": 859,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_18",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_19",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial20_marjergrounded.json",
        "frame_of_impact_neon": 228,
        "frame_of_impact_qtm": 915,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_19",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_20",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial21_marjergrounded.json",
        "frame_of_impact_neon": 225,
        "frame_of_impact_qtm": 892,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_20",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_21",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial22_marjergrounded.json",
        "frame_of_impact_neon": 223,
        "frame_of_impact_qtm": 881,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_21",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_22",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial23_marjergrounded.json",
        "frame_of_impact_neon": 210,
        "frame_of_impact_qtm": 830,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_22",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_23",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial24_marjergrounded.json",
        "frame_of_impact_neon": 234,
        "frame_of_impact_qtm": 918,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_23",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_24",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial25_marjergrounded.json",
        "frame_of_impact_neon": 234,
        "frame_of_impact_qtm": 901,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_24",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_25",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial26_marjergrounded.json",
        "frame_of_impact_neon": 216,
        "frame_of_impact_qtm": 850,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
    {
        "trial_id": "trial_25",
        "neon_recording_path": r"C:\Users\ricki\OneDrive\Desktop\PupilLabDelay\Native Recording Data\large_marker_drop_trial_26",
        "metadata_path": r"C:\Users\ricki\OneDrive\Desktop\Faran Method\Large - calib to ground\metadata json\metadata_drop_Trial27_marjergrounded.json",
        "frame_of_impact_neon": 226,
        "frame_of_impact_qtm": 898,
        "neon_fps": 30,
        "qtm_fps": 120,
    },
]
# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────

results = []

for trial in trials:
    trial_id = trial["trial_id"]

    # --- Load metadata ---
    with open(trial["metadata_path"], "r") as f:
        metadata = json.load(f)

    pc_time_qtm_start_ms       = metadata["pc_time_qtm_start_ms"]
    phone_to_pc_time_offset_ms = metadata["phone_to_pc_time_offset_ms"]

    # --- Load Pupil recording and get first eye frame UTC timestamp ---
    # (Replicating colleague's exact approach)
    recording = nr.open(trial["neon_recording_path"])
    first_eye_frame_utc_ms = recording.eye.time[0] / 1e6  # convert microseconds → milliseconds
    

    # --- Calculate Neon impact time on PHONE clock ---
    ms_per_neon_frame = 1000 / trial["neon_fps"]   # e.g. 5ms at 200Hz
    impact_time_phone_ms = first_eye_frame_utc_ms + (trial["frame_of_impact_neon"] * ms_per_neon_frame)

    # --- Convert Neon impact time to PC clock ---
    # (same as colleague: add the laptop_to_neon_time_offset)
    impact_time_pc_neon_ms = impact_time_phone_ms + phone_to_pc_time_offset_ms

    # --- Calculate QTM impact time on PC clock ---
    ms_per_qtm_frame = 1000 / trial["qtm_fps"]     # e.g. 8.333ms at 120Hz
    impact_time_pc_qtm_ms = pc_time_qtm_start_ms + (trial["frame_of_impact_qtm"] * ms_per_qtm_frame)

    # --- Calculate offset ---
    # Negative = Neon sees the event LATER than QTM (Neon lags)
    offset_ms = impact_time_pc_qtm_ms - impact_time_pc_neon_ms

    results.append({
        "trial_id":                  trial_id,
        "first_eye_frame_utc_ms":    first_eye_frame_utc_ms,
        "impact_time_phone_ms":      impact_time_phone_ms,
        "impact_time_pc_neon_ms":    impact_time_pc_neon_ms,
        "impact_time_pc_qtm_ms":     impact_time_pc_qtm_ms,
        "offset_ms":                 offset_ms,
    })

    print(f"[{trial_id}] QTM impact (PC clock): {impact_time_pc_qtm_ms:.2f} ms")
    print(f"[{trial_id}] Neon impact (PC clock): {impact_time_pc_neon_ms:.2f} ms")
    print(f"[{trial_id}] Offset (QTM - Neon):    {offset_ms:.2f} ms")
    print(f"[{trial_id}] First Eye Frame:    {first_eye_frame_utc_ms:.2f} ms\n")
# ─────────────────────────────────────────────
# SUMMARY STATISTICS
# ─────────────────────────────────────────────

offsets = np.array([r["offset_ms"] for r in results])

print("=" * 40)
print("SUMMARY ACROSS ALL TRIALS")
print("=" * 40)
print(f"  N trials  : {len(offsets)}")
print(f"  Min offset: {offsets.min():.1f} ms")
print(f"  Max offset: {offsets.max():.1f} ms")
print(f"  Mean offset: {offsets.mean():.1f} ms")
print(f"  Median offset: {np.median(offsets):.1f} ms")
print(f"  Std dev:   {offsets.std():.1f} ms")
print()
print("Interpretation:")
if offsets.mean() < 0:
    print(f"  Neon lags QTM by ~{abs(offsets.mean()):.1f} ms on average.")
    print(f"  i.e. an event at t=830ms in Neon occurred at ~t={830 + offsets.mean():.0f}ms in QTM.")
else:
    print(f"  Neon leads QTM by ~{offsets.mean():.1f} ms on average.")
