from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import base64
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/analyze-plant")
async def analyze_plant_image(file: UploadFile = File(...)):
    try:
        print(f"[DEBUG] Received file: {file.filename}, Content-Type: {file.content_type}")

        # Read file content
        contents = await file.read()
        print(f"[DEBUG] File size: {len(contents)} bytes")

        # Encode to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        print(f"[DEBUG] Base64 image length: {len(base64_image)}")

        # Call OpenAI API
        print("[DEBUG] Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                   "content": """You are an expert plant pathologist integrated into a plant monitoring app. When the user sends an image of a plant, analyze the image carefully to identify any diseases, deficiencies, or issues.

Based on your analysis, respond ONLY and STRICTLY in the following JSON format. DO NOT add extra text beyond the JSON.

{
  "plantName": "string",
  "issue": "string",
  "severity": "string",
  "quickFix": "string",
  "problemDetails": {
    "issue": "string",
    "effects": "string",
    "causes": ["string"]
  },
  "solutions": {
    "organic": ["string"],
    "chemical": [
      {
        "name": "string",
        "description": "string",
        "price": "string"
      }
    ]
  },
  "prevention": {
    "summer": "string",
    "winter": "string"
  },
  "dosAndDonts": [
    {
      "text": "string",
      "isDo": boolean
    }
  ]
}

Rules You Must Follow:
1) RETURN ONLY THE JSON — no markdown, no explanation.
2) If the image is too blurry, return “Unknown” for all fields.
3) If no issue is found:
   - Set issue = "None"
   - Set severity = "None"
   - Set quickFix = "No action needed"
   - Keep prevention based on general care tips
4) Do not leave any field empty. Use fallback values when unsure.
5) Always return a full object with all keys — even if values are guesses or defaults.
6) For chemical solutions, suggest a common treatment like "Neem Oil" or "Fungicide Spray".

Example fallback output:
{
  "plantName": "Unknown Plant",
  "issue": "None",
  "severity": "None",
  "quickFix": "No action needed",
  "problemDetails": {
    "issue": "None",
    "effects": "Healthy growth",
    "causes": []
  },
  "solutions": {
    "organic": [],
    "chemical": [
      {
        "name": "General Fertilizer",
        "description": "Balanced NPK fertilizer for overall plant health",
        "price": "₹399"
      }
    ]
  },
  "prevention": {
    "summer": "Maintain regular watering and inspect leaves weekly.",
    "winter": "Avoid overwatering and keep away from cold drafts."
  },
  "dosAndDonts": [
    {"text": "Mist regularly", "isDo": true},
    {"text": "Don’t over-fertilize", "isDo": false}
  ]
}"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse this plant"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file.content_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        print("[DEBUG] OpenAI response received")
        print("[DEBUG] Raw GPT response:")
        print(response.choices[0].message.content)

        # Parse JSON
        result = json.loads(response.choices[0].message.content)
        print("[DEBUG] Successfully parsed JSON response")
        return result

    except json.JSONDecodeError as je:
        print(f"[ERROR] JSON decode failed: {je}")
        print("[ERROR] Raw content was:")
        print(response.choices[0].message.content)
        raise HTTPException(status_code=500, detail="Failed to parse model response")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        print(f"[ERROR] Full exception: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/health")
async def health_check():
    return {"status": "healthy"}