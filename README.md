🎥 YouTube Creator Growth & Intelligence Platform (Capstone Project)
An AI-powered analytics and optimization platform designed for YouTube Content Creators. Driven by Large Language Models (LLMs), Computer Vision, and Vector Search, this system delivers actionable insights to boost video performance and audience engagement based on empirical research in video recommendation algorithms and consumer visual behavior.

✨ Key Features
Thumbnail Analysis & Scoring: Evaluates thumbnail quality (scored from 1 to 10) alongside comparative pros and cons against niche competitors using principles of Visual Saliency, High-Contrast Features, and Facial Emotion Recognition.

Video Performance Drivers: Analyzes view metrics and engagement drivers informed by YouTube’s recommendation architecture (Deep Neural Networks for YouTube Recommendations) combined with audience comment sentiment analysis.

Trend & Velocity Analysis: Tracks real-time video performance velocity and category-wide trends.

Creator Matchmaking & Competitor Insights: Identifies prospective collaborators and similar competing channels with comparable subscriber and view counts using Vector Similarity (ChromaDB) to uncover differentiation opportunities and collab potential.

🛠️ Tech Stack
Frontend: Next.js (App Router), TypeScript, Tailwind CSS, Lucide React, Axios

Backend: Python, FastAPI, Pydantic, Uvicorn

AI / Machine Learning: Google Gemini API (Multimodal / LLM), OpenCV, MediaPipe (Vision Processing)

Database & Search: ChromaDB (Vector Database for Matchmaking)

External APIs: YouTube Data API v3

🏗️ System Architecture
Built with a modular and microservice-ready architecture for clear separation of concerns and high scalability:

Frontend Layer: Responsive dashboard designed for intuitive creator workflow management.

API Gateway (FastAPI): Handles routing, request/response validation, and exception handling.

Vision Processing Service: Processes thumbnail assets using computer vision models and multimodal LLMs.

Data & Trend Analytics Service: Fetches raw data from the YouTube API and executes NLP/sentiment pipelines.

Similarity Engine (Vector DB): Vectorizes channel profiles to compute spatial proximity via Cosine Similarity.

🚀 Getting Started
Because this application relies on a client-server architecture, both backend and frontend servers must be run concurrently.

1. Backend Setup (FastAPI)
Bash
# Navigate to the backend directory
cd backend

# Activate your virtual environment (if using one)
# .youtube_env\Scripts\activate (Windows) or source .youtube_env/bin/activate (Mac/Linux)

# Start the server
uvicorn main:app --reload --port 8000
(Backend running at: http://localhost:8000)

2. Frontend Setup (Next.js)
Open a separate terminal window:

Bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
(Access web application at: http://localhost:3000)

📚 Research References
Covington, P., Adams, J., & Sargin, E. (2016). Deep Neural Networks for YouTube Recommendations. Google Research.

Visual Saliency, High-Contrast Feature extraction, and Click-Through Rate (CTR) behavioral models on digital video platforms.
