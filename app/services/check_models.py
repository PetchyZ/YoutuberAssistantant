import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("=== รายชื่อโมเดลที่คุณใช้ได้จริง ===")
for model in client.models.list():
    # กรองเอาเฉพาะโมเดลที่รองรับการเจนข้อความ/วิเคราะห์ภาพ
    print(f"Model ID: {model.name}")