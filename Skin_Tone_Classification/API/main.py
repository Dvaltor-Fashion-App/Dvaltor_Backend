# Import required libraries
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from typing import List, Dict
from image_processor import ImageProcessor

# Initialize the FastAPI app with metadata
app = FastAPI(
    title="Dvaltor Fashion Recommendation API",
    description="Detect faces, analyze skin tone, and get color recommendations.",
    version="2.0.0"
)

# Set up CORS to allow cross-origin access from frontend or any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://dvaltor.com", "https://app.dvaltor.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load DNN face detection model ---
prototxt_path = "./Models/deploy.prototxt.txt"
model_path = "./Models/res10_300x300_ssd_iter_140000.caffemodel"

# Ensure the model files exist
if not os.path.exists(prototxt_path) or not os.path.exists(model_path):
    raise RuntimeError("Face detection model files missing.")

# Load the pre-trained OpenCV DNN face detector
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# --- Load and process skin tone recommendations CSV ---
try:
    df_recommendations = pd.read_csv("./Dataset/skin_tone_recommendations.csv")
except FileNotFoundError:
    raise RuntimeError("CSV file missing in './Dataset/'.")

# Convert hex color codes to RGB arrays
def hex_to_rgb(hex_code: str) -> List[int]:
    hex_code = hex_code.lstrip('#')
    return [int(hex_code[i:i+2], 16) for i in (0, 2, 4)]

# Add RGB column to dataframe
df_recommendations['RGB'] = df_recommendations['Hex Code'].apply(hex_to_rgb)
SKIN_TONE_RGB_LIST = np.array(df_recommendations['RGB'].tolist())

# Initialize FFmpeg-based image processor
image_processor = ImageProcessor(max_width=1920, max_height=1080, quality=85)

# --- Extract average skin tone from face region ---
def get_average_skin_color_from_roi(face_roi: np.ndarray) -> List[int] | None:
    try:
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)  # Convert to HSV for skin masking
        mask = cv2.inRange(hsv, np.array([0, 48, 80]), np.array([20, 255, 255]))  # Skin color range
        skin = cv2.bitwise_and(face_roi, face_roi, mask=mask)  # Mask non-skin pixels

        pixels = skin.reshape((-1, 3))  # Flatten to a list of pixels
        pixels = pixels[np.any(pixels != [0, 0, 0], axis=1)]  # Remove black background pixels

        if len(pixels) == 0:
            return None  # No skin detected

        return np.mean(pixels, axis=0).astype(int).tolist()  # Return average skin color
    except Exception as e:
        print("Skin color extraction error:", e)
        return None

# --- Match average skin color to closest dataset tone and get recommendations ---
def get_recommendation_json(avg_rgb_color: List[int]) -> Dict:
    distances = euclidean_distances([avg_rgb_color], SKIN_TONE_RGB_LIST)
    closest_index = np.argmin(distances)
    data = df_recommendations.iloc[closest_index]

    # Extract up to 20 recommended colors for closest tone
    recommendations = [
        {"name": data[f"Rec_Color_{i}_Name"], "hex": data[f"Rec_Color_{i}_Hex"]}
        for i in range(1, 21)
        if pd.notna(data.get(f"Rec_Color_{i}_Name")) and pd.notna(data.get(f"Rec_Color_{i}_Hex"))
    ]

    return {
        "detected_average_rgb": avg_rgb_color,
        "closest_skin_tone": {
            "description": data['Skin Shade Description'],
            "hex_code": data['Hex Code']
        },
        "recommended_colors": recommendations
    }

# --- Main API endpoint to process image and return recommendations ---
@app.post("/analyze-fashion/")
async def detect_and_recommend(file: UploadFile = File(...)):
    contents = await file.read()
    
    try:
        # Use FFmpeg to preprocess and optimize the image
        optimized_contents = image_processor.optimize_image(contents)
        
        # Decode the optimized image
        np_arr = np.frombuffer(optimized_contents, np.uint8)
        original_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        # Fallback to direct decoding if FFmpeg fails
        print(f"FFmpeg preprocessing failed, using fallback: {e}")
        np_arr = np.frombuffer(contents, np.uint8)
        original_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if original_image is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    (h, w) = original_image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(original_image, (300, 300)), 1.0, (300, 300), (104, 177, 123))
    net.setInput(blob)
    detections = net.forward()

    results = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            # Extract bounding box for detected face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            roi = original_image[max(0, startY):min(h, endY), max(0, startX):min(w, endX)]

            if roi.size > 0:
                avg_color = get_average_skin_color_from_roi(roi)
                if avg_color:
                    recommendation = get_recommendation_json(avg_color)
                else:
                    recommendation = {"error": "Could not extract skin tone."}

                results.append({
                    "face_details": {
                        "box_coordinates": [int(startX), int(startY), int(endX), int(endY)],
                        "confidence": float(confidence)
                    },
                    "fashion_recommendation": recommendation
                })

    # If no faces were processed, return 404
    if not results:
        return JSONResponse(content={"error": "No faces detected."}, status_code=404)

    return JSONResponse(content={"image_analysis_results": results})

# --- Root endpoint for API health/info ---
@app.get("/")
def root():
    return {
        "message": "Welcome to Dvaltor Fashion AI. Upload an image to get personalized fashion color suggestions."
    }

# --- Image info endpoint using FFmpeg ---
@app.post("/image-info/")
async def get_image_info(file: UploadFile = File(...)):
    """
    Get detailed image information using FFmpeg
    """
    try:
        contents = await file.read()
        info = image_processor.get_image_info(contents)
        return JSONResponse(content={
            "image_info": info,
            "status": "success"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

# --- Image optimization endpoint ---
@app.post("/optimize-image/")
async def optimize_uploaded_image(file: UploadFile = File(...)):
    """
    Optimize an image using FFmpeg for better performance
    """
    try:
        from fastapi.responses import StreamingResponse
        import io
        
        contents = await file.read()
        optimized = image_processor.optimize_image(contents)
        
        return StreamingResponse(
            io.BytesIO(optimized),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename=optimized_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to optimize image: {str(e)}")
# --- Run the app using: uvicorn main:app --reload ---
# Note: Ensure you have the required model files and CSV in the correct paths.