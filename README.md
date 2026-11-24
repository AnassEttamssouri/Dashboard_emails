# Email Monitoring & Automation Dashboard

An interactive **Dash + Plotly + Pandas** web dashboard for monitoring, simulating, filtering, and sending emails, paired with an automated hourly threshold alert system built with Python's `smtplib`, `imaplib`, and `email` modules.

## Features

- **Key Performance Indicators (KPIs):** Tracks total received emails, total sent emails, received complaints (`réclamation`), sent sales emails (`vente`), and orders received in the current hour (`commande`).
- **Interactive Visualizations:**
  - **Email Trend Line Chart:** Switch between **hourly (last 48 hours)** and **daily (last 7 days)** views for received vs. sent emails.
  - **Category Breakdown Bar Chart:** Compares email volumes across `réclamation`, `commande`, `support`, `vente`, and `alerte`.
- **Hourly Order Threshold & Emergency Alerts:** Configure an hourly order limit (`1` to `20`, default `5`). When received orders in the current hour exceed the threshold, an emergency banner is displayed and an alert email is automatically triggered (once per hour) via `alert_system()`.
- **Simulation & Email Sending:**
  - Simulate incoming traffic (`+1 réclamation`, `+1 commande`, or `+8 commandes` burst to test emergency alerts).
  - Send new `vente` or `support` emails directly from the dashboard (simulated locally by default when `MODE_SIMULATION = True` in `email_utils.py`).
- **Latest 5 Emails Table:** Filter by multiple categories, search subjects with keywords or regular expressions, and toggle unread emails only (`Non lus seulement`).
- **Email Utilities (`email_utils.py`):** Includes helper functions for SMTP sending (`send_email`), `.eml` parsing with attachments (`lire_email`), IMAP unread filtering (`filter_emails`), and IMAP archiving (`archive_email`).

## Project Structure

```text
dashboard_emails/
├── app.py              # Main Dash application (layout, callbacks, Plotly charts)
├── email_utils.py      # Email automation helpers (smtplib, imaplib, email, alert system)
├── generate_data.py    # Generates 7 days of sample emails into data/emails.csv
├── requirements.txt    # Pinned Python dependencies
├── README.md           # Project documentation and setup guide
├── .gitignore          # Git ignore rules (.venv, __pycache__, .env, etc.)
├── assets/
│   └── style.css       # Custom CSS loaded automatically by Dash
└── data/
    └── emails.csv      # Pre-generated sample email dataset
```

## Prerequisites

- **Python 3.10 to 3.12** recommended (matches the pinned dependency versions in `requirements.txt`).
- Works on **Windows**, **Linux**, **macOS**, and **WSL**.

## How to Run the Project

### 1. Navigate to the Project Folder

After extracting the archive, open a terminal inside the `dashboard_emails` directory:

```bash
cd path/to/dashboard_emails
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

> **Tip (No Activation Needed):** If you prefer to skip activating `.venv` in PowerShell, you can call `.\.venv\Scripts\python.exe` directly in the steps below.

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

*(If running on Python 3.13+ and the pinned `numpy==1.26.2` / `pandas==2.1.4` wheels fail to install, run `pip install --upgrade dash plotly pandas numpy` instead and see the Troubleshooting section below.)*

### 4. (Optional) Refresh Sample Data

`data/emails.csv` is already included. To regenerate 7 days of fresh timestamps relative to today, run:

```bash
python generate_data.py
```

### 5. Start the Dashboard

```bash
python app.py
```

Open your browser and go to:

```text
http://127.0.0.1:8050
```

Press `Ctrl + C` in the terminal to stop the server.

## Real SMTP / IMAP Configuration (Optional)

By default, `MODE_SIMULATION = True` in `email_utils.py` so no external mail server is contacted. To send real emails:

1. Open `email_utils.py`.
2. Set `MODE_SIMULATION = False`.
3. Update `smtp_server`, `smtp_port`, `sender_email`, `sender_password`, and `DESTINATAIRE_ALERTE` with your mail provider credentials (use an App Password if using Gmail/Outlook with 2FA).

> Never commit real credentials to Git. Consider loading them from environment variables or a `.env` file (already excluded in `.gitignore`).
