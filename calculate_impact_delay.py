"""
Sync Offset Analysis — Updated Methodology
===========================================
Used on data files resulting from running rearranging.py

Calculates the time offset at moment of impact between Pupil Labs Neon (phone clock) and QTM
(PC clock) across multiple trials.

METHODOLOGY:
  1. QTM start time  → read "TIME_STAMP" field from each trial's .tsv file
     (PC UTC wall-clock time, e.g. "14:46:51.753")
  2. QTM impact time → QTM start time + (frame_of_impact_qtm / qtm_fps) ms
  3. Neon impact time → convert impact_timestamp_ns to UTC ms-of-day using
     the same formula as the Google Sheet:
       =TEXT(((ns/1e9)/86400)-TIME(5,0,0), "hh:mm:ss.000")
  4. Raw difference  → neon_impact_utc_ms - qtm_impact_utc_ms
  5. Adjusted offset → raw_difference + phone_to_pc_time_offset_ms

  The section start from sections.csv is shown for reference only — it is
  matched to each trial by finding the section start that falls just before
  (and closest to) that trial's Neon impact timestamp.

SIGN CONVENTION:
  Positive adjusted offset → Neon event appears later than QTM (Neon lags)
  Negative adjusted offset → Neon event appears earlier than QTM (Neon leads)

NOTES ON fps:
  qtm_fps should match the QTM capture rate (e.g. 120 Hz).
  neon_fps / eye-camera fps is NOT used here — the Neon impact timestamp is
  a raw absolute ns value read directly from the Pupil Labs video player,
  so no frame-to-ms conversion is needed for the Neon side.
"""

import csv
import json
import math
import re
from pathlib import Path
import numpy as np

# =============================================================================
# BASE PATHS — edit once
# =============================================================================
BASE_DIR      = r"C:\Users\rpier12\Desktop\Marker Test 520"
BASE_TSV_DIR  = Path(BASE_DIR) / "tsv files"
BASE_META_DIR = Path(BASE_DIR) / "metadata"
SECTIONS_CSV  = Path(BASE_DIR) / "Timeseries Data" / "sections.csv"

CDT_OFFSET_HOURS = 5   # CDT = UTC-5; matches Google Sheet -TIME(5,0,0)
QTM_FPS          = 200 # nominal QTM capture rate

# =============================================================================
# TRIAL DEFINITIONS
# For each trial fill in:
#   tsv_filename        : .tsv file in BASE_TSV_DIR
#   metadata_filename   : .json file in BASE_META_DIR
#   frame_of_impact_qtm : frame number at impact, scrubbed from QTM
#   impact_timestamp_ns : raw ns timestamp at impact, from Pupil Labs video player
#   qtm_fps             : QTM capture rate (usually same as QTM_FPS above)
# =============================================================================

