import os
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# ============================
# 1. LOAD CONFIG FROM SECRETS
# ============================

LAT = float(os.getenv("LAT"))
LON = float(os.getenv("LON"))
ALT = float(os.getenv("ALT"))

API_KEY = os.getenv("API_KEY")              # N2YO API key
TOKEN = os.getenv("TELEGRAM_TOKEN")         # Telegram bot token
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")     # Telegram chat ID

LOCAL_TZ = ZoneInfo("Europe/London")

DAYS = 1          # look ahead this many days
MIN_VIS = 1       # minimum visible duration in minutes


# ============================
# 2. HELPERS
# ============================

def send_telegram(message: str):
    """Send a Telegram message via bot API."""
    if not TOKEN or not CHAT_ID:
        print("Telegram config missing. No message sent.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    r = requests.post(url, data=payload)
    r.raise_for_status()


def fetch_iss_passes():
    """Fetch visible ISS passes using N2YO 'visualpasses' endpoint."""
    url = (
        f"https://api.n2yo.com/rest/v1/satellite/visualpasses/"
        f"25544/{LAT}/{LON}/{ALT}/{DAYS}/{MIN_VIS}/&apiKey={API_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data.get("passes", [])


def az_to_dir(az_deg: float) -> str:
    """Convert azimuth degrees to compass direction."""
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    idx = int((az_deg + 22.5) // 45)
    return dirs[idx]


def elevation_label(max_el: float) -> str:
    """Friendly label based on elevation."""
    if max_el >= 70:
        return "overhead"
    elif max_el >= 40:
        return "high"
    else:
        return "low"


# ============================
# 3. MAIN LOGIC
# ============================

def main():
    print(f"Fetching ISS visible passes for the next {DAYS} day(s)...\n")
    passes = fetch_iss_passes()

    if not passes:
        print("No visible ISS passes. No Telegram alert sent.")
        return

    lines = []
    for p in passes:
        # Convert UNIX timestamps
        start_utc = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
        local_start = start_utc.astimezone(LOCAL_TZ)

        duration = p["duration"]  # seconds
        max_el = p["maxEl"]       # degrees
        start_az = p["startAz"]
        end_az = p["endAz"]

        # Friendly labels
        el_label = elevation_label(max_el)
        start_dir = az_to_dir(start_az)
        end_dir = az_to_dir(end_az)

        lines.append(
            f"🕒 {local_start.strftime('%Y-%m-%d %H:%M')} – "
            f"{duration//60}m{duration%60:02d}s – {el_label} ({max_el:.0f}°), "
            f"{start_dir} → {end_dir}"
        )

    msg = (
        f"🚀 ISS visibility over home – next {DAYS} day\n\n"
        + "\n".join(lines)
    )

    print(msg)
    send_telegram(msg)


if __name__ == "__main__":
    main()
