# ~ pvthon3
# Pvthon 3.10.12 (main, Nov 4 2025, 08:48:33) [GCC 11.4.01 on linux 
# Type "help", "copyright", "credits" or "license" for more information. 
# >>> import pupil_labs.neon_recording as nr 
# >>> rec_path = "/home/meshincf/MVD/TaskIntegration-cpp/pupil_cloud_downloads/ 4c53431b-1cb5-47b4-a462-6941ecdfa009/recording/2025-12-15_16-28-41-4c53431b" 
# >>> recording = nr.open(rec_path) 
# >>> recording.eye.time[0] 
# 1765834122989266552
# >>> neon_start = recording.eye.time[0] 
# >>> neon_start = recording.eye.time[0]/1e6 
# >>> neon_start 
# 1765834122989.2664
# >>> neon_marker_impact = neon_start + 4000 + (160 * 5) 
# >>> neon_marker_impact_laptop = neon_marker_impact + 104 
# >>> qtm_start_laptop = 1765834126864 
# >>> qtm_marker_impact_laptop = qtm_start_laptop + (120 * 8.3333) 
# >>> qtm_marker_impact_laptop - neon_marker_impact_Laptop 
# -29.270263671875 
# >>> exit()


import pupil_labs.neon_recording as nr

# ── EDIT THESE 5 VALUES FOR EACH TRIAL ────────────────────────────────────────
rec_path              = r"C:\Users\rpier12\Desktop\Faran Method\using eye camera\PupilLabsNative\Native Recording Data eye camera\eyecamera_trial1"
frame_of_impact_neon  = 1968    # frame number of marker impact in eye-camera video (200 Hz → 5 ms/frame)
frame_of_impact_qtm   = 1186    # frame number of marker impact in QTM (120 Hz → 8.3333 ms/frame)
phone_to_pc_offset_ms = -34.74  # phone_to_pc_time_offset_ms from your metadata JSON
qtm_start_laptop      = 1773419605276.3574  # pc_time_qtm_start_ms from your metadata JSON
# ──────────────────────────────────────────────────────────────────────────────

recording  = nr.open(rec_path)
print(recording.eye.time[0])

neon_start = recording.eye.time[0] / 1e6
print(neon_start)

neon_marker_impact        = neon_start + (frame_of_impact_neon * 5)
neon_marker_impact_laptop = neon_marker_impact + phone_to_pc_offset_ms

qtm_marker_impact_laptop  = qtm_start_laptop + (frame_of_impact_qtm * 8.3333)

print(qtm_marker_impact_laptop - neon_marker_impact_laptop)
