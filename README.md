# 🎥 YouTube Creator Growth & Intelligence Platform (Capstone Project)

An end-to-end, AI-powered analytics and optimization dashboard designed for YouTube Content Creators. Driven by Large Language Models (LLMs), Computer Vision, and Vector Search, this platform delivers research-backed, actionable insights to optimize thumbnails, boost audience retention, analyze competitor trends, and identify strategic collaboration opportunities.

---

## 🎯 Key Features

1. **Thumbnail Analysis & Scoring (Feature 1):**
   * Evaluates video thumbnails on a 1–10 scale using Computer Vision metrics combined with Multimodal AI (Gemini Vision).
   * Analyzes Visual Saliency, High-Contrast Features, Facial Emotion Recognition (FER), and Text Readability (OCR) to increase Click-Through Rate (CTR).

2. **Video Performance Drivers (Feature 2):**
   * Diagnoses view drivers and audience retention proxies based on Google Research (*Deep Neural Networks for YouTube Recommendations*).
   * Conducts NLP Sentiment Analysis on top viewer comments to identify content strengths, weaknesses, and audience satisfaction metrics.

3. **Trend & Velocity Analysis (Feature 3):**
   * Tracks real-time video performance velocity (Views/Day) against Thailand and global niche market trends.
   * Identifies emerging topics and content gaps to help creators pivot toward high-traffic search queries.

4. **Creator Matchmaking & Competitor Insights (Feature 4):**
   * Vectorizes YouTube channel profiles and calculates **Cosine Similarity** using **ChromaDB**.
   * Discovers lookalike competing channels within similar subscriber bands and generates tailored collaboration concepts via Gemini.

---

## 🛠️ Tech Stack

### **Frontend**
* **Framework:** Next.js (App Router), React, TypeScript
* **Styling:** Tailwind CSS, Lucide React Icons
* **Data Fetching:** Axios

### **Backend**
* **Framework:** Python 3.10+, FastAPI, Pydantic
* **Server:** Uvicorn

### **AI / Machine Learning & Search**
* **LLM & Vision:** Google Gemini API (`gemini-2.5-flash` / Multimodal)
* **Vector Store:** ChromaDB
* **Vision Processing:** OpenCV, MediaPipe

### **Data Source**
* **External API:** YouTube Data API v3

---

## 🏗️ System Architecture

```text
+-----------------------------------------------------------------------+
|                            Next.js Frontend                           |
|      (Dashboard UI: Thumbnail, Performance, Trend, Matchmaking)       |
+-----------------------------------+-----------------------------------+
                                    |
                                HTTP / REST
                                    |
+-----------------------------------v-----------------------------------+
|                           FastAPI Backend                             |
|                           (API Gateway)                               |
+-----------+-----------------------+-----------------------+-----------+
            |                       |                       |
+-----------v-----------+ +---------v-----------+ +---------v-----------+
| Vision Service        | | Performance Service | | Matchmaking Service |
| (OpenCV + Gemini)     | | (YouTube API + NLP) | | (ChromaDB Vector)   |
+-----------------------+ +---------------------+ +---------------------+
```

---

## 🚀 Getting Started

To run this project locally, execute the backend and frontend concurrently.

### Prerequisites
* Python 3.10+
* Node.js 18+
* YouTube Data API Key
* Gemini API Key

---

### 1. Backend Setup

```bash
# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file
# YOUTUBE_API_KEY=your_youtube_api_key
# GEMINI_API_KEY=your_gemini_api_key

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
*Backend API Docs will be available at:* `http://localhost:8000/docs`

---

### 2. Frontend Setup

```bash
# Navigate to the frontend folder
cd frontend

# Install Node modules
npm install

# Run the development server
npm run dev
```
*Access the web application at:* `http://localhost:3000`

---

## 📚 Research References

* Covington, P., Adams, J., & Sargin, E. (2016). *Deep Neural Networks for YouTube Recommendations*. Google Research. [Read Paper (PDF)](https://research.google.com/pubs/archive/45530.pdf)
* Research on Visual Saliency, High-Contrast Feature Extraction, and Click-Through Rate (CTR) Behavioral Analytics in Digital Video Platforms.
