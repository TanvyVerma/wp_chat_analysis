"""
preprocessor.py
───────────────
Robust WhatsApp chat parser.

Supported formats
─────────────────
  Android  24-h : 25/12/23, 14:05 - Name: text
  Android  12-h : 25/12/23, 2:05 pm - Name: text
  iOS      24-h : [25/12/2023, 14:05:30] Name: text
  iOS      12-h : [25/12/2023, 2:05:30 PM] Name: text

Special messages handled
────────────────────────
  • <Media omitted>
  • This message was deleted
  • You deleted this message
  • Missed voice / video call
  • Group notifications (user joined / left / changed, etc.)

Usage
─────
  from preprocessor import preprocess, detect_format
  df = preprocess(raw_text)
"""

import re
import pandas as pd
from typing import Optional


# ── REGEX PATTERNS ────────────────────────────────────────────────────────────

# Android: "25/12/23, 14:05 - "  or  "25/12/23, 2:05 pm - "
_ANDROID_PATTERN = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s"          # date
    r"(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?)"  # time (12h or 24h)
    r"\s-\s",
    re.MULTILINE,
)

# iOS: "[25/12/2023, 14:05:30] "  or  "[25/12/2023, 2:05:30 PM] "
_IOS_PATTERN = re.compile(
    r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s"        # date
    r"(\d{1,2}:\d{2}:\d{2}(?:\s?[AaPp][Mm])?)"  # time
    r"\]\s",
    re.MULTILINE,
)

# System / notification messages (no ":" author separator)
_SYSTEM_KEYWORDS = (
    "messages and calls are end-to-end encrypted",
    "created group",
    "added you",
    "left",
    "added ",
    "removed ",
    "changed the subject",
    "changed this group",
    "changed the group",
    "you're now an admin",
    "is now an admin",
    "pinned a message",
    "security code changed",
    "created this group",
    "joined using this group",
    "turned on disappearing messages",
    "turned off disappearing messages",
    "you joined",
    "video call",
    "voice call",
    "missed",
    "waiting for this message",
)

# Placeholder messages
_DELETED_VARIANTS = {
    "this message was deleted",
    "you deleted this message",
}

_MEDIA_VARIANTS = {
    "<media omitted>",
}


# ── FORMAT DETECTION ──────────────────────────────────────────────────────────

def detect_format(data: str) -> str:
    """Return 'ios' or 'android' by testing which header regex matches first."""
    if _IOS_PATTERN.search(data):
        return "ios"
    return "android"


# ── TIMESTAMP PARSING ─────────────────────────────────────────────────────────

_ANDROID_TS_FORMATS = [
    "%d/%m/%Y, %H:%M",
    "%d/%m/%y, %H:%M",
    "%d/%m/%Y, %I:%M %p",
    "%d/%m/%y, %I:%M %p",
    "%d/%m/%Y, %I:%M%p",
    "%d/%m/%y, %I:%M%p",
    # with seconds
    "%d/%m/%Y, %H:%M:%S",
    "%d/%m/%y, %H:%M:%S",
    "%d/%m/%Y, %I:%M:%S %p",
    "%d/%m/%y, %I:%M:%S %p",
]

_IOS_TS_FORMATS = [
    "%d/%m/%Y, %I:%M:%S %p",
    "%d/%m/%y, %I:%M:%S %p",
    "%d/%m/%Y, %H:%M:%S",
    "%d/%m/%y, %H:%M:%S",
    "%d/%m/%Y, %I:%M:%S%p",
    "%d/%m/%y, %I:%M:%S%p",
]


def _parse_timestamp(raw: str, fmt: str) -> Optional[pd.Timestamp]:
    """Try a list of strptime formats; return Timestamp or None."""
    formats = _IOS_TS_FORMATS if fmt == "ios" else _ANDROID_TS_FORMATS
    raw = raw.strip()
    for f in formats:
        try:
            return pd.Timestamp(pd.to_datetime(raw, format=f))
        except (ValueError, TypeError):
            continue
    # Last resort: let pandas guess
    try:
        return pd.Timestamp(pd.to_datetime(raw, dayfirst=True))
    except Exception:
        return None


# ── BODY CLASSIFICATION ───────────────────────────────────────────────────────

