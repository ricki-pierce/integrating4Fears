import pupil_labs.neon_recording as nr
import json
import os
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURATION — fill in per trial
# ─────────────────────────────────────────────

trials = [
    {"trial_id": "trial_01", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial1", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial1_eyecamera.json", "frame_of_impact_neon": 1968, "frame_of_impact_qtm": 1186, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_02", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial2", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial2_eyecamera.json", "frame_of_impact_neon": 2685, "frame_of_impact_qtm": 1591, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_03", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial3", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial3_eyecamera.json", "frame_of_impact_neon": 1662, "frame_of_impact_qtm": 1041, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_04", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial4", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial4_eyecamera.json", "frame_of_impact_neon": 1615, "frame_of_impact_qtm": 943, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_05", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial5", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial5_eyecamera.json", "frame_of_impact_neon": 1343, "frame_of_impact_qtm": 774, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_06", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial6", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial6_eyecamera.json", "frame_of_impact_neon": 1513, "frame_of_impact_qtm": 893, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_07", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial7", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial7_eyecamera.json", "frame_of_impact_neon": 1530, "frame_of_impact_qtm": 904, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_08", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial8", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial8_eyecamera.json", "frame_of_impact_neon": 1171, "frame_of_impact_qtm": 698, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_09", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial9", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial9_eyecamera.json", "frame_of_impact_neon": 958, "frame_of_impact_qtm": 922, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_10", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial10", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial10_eyecamera.json", "frame_of_impact_neon": 1325, "frame_of_impact_qtm": 794, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_11", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial11", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial11_eyecamera.json", "frame_of_impact_neon": 1615, "frame_of_impact_qtm": 967, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_12", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial12", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial12_eyecamera.json", "frame_of_impact_neon": 1442, "frame_of_impact_qtm": 838, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_13", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial13", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial13_eyecamera.json", "frame_of_impact_neon": 1489, "frame_of_impact_qtm": 904, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_14", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial14", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial14_eyecamera.json", "frame_of_impact_neon": 1572, "frame_of_impact_qtm": 925, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_15", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial15", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial15_eyecamera.json", "frame_of_impact_neon": 1448, "frame_of_impact_qtm": 859, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_16", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial16", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial16_eyecamera.json", "frame_of_impact_neon": 1648, "frame_of_impact_qtm": 972, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_17", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial17", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial17_eyecamera.json", "frame_of_impact_neon": 1843, "frame_of_impact_qtm": 1104, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_18", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial18", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial18_eyecamera.json", "frame_of_impact_neon": 1432, "frame_of_impact_qtm": 847, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_19", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial19", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial19_eyecamera.json", "frame_of_impact_neon": 1436, "frame_of_impact_qtm": 862, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_20", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial20", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial20_eyecamera.json", "frame_of_impact_neon": 1306, "frame_of_impact_qtm": 780, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_21", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial21", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial21_eyecamera.json", "frame_of_impact_neon": 1437, "frame_of_impact_qtm": 858, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_22", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial22", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial22_eyecamera.json", "frame_of_impact_neon": 1537, "frame_of_impact_qtm": 932, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_24", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial24", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial24_eyecamera.json", "frame_of_impact_neon": 1399, "frame_of_impact_qtm": 844, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_25", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial25", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial25_eyecamera.json", "frame_of_impact_neon": 1599, "frame_of_impact_qtm": 962, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_26", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial26", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial26_eyecamera.json", "frame_of_impact_neon": 1522, "frame_of_impact_qtm": 911, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_27", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial27", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial27_eyecamera.json", "frame_of_impact_neon": 1530, "frame_of_impact_qtm": 915, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_28", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial28", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial28_eyecamera.json", "frame_of_impact_neon": 1363, "frame_of_impact_qtm": 829, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_29", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial29", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial29_eyecamera.json", "frame_of_impact_neon": 1364, "frame_of_impact_qtm": 814, "neon_fps": 200, "qtm_fps": 120},
    {"trial_id": "trial_30", "neon_recording_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial30", "metadata_path": r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\metadata json\metadata_drop_Trial30_eyecamera.json", "frame_of_impact_neon": 1264, "frame_of_impact_qtm": 751, "neon_fps": 200, "qtm_fps": 120},

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
    info_json_path = os.path.join(trial["neon_recording_path"], "info.json")

    with open(info_json_path, "r") as f:
        info = json.load(f)

    recording = nr.open(trial["neon_recording_path"])
    first_eye_frame_utc_ms = recording.eye.time[0] / 1e6

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
    print(f"[{trial_id}] First eye Frame:    {first_eye_frame_utc_ms:.2f} ms\n")

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
else:
    print(f"  Neon leads QTM by ~{offsets.mean():.1f} ms on average.")
