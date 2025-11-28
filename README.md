# 🌌 ISS Radar – Visible Pass Alerts

A tiny automated bot that alerts me when the International Space Station will be **visible from my home** in the next 24 hours.

This project uses the free N2YO API to check for visible ISS passes once per day, and sends a Telegram notification only when something is worth looking up for.

---

## ✔️ What It Does

- Fetches the next **visible ISS passes** using the N2YO `visualpasses` API  
- Converts azimuth into **compass directions** (e.g., *SW → NE*)  
- Labels passes by elevation (*overhead*, *high*, *low*)  
- Sends a **Telegram message** only when visibility is predicted  
- Runs automatically every day via **GitHub Actions**  
- No server, no hosting costs, no noise

---

## ⚙️ How It Works

- `iss_check.py` loads location + API keys from **GitHub Secrets**
- Queries N2YO for passes in the next 1 day  
- Formats a clean visibility report  
- Sends a Telegram alert via bot API  
- `.github/workflows/iss.yml` runs the script daily at **15:00 UTC**

---

## 🔐 Secrets Required

Add these in **Repo → Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `API_KEY` | N2YO API key |
| `TELEGRAM_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Chat ID for notifications |
| `LAT` | Latitude of observing location |
| `LON` | Longitude of observing location |
| `ALT` | Altitude (meters) |

---

## 🕒 Schedule

The workflow runs at:

**15:00 UTC daily**  
*(3pm UK winter / 4pm UK summer)*

If the ISS is visible in the next 24 hours, I get a Telegram ping.  
If not, the bot stays silent.