def _classify_message(body: str) -> tuple[str, str]:
    """
    Return (user, clean_message).
    user is 'group_notification' for system lines.
    """
    body = body.strip()
    body_lower = body.lower()

    # System messages never contain a proper "Name: text" split
    for kw in _SYSTEM_KEYWORDS:
        if kw in body_lower:
            return "group_notification", body

    if ":" not in body:
        return "group_notification", body

    user, _, text = body.partition(":")
    user = user.strip()
    text = text.strip()

    # Guard: user names shouldn't be very long
    if len(user) > 60:
        return "group_notification", body

    return user, text


# ── MAIN PREPROCESSOR ─────────────────────────────────────────────────────────

def preprocess(data: str) -> Optional[pd.DataFrame]:
    """
    Parse a raw WhatsApp export string into a structured DataFrame.

    Returns None on catastrophic parse failure.
    Raises ValueError with a human-readable message for recoverable errors.
    """
    if not data or not data.strip():
        raise ValueError("The uploaded file appears to be empty.")

    # Strip invisible characters
    data = (
        data
        .replace("\u200e", "")   # left-to-right mark
        .replace("\u200f", "")   # right-to-left mark
        .replace("\ufeff", "")   # BOM
        .replace("\u202a", "")
        .replace("\u202c", "")
    )

    fmt = detect_format(data)
    pattern = _IOS_PATTERN if fmt == "ios" else _ANDROID_PATTERN

    # Split on message headers; keep delimiters via capturing groups
    parts = pattern.split(data)

    # parts[0] is text before the first message (usually empty / file header)
    # After that: [date, time, body, date, time, body, ...]
    header_text = parts[0]
    rest = parts[1:]

    if len(rest) < 3:
        raise ValueError(
            "Could not find any recognisable WhatsApp message headers. "
            "Please make sure you exported the chat without media, "
            "and that the file is not corrupted."
        )

    dates_raw = rest[0::3]
    times_raw = rest[1::3]
    bodies    = rest[2::3]

    if not (len(dates_raw) == len(times_raw) == len(bodies)):
        # Trim to the shortest length to stay consistent
        n = min(len(dates_raw), len(times_raw), len(bodies))
        dates_raw, times_raw, bodies = dates_raw[:n], times_raw[:n], bodies[:n]

    records = []
    parse_errors = 0

    for date_str, time_str, body in zip(dates_raw, times_raw, bodies):
        raw_ts = f"{date_str.strip()}, {time_str.strip()}"
        ts = _parse_timestamp(raw_ts, fmt)
        if ts is None:
            parse_errors += 1
            continue

        # Multiline messages arrive as a single body string; keep them intact.
        body = body.strip()
        if not body:
            continue

        user, message = _classify_message(body)

        records.append({
            "date":    ts,
            "user":    user,
            "message": message,
        })

    if not records:
        raise ValueError(
            "Parsing produced 0 messages. "
            f"({parse_errors} timestamp errors encountered.) "
            "The file may be in an unsupported format or locale."
        )

    df = pd.DataFrame(records)

    # ── Derived columns ────────────────────────────────────────────────────
    df["chat_format"] = fmt
    df["year"]        = df["date"].dt.year
    df["only_date"]   = df["date"].dt.date
    df["month"]       = df["date"].dt.month_name()
    df["month_num"]   = df["date"].dt.month
    df["day"]         = df["date"].dt.day
    df["day_name"]    = df["date"].dt.day_name()
    df["hour"]        = df["date"].dt.hour
    df["minute"]      = df["date"].dt.minute

    df["period"] = df["hour"].apply(
        lambda h: f"{h:02d}-{(h + 1) % 24:02d}"
    )

    # ── Message type tags ──────────────────────────────────────────────────
    msg_lower = df["message"].str.lower().str.strip()
    df["is_media"]   = msg_lower.isin(_MEDIA_VARIANTS)
    df["is_deleted"] = msg_lower.isin(_DELETED_VARIANTS)
    df["is_system"]  = df["user"] == "group_notification"

    df = df.sort_values("date").reset_index(drop=True)

    # ── Sanity assertions ──────────────────────────────────────────────────
    assert df["date"].isnull().sum() == 0, "Unexpected NaT dates after parsing."
    assert len(df) > 0, "DataFrame is empty after parsing."

    if parse_errors:
        import warnings
        warnings.warn(
            f"{parse_errors} message(s) were skipped due to unrecognised timestamp formats.",
            stacklevel=2,
        )

    return df