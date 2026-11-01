# SmartV2V — Complete Deployment Guide
**How to Deploy the Software Defined Vehicle (SDV) Simulator**

SmartV2V is designed with a **Unified Single-Port Architecture**:
The Python FastAPI backend serves the REST API (`/api`), the real-time WebSocket channel (`/ws`), and the compiled React production frontend (`/`) all on a single port (default `8000` or `$PORT`).

---

## Deployment Options At-a-Glance

| Method | Best For | Cost | Setup Time | Public URL? |
|---|---|---|---|---|
| **Option 1: Render.com** | Permanent academic project link | **Free** | 3–5 mins | Yes (HTTPS) |
| **Option 2: Cloudflare Tunnel / Ngrok** | Live college presentation demo | **Free** | 30 seconds | Yes (Instant HTTPS) |
| **Option 3: Local Network (Wi-Fi/LAN)** | College classroom sharing | **Free** | 10 seconds | Yes (Local Wi-Fi) |
| **Option 4: Railway.app** | Continuous Cloud deployment | Free Tier | 2 mins | Yes (HTTPS) |
| **Option 5: Docker / Docker Compose** | Portable containerized demo | **Free** | 1 command | Local/Cloud host |

---

## Option 1: Free Cloud Deployment on Render.com (Recommended for Project Submission)

Render provides a **free web service** tier that supports Docker and WebSockets natively.

### Step 1: Push Project to GitHub
1. Create a new GitHub repository (e.g., `SmartV2V`).
2. Initialize git and push the project:
   ```bash
   git init
   git add .
   git commit -m "Initial SmartV2V platform release"
   git branch -M main
   git remote add origin https://github.com/<your-username>/SmartV2V.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [https://render.com](https://render.com) and sign in with GitHub.
2. Click **New +** $\to$ **Web Service**.
3. Connect your `SmartV2V` GitHub repository.
4. Render will automatically detect the `Dockerfile` in the root folder:
   - **Name:** `smartv2v`
   - **Region:** Any (e.g., Oregon or Frankfurt)
   - **Environment:** `Docker`
   - **Instance Type:** `Free`
5. Click **Create Web Service**.
6. Render builds the multi-stage Docker container and provides a live HTTPS URL:
   ```
   https://smartv2v-xxxx.onrender.com
   ```
   *Your live platform, WebSockets, and dashboard will be accessible worldwide!*

---

## Option 2: Instant 30-Second Public HTTPS URL (Recommended for Live College Presentation)

If you are demonstrating the project on your laptop in front of professors and want them to open the dashboard on their phones or tablets **without uploading to GitHub**, use **Cloudflare Tunnel** or **Ngrok**.

### Using Cloudflare Tunnel (Zero Signup, Completely Free):
1. In your terminal, run:
   ```bash
   npx cloudflared tunnel --url http://localhost:8000
   ```
2. Cloudflare will instantly output a temporary public HTTPS URL:
   ```
   https://random-subdomain.trycloudflare.com
   ```
3. Anyone in the room (or worldwide) can open that link in their browser.

### Using Ngrok:
1. If you have ngrok installed:
   ```bash
   ngrok http 8000
   ```
2. Share the generated `https://xxxx.ngrok-free.app` link.

---

## Option 3: Local Network / College Wi-Fi Sharing

You can share the dashboard with anyone connected to the same college Wi-Fi or mobile hotspot.

1. Find your laptop's local IP address:
   - **Windows:** Run `ipconfig` in PowerShell (look for `IPv4 Address`, e.g., `192.168.1.45`).
   - **Mac/Linux:** Run `ifconfig` or `ip a`.
2. Start the unified backend (it already listens on `0.0.0.0`):
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Tell your professors or teammates to open their browser and visit:
   ```
   http://192.168.1.45:8000
   ```
   *(Replace `192.168.1.45` with your actual laptop IP).*

---

## Option 4: Deploying on Railway.app

1. Sign up at [https://railway.app](https://railway.app).
2. Click **New Project** $\to$ **Deploy from GitHub repo**.
3. Select your `SmartV2V` repository.
4. Railway will automatically build the `Dockerfile` and expose the web service.
5. In the service settings, click **Generate Domain** to get a public `https://smartv2v-production.up.railway.app` URL.

---

## Option 5: 1-Click Containerized Run with Docker

To run the entire platform inside an isolated container on any machine:

1. Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is running.
2. Run from the project root:
   ```bash
   docker compose up --build
   ```
3. Open `http://localhost:8000`.

---

## Pre-Deployment Production Build Verification

Before deploying, you can test the production build locally:

1. Build the React frontend:
   ```bash
   cd frontend
   npm run build
   ```
2. Start FastAPI (which automatically serves `frontend/dist`):
   ```bash
   cd ../backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Open `http://localhost:8000` in your browser.
