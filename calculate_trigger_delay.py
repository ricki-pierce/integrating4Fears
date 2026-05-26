"""
Sync Offset Analysis — Trigger Version
=======================================
Calculates the time offset at moment of trigger between Pupil Labs Neon
(phone clock) and QTM (PC clock) across multiple trials.

METHODOLOGY:
  1. QTM start time   → read "TIME_STAMP" field from each trial's .tsv file
                        (PC UTC wall-clock time, e.g. "14:46:51.753")
  2. QTM trigger time → QTM start time + (frame_of_trigger_qtm / qtm_fps) ms
                        - 5 ms correction for QTM timing offset
  3. Neon trigger time → auto-read from events.csv in the matching Timeseries
                         Data subfolder, row where name == "TEST_TRIGGER",
                         column "timestamp [ns]", converted to UTC ms-of-day
                         using: (ns/1e9)/86400 - TIME(5,0,0)
  4. Raw difference   → neon_trigger_utc_ms - qtm_trigger_utc_ms
  5. Adjusted offset  → raw_difference + phone_to_pc_time_offset_ms

HOW FOLDERS ARE MATCHED TO TRIALS:
  sections.csv contains one row per Neon recording with a "recording id"
  (full UUID, e.g. "e210b87f-1cb5-47b4-a462-...").
  The Timeseries Data subfolders are named like:
    2026-05-20_14-46-48-e210b87f
  The last 8 characters of the folder name match the first 8 characters of
  the recording id UUID.

  Matching strategy (proximity-based):
    - For each trial, we compute the QTM trigger time (UTC ms-of-day).
    - We scan all events.csv files in all subfolders, find the one whose
      TEST_TRIGGER timestamp [ns] (converted to UTC ms-of-day) is closest
      in time to that trial's QTM trigger time.
    - The matched folder's 8-char suffix is used to look up the recording id
      from sections.csv, which is sorted ascending by recording name
      (chronological order).
  Deleted trials (e.g. trial_05, trial_20) are simply skipped — no
  events.csv will be close enough in time to match them.

SIGN CONVENTION:
  Positive adjusted offset → Neon event appears later than QTM (Neon lags)
  Negative adjusted offset → Neon event appears earlier than QTM (Neon leads)
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
BASE_DIR        = r"C:\Users\rpier12\Desktop\Marker Test 520"
BASE_TSV_DIR    = Path(BASE_DIR) / "tsv files"
BASE_META_DIR   = Path(BASE_DIR) / "metadata"
TIMESERIES_DIR  = Path(BASE_DIR) / "Timeseries Data"
SECTIONS_CSV    = TIMESERIES_DIR / "sections.csv"

CDT_OFFSET_HOURS = 5    # CDT = UTC-5; matches Google Sheet -TIME(5,0,0)
QTM_FPS          = 200  # nominal QTM capture rate

# =============================================================================
# TRIAL DEFINITIONS
# Only fill in:
#   tsv_filename          : .tsv file in BASE_TSV_DIR
#   metadata_filename     : .json file in BASE_META_DIR
#   frame_of_trigger_qtm  : frame number at trigger, scrubbed from QTM
#   qtm_fps               : QTM capture rate
#
# recording_id and trigger_timestamp_ns are resolved automatically:
#   - trigger_timestamp_ns is read from the events.csv whose TEST_TRIGGER
#     timestamp is closest in time to this trial's QTM trigger time.
#   - recording_id is then looked up from sections.csv using the matched
#     folder's 8-char suffix.
# =============================================================================

trials = [
    {
        "trial_id"             : "trial_01",
        "tsv_filename"         : "drop_Trial1_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial1_ricki520.json",
        "frame_of_trigger_qtm" : 330,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_02",
        "tsv_filename"         : "drop_Trial2_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial2_ricki520.json",
        "frame_of_trigger_qtm" : 287,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_03",
        "tsv_filename"         : "drop_Trial3_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial3_ricki520.json",
        "frame_of_trigger_qtm" : 301,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_04",
        "tsv_filename"         : "drop_Trial4_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial4_ricki520.json",
        "frame_of_trigger_qtm" : 574,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_06",
        "tsv_filename"         : "drop_Trial6_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial6_ricki520.json",
        "frame_of_trigger_qtm" : 296,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_07",
        "tsv_filename"         : "drop_Trial7_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial7_ricki520.json",
        "frame_of_trigger_qtm" : 234,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_08",
        "tsv_filename"         : "drop_Trial8_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial8_ricki520.json",
        "frame_of_trigger_qtm" : 262,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_09",
        "tsv_filename"         : "drop_Trial9_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial9_ricki520.json",
        "frame_of_trigger_qtm" : 282,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_10",
        "tsv_filename"         : "drop_Trial10_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial10_ricki520.json",
        "frame_of_trigger_qtm" : 325,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_11",
        "tsv_filename"         : "drop_Trial11_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial11_ricki520.json",
        "frame_of_trigger_qtm" : 304,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_12",
        "tsv_filename"         : "drop_Trial12_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial12_ricki520.json",
        "frame_of_trigger_qtm" : 344,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_13",
        "tsv_filename"         : "drop_Trial13_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial13_ricki520.json",
        "frame_of_trigger_qtm" : 278,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_14",
        "tsv_filename"         : "drop_Trial14_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial14_ricki520.json",
        "frame_of_trigger_qtm" : 380,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_15",
        "tsv_filename"         : "drop_Trial15_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial15_ricki520.json",
        "frame_of_trigger_qtm" : 243,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_16",
        "tsv_filename"         : "drop_Trial16_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial16_ricki520.json",
        "frame_of_trigger_qtm" : 293,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_17",
        "tsv_filename"         : "drop_Trial17_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial17_ricki520.json",
        "frame_of_trigger_qtm" : 264,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_18",
        "tsv_filename"         : "drop_Trial18_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial18_ricki520.json",
        "frame_of_trigger_qtm" : 297,
        "qtm_fps"              : QTM_FPS,
    },
    {
        "trial_id"             : "trial_19",
        "tsv_filename"         : "drop_Trial19_ricki520.tsv",
        "metadata_filename"    : "metadata_drop_Trial19_ricki520.json",
        "frame_of_trigger_qtm" : 229,
        "qtm_fps"              : QTM_FPS,
    },
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ns_to_utc_ms(ns: int, cdt_offset_hours: int = CDT_OFFSET_HOURS) -> float:
    """
    Convert a Pupil Labs nanosecond timestamp to UTC milliseconds-of-day.
    Replicates the Google Sheets formula:
      =TEXT(((ns/1e9)/86400) - TIME(5,0,0), "hh:mm:ss.000")
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
    Read sections.csv and return a list of dicts with 'recording_id' and
    'recording_name', sorted ascending by recording_name (chronological).
    """
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rec_key  = next((k for k in row if "recording id" in k.lower()), None)
            name_key = next((k for k in row if "recording name" in k.lower()), None)
            if rec_key is None or name_key is None:
                raise KeyError(
                    f"Missing expected columns in {csv_path}. Found: {list(row.keys())}"
                )
            rows.append({
                "recording_id"   : row[rec_key].strip(),
                "recording_name" : row[name_key].strip(),
            })
    # Sort ascending by recording_name — the name contains a timestamp so
    # lexicographic order == chronological order (e.g. "2026-05-20_14-46-48-…")
    return sorted(rows, key=lambda r: r["recording_name"])


def build_folder_lookup(timeseries_dir: Path) -> dict:
    """
    Scan TIMESERIES_DIR for subfolders named like:
      2026-05-20_14-46-48-e210b87f
    Return a dict mapping the 8-char suffix → full folder Path.
    """
    lookup = {}
    for folder in timeseries_dir.iterdir():
        if not folder.is_dir():
            continue
        m = re.search(r'-([0-9a-f]{8})$', folder.name)
        if m:
            lookup[m.group(1)] = folder
    return lookup


def read_trigger_ns_from_events(events_csv: Path,
                                 event_name: str = "TEST_TRIGGER") -> int:
    """
    Read an events.csv file and return the timestamp [ns] for the first row
    where the 'name' column equals event_name.
    Returns None if the event is not present.
    """
    with open(events_csv, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name_key = next((k for k in row if k.strip().lower() == "name"), None)
            ts_key   = next((k for k in row if "timestamp" in k.lower()
                             and "ns" in k.lower()), None)
            if name_key is None or ts_key is None:
                raise KeyError(
                    f"Missing 'name' or 'timestamp [ns]' column in {events_csv}. "
                    f"Found: {list(row.keys())}"
                )
            if row[name_key].strip() == event_name:
                return int(row[ts_key].strip())
    return None  # event not found in this file


# =============================================================================
# BUILD LOOKUP TABLES
# =============================================================================
print(f"{'='*70}")
print(f"  SYNC OFFSET ANALYSIS (TRIGGER)  —  {len(trials)} trials")
print(f"{'='*70}\n")

# --- Scan subfolders --------------------------------------------------------
print("  Scanning Timeseries Data subfolders …")
folder_lookup = build_folder_lookup(TIMESERIES_DIR)
print(f"  Found {len(folder_lookup)} recording folder(s).\n")

# --- Build a master table of every events.csv and its TEST_TRIGGER time ----
# Structure: list of dicts with keys: suffix8, folder, events_path,
#            trigger_ns, trigger_utc_ms
print("  Reading TEST_TRIGGER timestamps from every events.csv …\n")
event_index = []   # one entry per folder that has a TEST_TRIGGER

for suffix8, folder in sorted(folder_lookup.items()):
    events_path = folder / "events.csv"
    if not events_path.exists():
        print(f"    {suffix8}  →  {folder.name}  [✗ no events.csv — skipping]")
        continue
    trigger_ns = read_trigger_ns_from_events(events_path)
    if trigger_ns is None:
        print(f"    {suffix8}  →  {folder.name}  [✗ no TEST_TRIGGER — skipping]")
        continue
    trigger_utc_ms = ns_to_utc_ms(trigger_ns)
    event_index.append({
        "suffix8"        : suffix8,
        "folder"         : folder,
        "events_path"    : events_path,
        "trigger_ns"     : trigger_ns,
        "trigger_utc_ms" : trigger_utc_ms,
    })
    print(f"    {suffix8}  →  {folder.name}  "
          f"[TEST_TRIGGER @ {fmt_ms(trigger_utc_ms)} UTC]")

print()

# --- Load and sort sections.csv ---------------------------------------------
print("  Loading sections.csv (sorted ascending by recording name) …")
sections = read_sections(SECTIONS_CSV)
print(f"  Found {len(sections)} section row(s):\n")
for i, sec in enumerate(sections, 1):
    prefix8 = sec["recording_id"].replace("-", "")[:8]
    print(f"    Row {i:>2d}: {prefix8}…  name={sec['recording_name']}")
print()

# Build a lookup: 8-char prefix → full recording_id
prefix8_to_recid = {}
for sec in sections:
    prefix8 = sec["recording_id"].replace("-", "")[:8]
    prefix8_to_recid[prefix8] = sec["recording_id"]

# =============================================================================
# ANALYSIS
# =============================================================================
offsets = []
skipped = []

# Track which event_index entries have already been claimed so that two
# trials cannot match to the same events.csv.
claimed_suffixes = set()

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
    # STEP 2 — QTM trigger time (-5 ms correction for QTM timing offset)
    # ------------------------------------------------------------------
    ms_per_frame   = 1000.0 / t["qtm_fps"]
    qtm_trigger_ms = qtm_start_ms + (t["frame_of_trigger_qtm"] * ms_per_frame) - 5.0

    # ------------------------------------------------------------------
    # STEP 3 — Find the closest unclaimed events.csv by proximity of
    #           TEST_TRIGGER timestamp to QTM trigger time
    # ------------------------------------------------------------------
    candidates = [e for e in event_index if e["suffix8"] not in claimed_suffixes]
    if not candidates:
        print(f"  [{trial_id}]  SKIPPED — no unclaimed events.csv remaining\n")
        skipped.append(trial_id)
        continue

    best = min(candidates,
               key=lambda e: abs(e["trigger_utc_ms"] - qtm_trigger_ms))
    proximity_ms = abs(best["trigger_utc_ms"] - qtm_trigger_ms)

    # Warn if the best match is suspiciously far away (> 60 seconds)
    if proximity_ms > 60_000:
        print(f"  [{trial_id}]  WARNING — best match is {proximity_ms/1000:.1f} s away. "
              f"Check manually.\n")

    claimed_suffixes.add(best["suffix8"])
    trigger_ns      = best["trigger_ns"]
    neon_trigger_ms = best["trigger_utc_ms"]
    matched_suffix  = best["suffix8"]

    # Look up full recording id from sections.csv
    recording_id = prefix8_to_recid.get(matched_suffix, f"[{matched_suffix}…not in sections.csv]")

    # ------------------------------------------------------------------
    # STEP 4 — Raw difference
    # ------------------------------------------------------------------
    raw_diff_ms = neon_trigger_ms - qtm_trigger_ms

    # ------------------------------------------------------------------
    # STEP 5 — Apply phone-to-PC clock offset from metadata
    # ------------------------------------------------------------------
    meta_path = BASE_META_DIR / t["metadata_filename"]
    try:
        with open(meta_path, "r") as fh:
            meta = json.load(fh)
        phone_to_pc_ms = meta["phone_to_pc_time_offset_ms"]
    except Exception as e:
        print(f"  [{trial_id}]  SKIPPED — cannot read metadata: {e}\n")
        skipped.append(trial_id)
        # Un-claim so it can be reused if we re-run after fixing metadata
        claimed_suffixes.discard(matched_suffix)
        continue

    adjusted_offset_ms = raw_diff_ms + phone_to_pc_ms
    offsets.append(adjusted_offset_ms)

    print(f"  Trial: {trial_id}  (matched recording: {matched_suffix}…  "
          f"proximity: {proximity_ms:.1f} ms)")
    print(f"    Matched events.csv              : {best['folder'].name}")
    print(f"    Recording ID                    : {recording_id}")
    print(f"    QTM start (PC UTC)              : {fmt_ms(qtm_start_ms)}")
    print(f"    QTM frame of trigger            : {t['frame_of_trigger_qtm']}  "
          f"@ {t['qtm_fps']} Hz  →  +{t['frame_of_trigger_qtm'] * ms_per_frame:.1f} ms")
    print(f"    QTM trigger (PC UTC)            : {fmt_ms(qtm_trigger_ms)}")
    print(f"    Neon trigger (ns, from events)  : {trigger_ns}")
    print(f"    Neon trigger (phone UTC)        : {fmt_ms(neon_trigger_ms)}")
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
    print("  No completed trials — check TSV paths, metadata, and events.csv files.\n")
