# 🚨 RESQ-AI — Multi-Agent Disaster Response Coordinator

> **Generative Multi-Agent Crisis Management & Real-Time Re-Planning System**

![RESQ-AI Command Center](https://img.shields.io/badge/RESQ--AI-v2.0.0-cyan?style=for-the-badge&logo=cpu)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google)

---

## 📌 1. Project Title & Tagline
**RESQ-AI — Multi-Agent Disaster Response Coordinator**  
*Generative AI for Situation-Aware Disaster Response Planning*

---

## 🚨 2. Problem Statement (HTH-GA-07)
During simulated disasters (floods, landslides, chemical spills), emergency managers must coordinate resource allocation, evacuation routing, medical triage, and public alerts under scarce resources.

Key Challenges:
- **Competing demands**: Field medics demanded in multiple sectors simultaneously.
- **Resource scarcity**: Rescue vehicles, medical teams, shelters, and supplies are strictly finite.
- **Dynamic escalation**: Secondary emergencies arise unexpectedly (e.g., landslides hitting hospital precincts).
- **Explainability**: Response plans must be fully transparent and explain trade-offs to human commanders.

---

## 💡 3. The RESQ-AI Solution
RESQ-AI deploys **4 specialized Generative AI Agents**:
1. **Medical Agent**: Evaluates casualty severity and triage priority.
2. **Logistics Agent**: Allocates vehicle fleet, shelter capacity, and analyzes **Synthetic Road Network Access** (reroutes traffic when primary roads are blocked).
3. **Communications Agent**: Drafts public evacuation alerts (`AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO`).
4. **Coordinator Agent**: Master orchestrator that resolves agent conflicts, enforces hard limits, and generates human-commander-explainable decision rationales.

---

## 💻 4. Tech Stack

- **Backend**: Python 3.14, FastAPI, Pydantic v2, Uvicorn, Google GenAI SDK (`google-genai`), Python-Dotenv
- **Frontend**: React 19, Vite 6, Tailwind CSS v4, Lucide React, Axios
- **LLM Engine**: Google Gemini API (`gemini-2.5-flash`) with smart deterministic fallback mode.

---

## 🚀 5. Setup Instructions

### Quick Start

**Windows:**
```cmd
start.bat
```

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

---

## 📡 6. API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/state` | `GET` | Fetches complete current system state (Zones, Resources, Plan, Logs) |
| `/api/analyze` | `POST` | Validates location & situation inputs and initializes response simulation |
| `/api/chat` | `POST` | Processes natural-language chatbot requests and updates scenario state |
| `/api/plan` | `POST` | Triggers multi-agent pipeline for initial response plan |
| `/api/replan` | `POST` | Triggers multi-agent pipeline for dynamic re-planning |
| `/api/zones/preset-d` | `POST` | Adds Zone D (Hospital Landslide Hazard) to scenario roster |
| `/api/reset` | `POST` | Resets disaster scenario back to initial state |
