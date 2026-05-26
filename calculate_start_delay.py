"""
Sync Offset Analysis — Start Time Version
==========================================
Calculates the time offset between Pupil Labs Neon (phone clock) and QTM
(PC clock) using only recording start times — no trigger or impact events.

METHODOLOGY:
  1. QTM start time  → read "TIME_STAMP" field from each trial's .tsv file
                       (PC UTC wall-clock time, e.g. "14:46:51.753")
  2. Neon start time → read "section start time [ns]" from sections.csv,
                       sorted ascending by recording name (chronological).
                       Each trial is matched to the closest unmatched section
                       row by proximity of start times.
                       Converted to UTC ms-of-day via: (ns/1e9)/86400 - TIME(5,0,0)
  3. Raw difference  → neon_start_utc_ms - qtm_start_ms
  4. Adjusted offset → raw_difference + phone_to_pc_time_offset_ms

SIGN CONVENTION:
  Positive adjusted offset → Neon started later than QTM (Neon lags)
  Negative adjusted offset → Neon started earlier than QTM (Neon leads)
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
TIMESERIES_DIR = Path(BASE_DIR) / "Timeseries Data"
SECTIONS_CSV  = TIMESERIES_DIR / "sections.csv"

CDT_OFFSET_HOURS = 5    # CDT = UTC-5
QTM_FPS          = 200  # only used for display; no frame math needed here

# =============================================================================
# TRIAL DEFINITIONS
# Only fill in tsv_filename and metadata_filename.
# Neon start time and recording_id are matched automatically from sections.csv.
# =============================================================================

trials = [
    {"trial_id": "trial_01",  "tsv_filename": "drop_Trial1_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial1_ricki520.json"},
    {"trial_id": "trial_02",  "tsv_filename": "drop_Trial2_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial2_ricki520.json"},
    {"trial_id": "trial_03",  "tsv_filename": "drop_Trial3_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial3_ricki520.json"},
    {"trial_id": "trial_04",  "tsv_filename": "drop_Trial4_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial4_ricki520.json"},
    {"trial_id": "trial_06",  "tsv_filename": "drop_Trial6_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial6_ricki520.json"},
    {"trial_id": "trial_07",  "tsv_filename": "drop_Trial7_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial7_ricki520.json"},
    {"trial_id": "trial_08",  "tsv_filename": "drop_Trial8_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial8_ricki520.json"},
    {"trial_id": "trial_09",  "tsv_filename": "drop_Trial9_ricki520.tsv",  "metadata_filename": "metadata_drop_Trial9_ricki520.json"},
    {"trial_id": "trial_10",  "tsv_filename": "drop_Trial10_ricki520.tsv", "metadata_filename": "metadata_drop_Trial10_ricki520.json"},
    {"trial_id": "trial_11",  "tsv_filename": "drop_Trial11_ricki520.tsv", "metadata_filename": "metadata_drop_Trial11_ricki520.json"},
    {"trial_id": "trial_12",  "tsv_filename": "drop_Trial12_ricki520.tsv", "metadata_filename": "metadata_drop_Trial12_ricki520.json"},
    {"trial_id": "trial_13",  "tsv_filename": "drop_Trial13_ricki520.tsv", "metadata_filename": "metadata_drop_Trial13_ricki520.json"},
    {"trial_id": "trial_14",  "tsv_filename": "drop_Trial14_ricki520.tsv", "metadata_filename": "metadata_drop_Trial14_ricki520.json"},
    {"trial_id": "trial_15",  "tsv_filename": "drop_Trial15_ricki520.tsv", "metadata_filename": "metadata_drop_Trial15_ricki520.json"},
    {"trial_id": "trial_16",  "tsv_filename": "drop_Trial16_ricki520.tsv", "metadata_filename": "metadata_drop_Trial16_ricki520.json"},
    {"trial_id": "trial_17",  "tsv_filename": "drop_Trial17_ricki520.tsv", "metadata_filename": "metadata_drop_Trial17_ricki520.json"},
    {"trial_id": "trial_18",  "tsv_filename": "drop_Trial18_ricki520.tsv", "metadata_filename": "metadata_drop_Trial18_ricki520.json"},
    {"trial_id": "trial_19",  "tsv_filename": "drop_Trial19_ricki520.tsv", "metadata_filename": "metadata_drop_Trial19_ricki520.json"},
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ns_to_utc_ms(ns: int, cdt_offset_hours: int = CDT_OFFSET_HOURS) -> float:
    """Convert Pupil Labs nanosecond timestamp to UTC milliseconds-of-day."""
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
    """Parse TIME_STAMP from a QTM .tsv export, return ms-of-day."""
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


def read_sections(csv_path: Path) -> list:
    """
    Read sections.csv and return a list of dicts with recording_id,
    recording_name, section_start_ns, and section_start_utc_ms.
    Sorted ascending by recording_name (lexicographic == chronological).
    """
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rec_key   = next((k for k in row if "recording id"         in k.lower()), None)
            name_key  = next((k for k in row if "recording name"       in k.lower()), None)
            start_key = next((k for k in row if "section start time"   in k.lower()), None)
            if None in (rec_key, name_key, start_key):
                raise KeyError(
                    f"Missing expected columns in {csv_path}. Found: {list(row.keys())}"
                )
            ns = int(row[start_key].strip())
            rows.append({
                "recording_id"        : row[rec_key].strip(),
                "recording_name"      : row[name_key].strip(),
                "section_start_ns"    : ns,
                "section_start_utc_ms": ns_to_utc_ms(ns),
            })
    return sorted(rows, key=lambda r: r["recording_name"])

# =============================================================================
# LOAD SECTIONS
# =============================================================================
print(f"{'='*70}")
print(f"  SYNC OFFSET ANALYSIS (START TIME)  —  {len(trials)} trials")
print(f"{'='*70}\n")

print("  Loading sections.csv (sorted ascending by recording name) …")
sections = read_sections(SECTIONS_CSV)
print(f"  Found {len(sections)} section row(s):\n")
for i, sec in enumerate(sections, 1):
    print(f"    Row {i:>2d}: {sec['recording_id'][:8]}…  "
          f"name={sec['recording_name']}  "
          f"start={fmt_ms(sec['section_start_utc_ms'])} UTC")
print()

# =============================================================================
# ANALYSIS
# =============================================================================
offsets  = []
skipped  = []
claimed  = set()   # indices into sections[] already matched to a trial

for t in trials:
    trial_id = t["trial_id"]

    # ------------------------------------------------------------------
    # STEP 1 — QTM start time from TSV
    # ------------------------------------------------------------------
    tsv_path = BASE_TSV_DIR / t["tsv_filename"]
    try:
        qtm_start_ms = read_qtm_start_ms(tsv_path)
    except Exception as e:
        print(f"  [{trial_id}]  SKIPPED — cannot read TSV: {e}\n")
        skipped.append(trial_id)
        continue

    # ------------------------------------------------------------------
    # STEP 2 — Find closest unclaimed Neon section by start-time proximity
    # ------------------------------------------------------------------
    candidates = [(i, sec) for i, sec in enumerate(sections) if i not in claimed]
    if not candidates:
        print(f"  [{trial_id}]  SKIPPED — no unclaimed section rows remaining\n")
        skipped.append(trial_id)
        continue

    best_idx, best_sec = min(
        candidates,
        key=lambda x: abs(x[1]["section_start_utc_ms"] - qtm_start_ms)
    )
    proximity_ms = abs(best_sec["section_start_utc_ms"] - qtm_start_ms)

    if proximity_ms > 60_000:
        print(f"  [{trial_id}]  WARNING — best match is {proximity_ms/1000:.1f} s away. "
              f"Check manually.")

    claimed.add(best_idx)
    neon_start_ms = best_sec["section_start_utc_ms"]
    recording_id  = best_sec["recording_id"]

    # ------------------------------------------------------------------
    # STEP 3 — Raw difference
    # ------------------------------------------------------------------
    raw_diff_ms = neon_start_ms - qtm_start_ms

    # ------------------------------------------------------------------
    # STEP 4 — Apply phone-to-PC clock offset from metadata
    # ------------------------------------------------------------------
    meta_path = BASE_META_DIR / t["metadata_filename"]
    try:
        with open(meta_path, "r") as fh:
            meta = json.load(fh)
        phone_to_pc_ms = meta["phone_to_pc_time_offset_ms"]
    except Exception as e:
        print(f"  [{trial_id}]  SKIPPED — cannot read metadata: {e}\n")
        skipped.append(trial_id)
        claimed.discard(best_idx)
        continue

    adjusted_offset_ms = raw_diff_ms + phone_to_pc_ms
    offsets.append(adjusted_offset_ms)

    print(f"  Trial: {trial_id}  (matched: {recording_id[:8]}…  proximity: {proximity_ms:.1f} ms)")
    print(f"    Recording name                  : {best_sec['recording_name']}")
    print(f"    QTM start (PC UTC)              : {fmt_ms(qtm_start_ms)}")
    print(f"    Neon section start (phone UTC)  : {fmt_ms(neon_start_ms)}")
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
        print(f"  → Neon started later than QTM by ~{arr.mean():.1f} ms on average (after clock correction)")
    elif arr.mean() < 0:
        print(f"  → Neon started earlier than QTM by ~{abs(arr.mean()):.1f} ms on average (after clock correction)")
    else:
        print(f"  → Neon and QTM start times are perfectly aligned on average.")
    print(f"{'='*70}\n")
else:
    print("  No completed trials — check TSV paths and metadata files.\n")
