# ☕ Morning News Digest

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?logo=pwa&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

An AI-powered daily news digest with a **Cybersecurity-first** focus. The pipeline automatically fetches articles from top security feeds (The Hacker News, Krebs on Security, BleepingComputer, CISA, SecurityWeek) and general news sources, summarizes them with **Google Gemini AI**, and delivers a beautiful mobile-first PWA dashboard with push notifications — all running hands-free via GitHub Actions every morning.

---

## 📸 Screenshots

> _Coming soon — screenshots of the PWA dashboard in dark mode._

---

## ✨ Features

- 🔒 **Cybersecurity-first** — Dedicated feeds from The Hacker News, Krebs on Security, BleepingComputer, SecurityWeek, and CISA Advisories
- 🌍 **Multi-category** — Also covers Technology, Business, and World news via the Currents API
- 🤖 **AI-powered summaries** — Each article gets a punchy hook, key bullets, and a "why it matters" line courtesy of Gemini 2.5 Flash
- 🛡️ **CVE tracking** — Automatically detects and tags CVE IDs (e.g., `CVE-2024-12345`) in articles
- 📱 **PWA dashboard** — Installable, offline-capable, mobile-first dark-mode interface
- 🔔 **Push notifications** — Get a morning alert via [ntfy.sh](https://ntfy.sh) with the top headline
- ⚡ **Zero-config automation** — GitHub Actions runs the full pipeline daily at 7:30 AM IST
- 🎯 **Category filtering** — Filter articles by Cybersecurity, Technology, Business, or World
- 💾 **Save for later** — Bookmark articles locally in the browser
- 🧪 **Mock mode** — Generate realistic sample data instantly for UI development and testing

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   RSS Feeds     │     │  Currents API    │     │  Gemini AI  │
│  (Cybersecurity)│     │  (Tech/Biz/World)│     │  (2.5 Flash)│
└────────┬────────┘     └────────┬─────────┘     └──────┬──────┘
         │                       │                       │
         └───────────┬───────────┘                       │
                     ▼                                   │
          ┌─────────────────────┐                        │
          │   Python Pipeline   │◄───────────────────────┘
          │  generate_digest.py │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │    digest.json      │
          │  (frontend/public/) │
          └──────────┬──────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
   ┌────────────────┐  ┌───────────┐
   │  PWA Frontend  │  │  ntfy.sh  │
   │  (Dark Mode)   │  │   Push    │
   └────────────────┘  └───────────┘
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/morning-news-digest.git
cd morning-news-digest
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys (see [API Keys](#-api-keys) below).

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Generate a mock digest (instant, no API keys needed)

```bash
python backend/generate_digest.py --mock
```

This creates a realistic `digest.json` with 12–15 sample articles for UI testing.

### 5. Serve the frontend

```bash
cd frontend && python -m http.server 8080
```

### 6. Open in your browser

```
http://localhost:8080
```

---

## ☁️ Zero-Server Cloud Setup & Phone Installation

You **do not need to keep your computer running** to use this app. The entire stack runs 100% free in the cloud:

```
[GitHub Cloud Runner] 
   └── Daily at 07:30 AM IST: Fetches RSS → Gemini Summarizes → Updates digest.json
          │
          ├──► Deploys frontend to GitHub Pages (HTTPS PWA)
          └──► Sends alert to your Phone (ntfy.sh app)
```

### Step 1: Push This Code to GitHub
1. Create a new repository on [GitHub](https://github.com/new) (public or private).
2. Push your project code to the `main` branch:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

### Step 2: Enable GitHub Pages in 10 Seconds
1. In your GitHub repo, go to **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, select **GitHub Actions**.
3. That's it! GitHub will now host your PWA with free HTTPS at:
   `https://<your-username>.github.io/<your-repo-name>/`

### Step 3: Add API Keys in GitHub Secrets
Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:
- `GEMINI_API_KEY`: Your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
- `CURRENTS_API_KEY`: Your Currents API key from [currentsapi.services](https://currentsapi.services/).
- `NTFY_TOPIC`: A unique secret topic string (e.g., `my-cyber-digest-7749`).
- `APP_URL`: Your GitHub Pages URL (e.g., `https://<your-username>.github.io/<your-repo-name>/`).

### Step 4: Install the App on Your Phone 📲

| On iPhone (iOS Safari) | On Android (Chrome) |
|---|---|
| 1. Open your GitHub Pages URL in Safari. | 1. Open your GitHub Pages URL in Chrome. |
| 2. Tap the **Share** button (box with upward arrow). | 2. Tap the **three dots** (⋮) in the top-right. |
| 3. Scroll down and tap **"Add to Home Screen"**. | 3. Tap **"Install app"** or **"Add to Home screen"**. |
| 4. The icon appears on your home screen and opens full-screen like a native app. | 4. The app installs to your app drawer and home screen. |

### Step 5: Turn On Direct In-App Alerts (No Third-Party App Needed!) 🔔
1. Open the app on your phone.
2. Tap the **Bell icon (🔔)** in the top right.
3. Turn on **In-App News Alerts** and allow browser notifications when prompted.
4. Set your **Preferred Delivery Time** (e.g. `07:30`, `08:00`).
5. Tap **"Send Test Notification Now"** to verify your phone receives notifications!

---

## 🔍 Variable News Search & Console Inspection

The app includes variable multi-keyword search across all article fields:
- Type partial words or terms (e.g., `palo`, `cve`, `zero-day`, `apple ai`, `hospital`, `krebs`).
- The list updates in real-time.
- **Console Inspection:** Whenever you type a search term, the app outputs formatted tables to the browser DevTools console via `console.table()` with columns for Title, Category, Source, CVE, and Hook!
- **Console Command:** You can also run searches directly from the browser DevTools console by typing:
  ```javascript
  searchNews("cve")
  searchNews("palo alto")
  ```

---

## ⏰ Changing the Automated News Schedule

You can change the time when GitHub automatically fetches news in two places:

1. **In the Cloud (GitHub Actions fetch time):**
   Open `.github/workflows/morning_digest.yml` and change the cron schedule:
   ```yaml
   on:
     schedule:
       - cron: '0 2 * * *'  # 02:00 UTC = 07:30 AM IST
   ```
   - For **8:00 AM IST**: use `'30 2 * * *'` (02:30 UTC)
   - For **8:30 AM IST**: use `'0 3 * * *'` (03:00 UTC)
   - For **9:00 AM IST**: use `'30 3 * * *'` (03:30 UTC)

2. **On Your Phone / Device (Daily reminder alarm):**
   Tap the **Bell icon (🔔)** in the app header and choose your preferred time in the time picker.

---

| Key | Where to get it | Required? |
|-----|----------------|-----------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) — free tier available | Yes (for live mode) |
| `CURRENTS_API_KEY` | [currentsapi.services](https://currentsapi.services/en/register) — free tier: 600 req/day | Yes (for live mode) |
| `NTFY_TOPIC` | [ntfy.sh](https://ntfy.sh) — free, no sign-up needed. Pick any unique topic name. Can also be [self-hosted](https://docs.ntfy.sh/install/). | Optional |

---

## ⚙️ GitHub Actions

The included workflow (`.github/workflows/morning_digest.yml`) runs the full pipeline automatically:

- **Schedule:** Every day at **02:00 UTC** (07:30 AM IST)
- **Manual trigger:** Click "Run workflow" in the Actions tab anytime
- **What it does:**
  1. Checks out the repo
  2. Installs Python dependencies (cached for speed)
  3. Runs `generate_digest.py` to fetch, summarize, and write `digest.json`
  4. Commits and pushes the updated digest back to the repo
  5. Sends a push notification via ntfy.sh

### Required Secrets

Add these in your repo → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Description |
|--------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `CURRENTS_API_KEY` | Currents API key |
| `NTFY_TOPIC` | Your ntfy.sh topic name |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, feedparser, trafilatura, BeautifulSoup4, requests |
| **AI** | Google Gemini 2.5 Flash (via `google-genai` SDK) |
| **News APIs** | RSS/Atom feeds, Currents API |
| **Frontend** | Vanilla HTML/CSS/JS, Progressive Web App |
| **Notifications** | ntfy.sh (push notifications) |
| **CI/CD** | GitHub Actions |
| **Styling** | Plus Jakarta Sans, JetBrains Mono, dark-mode design system |

---

## 📁 Project Structure

```
├── backend/
│   ├── generate_digest.py      # Main pipeline: fetch → summarize → output
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html              # PWA single-page app (embedded CSS/JS)
│   ├── manifest.json           # PWA manifest
│   ├── sw.js                   # Service worker (offline support)
│   └── public/
│       └── digest.json         # Generated digest data (auto-committed)
├── .github/
│   └── workflows/
│       └── morning_digest.yml  # Daily GitHub Actions workflow
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 Morning News Digest Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