trials = [
    {
        "trial_id"            : "trial_01",
        "tsv_filename"        : "drop_Trial1_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial1_ricki520.json",
        "frame_of_impact_qtm" : 1889,
        "impact_timestamp_ns" : 1779306421417500000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_02",
        "tsv_filename"        : "drop_Trial2_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial2_ricki520.json",
        "frame_of_impact_qtm" : 1873,
        "impact_timestamp_ns" : 1779306451024670000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_03",
        "tsv_filename"        : "drop_Trial3_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial3_ricki520.json",
        "frame_of_impact_qtm" : 2116,
        "impact_timestamp_ns" : 1779306482594750000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_04",
        "tsv_filename"        : "drop_Trial4_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial4_ricki520.json",
        "frame_of_impact_qtm" : 2324,
        "impact_timestamp_ns" : 1779306512511270000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_06",
        "tsv_filename"        : "drop_Trial6_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial6_ricki520.json",
        "frame_of_impact_qtm" : 1962,
        "impact_timestamp_ns" : 1779306573293120000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_07",
        "tsv_filename"        : "drop_Trial7_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial7_ricki520.json",
        "frame_of_impact_qtm" : 1967,
        "impact_timestamp_ns" : 1779306602805890000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_08",
        "tsv_filename"        : "drop_Trial8_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial8_ricki520.json",
        "frame_of_impact_qtm" : 2289,
        "impact_timestamp_ns" : 1779306633603590000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_09",
        "tsv_filename"        : "drop_Trial9_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial9_ricki520.json",
        "frame_of_impact_qtm" : 2080,
        "impact_timestamp_ns" : 1779306665409630000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_10",
        "tsv_filename"        : "drop_Trial10_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial10_ricki520.json",
        "frame_of_impact_qtm" : 2020,
        "impact_timestamp_ns" : 1779306702012930000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_11",
        "tsv_filename"        : "drop_Trial11_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial11_ricki520.json",
        "frame_of_impact_qtm" : 1906,
        "impact_timestamp_ns" : 1779306730799310000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_12",
        "tsv_filename"        : "drop_Trial12_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial12_ricki520.json",
        "frame_of_impact_qtm" : 1998,
        "impact_timestamp_ns" : 1779306760060000000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_13",
        "tsv_filename"        : "drop_Trial13_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial13_ricki520.json",
        "frame_of_impact_qtm" : 2125,
        "impact_timestamp_ns" : 1779306791493430000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_14",
        "tsv_filename"        : "drop_Trial14_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial14_ricki520.json",
        "frame_of_impact_qtm" : 1967,
        "impact_timestamp_ns" : 1779306822434740000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_15",
        "tsv_filename"        : "drop_Trial15_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial15_ricki520.json",
        "frame_of_impact_qtm" : 1948,
        "impact_timestamp_ns" : 1779306855202280000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_16",
        "tsv_filename"        : "drop_Trial16_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial16_ricki520.json",
        "frame_of_impact_qtm" : 2046,
        "impact_timestamp_ns" : 1779306885610280000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_17",
        "tsv_filename"        : "drop_Trial17_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial17_ricki520.json",
        "frame_of_impact_qtm" : 2045,
        "impact_timestamp_ns" : 1779306920582870000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_18",
        "tsv_filename"        : "drop_Trial18_ricki520.tsv",
        "metadata_filename"   : "metadata_drop_Trial18_ricki520.json",
        "frame_of_impact_qtm" : 1990,
        "impact_timestamp_ns" : 1779306951548400000,
        "qtm_fps"             : QTM_FPS,
    },
    {
        "trial_id"            : "trial_19",
        "tsv_filename"        : "drop_Trial19_ricki520.tsv",   # ← fixed (was Trial18)
        "metadata_filename"   : "metadata_drop_Trial19_ricki520.json",
        "frame_of_impact_qtm" : 2089,
        "impact_timestamp_ns" : 1779306981676270000,
        "qtm_fps"             : QTM_FPS,
    },
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ns_to_utc_ms(ns: int, cdt_offset_hours: int = CDT_OFFSET_HOURS) -> float:
    """
    Convert a Pupil Labs nanosecond timestamp to UTC milliseconds-of-day.
    Replicates the Google Sheets formula exactly:
      =TEXT(((ns/1e9)/86400) - TIME(5,0,0), "hh:mm:ss.000")
    Uses modf() to extract only the fractional-day (time-of-day) portion,
    matching how TEXT() in Sheets discards the integer day part.
    """
    fractional_days = (ns / 1_000_000_000) / 86400
    fractional_days -= cdt_offset_hours / 24
    time_of_day = math.modf(fractional_days)[0]
    if time_of_day < 0:
        time_of_day += 1.0
    return time_of_day * 86400 * 1000


def fmt_ms(ms: float) -> str:
    """Format milliseconds-of-day as HH:MM:SS.mmm"""
    ms = round(ms, 3)
    h   = int(ms // 3_600_000)
    m   = int((ms % 3_600_000) // 60_000)
    s   = int((ms % 60_000) // 1000)
    frc = int(round(ms % 1000))
    return f"{h:02d}:{m:02d}:{s:02d}.{frc:03d}"


def hms_to_ms(time_str: str) -> float:
    """Convert 'HH:MM:SS.mmm' string to total milliseconds-of-day."""
    time_str = time_str.strip()
    match = re.match(r'^(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d+))?$', time_str)
    if not match:
        raise ValueError(f"Cannot parse time string: '{time_str}'")
    h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
    frac_str = match.group(4) or "0"
    frac_ms  = int(frac_str[:3].ljust(3, "0"))
    return (h * 3600 + m * 60 + s) * 1000 + frac_ms


def read_qtm_start_ms(tsv_path: Path) -> float:
    """
    Parse the TIME_STAMP line from a QTM .tsv export.
    Format: TIME_STAMP\t2026-05-20, 14:46:51.753
    Returns the time-of-day portion as milliseconds.
    """
    with open(tsv_path, "r", encoding="utf-8-sig") as fh:
        for line in fh:
            if line.startswith("TIME_STAMP"):
                parts = line.strip().split("\t")
                if len(parts) < 2:
                    raise ValueError(f"Unexpected TIME_STAMP format in {tsv_path}: {line!r}")
                value = parts[1].strip()
                time_part = value.split(",", 1)[1].strip() if "," in value else value
                return hms_to_ms(time_part)
    raise ValueError(f"TIME_STAMP not found in {tsv_path}")


def read_section_starts(csv_path: Path) -> list:
    """
    Read sections.csv and return all section start times (ns) sorted ascending.
    Used only for informational display — not part of the offset calculation.
    """
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        starts = []
        for row in reader:
            key = next((k for k in row if "section start time" in k.lower()), None)
            if key is None:
                raise KeyError(f"Could not find 'section start time' column. "
                               f"Available: {list(row.keys())}")
            starts.append(int(row[key].strip()))
    return sorted(starts)


def find_section_start_for_trial(impact_ns: int, section_starts_ns: list) -> int:
    """
    Find the section start that is closest to (but not after) the impact timestamp.
    This is robust to deleted trials leaving extra rows in sections.csv.
    """
    candidates = [s for s in section_starts_ns if s <= impact_ns]
    if not candidates:
        # Fallback: just pick the closest one overall
        return min(section_starts_ns, key=lambda s: abs(s - impact_ns))
    return max(candidates)  # largest ns value that is still ≤ impact_ns


# =============================================================================
# LOAD SECTION START TIMES ONCE (informational only)
# =============================================================================
print(f"{'='*70}")
print(f"  SYNC OFFSET ANALYSIS  —  {len(trials)} trials")
print(f"{'='*70}\n")

print("  Loading sections.csv …")
section_starts_ns = read_section_starts(SECTIONS_CSV)
print(f"  Found {len(section_starts_ns)} section rows (sorted ascending):\n")
for i, ns_val in enumerate(section_starts_ns, 1):
    print(f"    Row {i:>2d}: {ns_val}  →  {fmt_ms(ns_to_utc_ms(ns_val))} UTC")
print()

# =============================================================================
# ANALYSIS
# =============================================================================

offsets = []
skipped = []

for t in trials:
    trial_id = t["trial_id"]

    if t["frame_of_impact_qtm"] == 0 and t["impact_timestamp_ns"] == 0:
        print(f"  [{trial_id}]  SKIPPED — values not yet filled in\n")
        skipped.append(trial_id)
        continue

    # STEP 1 — QTM start time from TSV (PC clock, ms-of-day)
    tsv_path     = BASE_TSV_DIR / t["tsv_filename"]
    qtm_start_ms = read_qtm_start_ms(tsv_path)

    # STEP 2 — QTM impact time
    ms_per_frame  = 1000.0 / t["qtm_fps"]
    qtm_impact_ms = qtm_start_ms + (t["frame_of_impact_qtm"] * ms_per_frame) - 5.0  # -5 ms correction for QTM timing offset

    # STEP 3 — Neon impact time (phone clock, UTC ms-of-day)
    neon_impact_ms = ns_to_utc_ms(t["impact_timestamp_ns"])

    # STEP 4 — Raw difference
    raw_diff_ms = neon_impact_ms - qtm_impact_ms

    # STEP 5 — Apply phone-to-PC clock offset
    meta_path = BASE_META_DIR / t["metadata_filename"]
    with open(meta_path, "r") as fh:
        meta = json.load(fh)
    phone_to_pc_ms = meta["phone_to_pc_time_offset_ms"]

    adjusted_offset_ms = raw_diff_ms + phone_to_pc_ms
    offsets.append(adjusted_offset_ms)

    # Section start — informational display only, matched by proximity
    section_ns     = find_section_start_for_trial(t["impact_timestamp_ns"], section_starts_ns)
    section_utc_ms = ns_to_utc_ms(section_ns)

    print(f"  Trial: {trial_id}")
    print(f"    QTM start (PC UTC)              : {fmt_ms(qtm_start_ms)}")
    print(f"    QTM frame of impact             : {t['frame_of_impact_qtm']}  @ {t['qtm_fps']} Hz  →  +{t['frame_of_impact_qtm'] * ms_per_frame:.1f} ms")
    print(f"    QTM impact (PC UTC)             : {fmt_ms(qtm_impact_ms)}")
    print(f"    Neon section start [info only]  : {section_ns}  →  {fmt_ms(section_utc_ms)} UTC")
    print(f"    Neon impact (ns)                : {t['impact_timestamp_ns']}")
    print(f"    Neon impact (phone UTC)         : {fmt_ms(neon_impact_ms)}")
    print(f"    Raw diff (Neon − QTM) ms        : {raw_diff_ms:+.3f}")
    print(f"    phone_to_pc_time_offset_ms      : {phone_to_pc_ms:+.2f}")
    print(f"    ADJUSTED OFFSET ms              : {adjusted_offset_ms:+.3f}")
    print()

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================
if offsets:
    arr = np.array(offsets)
    print(f"{'='*70}")
    print(f"  SUMMARY  —  {len(offsets)} completed trial(s)")
    if skipped:
        print(f"  Skipped: {', '.join(skipped)}")
    print(f"{'='*70}")
    print(f"  Min    : {arr.min():+.1f} ms")
    print(f"  Max    : {arr.max():+.1f} ms")
    print(f"  Mean   : {arr.mean():+.1f} ms")
    print(f"  Median : {np.median(arr):+.1f} ms")
    print(f"  Std    : {arr.std():.1f} ms")
    print(f"  Range  : {arr.max() - arr.min():.1f} ms")
    print()
    if arr.mean() > 0:
        print(f"  → Neon lags QTM by ~{arr.mean():.1f} ms on average (after clock correction)")
    elif arr.mean() < 0:
        print(f"  → Neon leads QTM by ~{abs(arr.mean()):.1f} ms on average (after clock correction)")
    else:
        print(f"  → Neon and QTM are perfectly aligned on average.")
    print(f"{'='*70}\n")
else:
    print("  No completed trials — fill in frame_of_impact_qtm and impact_timestamp_ns and re-run.\n")
