# 🎨✨ Skin Tone Prediction API — Powered by FastAPI, Machine Learning & FFmpeg

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Fastest%20Python%20API-green?logo=fastapi)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-blue?logo=opencv)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Image%20Optimization-orange?logo=ffmpeg)
![License](https://img.shields.io/github/license/ChromaFit-Project/backend_machine_learning?style=flat-square)
![Repo Size](https://img.shields.io/github/repo-size/ChromaFit-Project/backend_machine_learning)
![Contributions](https://img.shields.io/badge/PRs-Welcome-ff69b4?logo=github)
![Issues](https://img.shields.io/github/issues/ChromaFit-Project/backend_machine_learning)
![Stars](https://img.shields.io/github/stars/ChromaFit-Project/backend_machine_learning?style=social)
![Last Commit](https://img.shields.io/github/last-commit/ChromaFit-Project/backend_machine_learning)
![Uptime](https://img.shields.io/badge/Uptime-100%25-brightgreen)
![Model](https://img.shields.io/badge/ML_Model-KNN%20Trained-orange)
![Code Style](https://img.shields.io/badge/Code%20Style-PEP8-informational)

> 📷 Upload your face or skin image → 🎯 Detect average skin tone → 🎨 Get the predicted skin tone and its HEX code.  
> Powered by **Machine Learning**, **OpenCV**, and **FFmpeg**, wrapped inside a clean **FastAPI** interface!

---

## 🚀 Key Features

- 🧠 AI-powered **Skin Tone Prediction**
- 🔬 Detects **average RGB** value from face/body region
- 🎨 Returns closest **HEX Code** & predefined **skin shade label**
- 📊 Uses **Euclidean distance** for accurate shade matching
- ⚡ Fast, asynchronous, developer-friendly API with **FastAPI**
- 🎬 **FFmpeg integration** for advanced image preprocessing and optimization
- 🖼️ Automatic image normalization and format conversion
- 📉 Smart image compression for faster processing
- 🔁 Cleans up uploaded files automatically
- 📂 Clean, modular project structure

---

## 🗂️ Folder Structure

```bash
skin-tone-api/
│
├── main.py                      # 🔥 FastAPI app logic
├── image_processor.py           # 🎬 FFmpeg-based image processing utilities
├── requirements.txt             # 📦 Dependency list
│
├── Models/                      # 🧠 Trained ML model files
│   ├── skin_tone_model.pkl
│   └── label_encoder.pkl
│
├── Dataset/                     # 🎨 Skin shade references
│   └── skin_shades_india.csv
│
├── static/                      # 🖼️ (Optional) Sample image storage
│   └── example_image.jpg
│
└── README.md                    # 📘 You are here!
````

---

## ⚙️ Installation Guide

```bash
# 🚀 Clone the repository
git clone https://github.com/Alok-2002/skin-tone-api.git
cd skin-tone-api

# 🧪 Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 📦 Install required packages
pip install -r requirements.txt
```

---

## 🚦 Run the API Server

```bash
uvicorn main:app --reload
```

📍 Visit **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** for interactive Swagger UI

---

## 📡 API Endpoints

### 🔸 `POST /analyze-fashion/`

Main endpoint for skin tone detection and fashion recommendations with FFmpeg preprocessing.

* **Form field**: `file` (image file: JPG, PNG, WEBP, etc.)
* **Returns JSON** with:
  * Detected face coordinates
  * Average RGB skin color
  * Closest matching skin tone
  * Recommended fashion colors (up to 20)

📤 **Sample Response**:

```json
{
  "image_analysis_results": [
    {
      "face_details": {
        "box_coordinates": [150, 100, 350, 300],
        "confidence": 0.98
      },
      "fashion_recommendation": {
        "detected_average_rgb": [210, 180, 160],
        "closest_skin_tone": {
          "description": "Light Medium Skin",
          "hex_code": "#E3A58D"
        },
        "recommended_colors": [
          {"name": "Navy Blue", "hex": "#000080"},
          {"name": "Emerald Green", "hex": "#50C878"}
        ]
      }
    }
  ]
}
```

### 🔸 `POST /image-info/`

Get detailed image information using FFmpeg probe.

* **Form field**: `file` (image file)
* **Returns JSON** with:
  * Image dimensions (width, height)
  * Format and pixel format
  * File size
  * Duration

📤 **Sample Response**:

```json
{
  "image_info": {
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "pixel_format": "yuvj420p",
    "size_bytes": 245678
  },
  "status": "success"
}
```

### 🔸 `POST /optimize-image/`

Optimize and compress an image using FFmpeg.

* **Form field**: `file` (image file)
* **Returns**: Optimized JPEG image file
* **Features**:
  - Automatic compression
  - Size reduction
  - Format normalization

---

## 🧠 Machine Learning Details

| Component         | Description                                 |
| ----------------- | ------------------------------------------- |
| 🎯 Model          | Trained on labeled average RGB skin samples |
| 📚 Algorithm      | K-Nearest Neighbors (KNN)                   |
| 🧩 Label Encoding | Encodes skin tone categories                |
| 🎯 Color Match    | Euclidean distance with HEX RGBs            |

---

## 🎨 Skin Shade Reference Table

| 🔢 ID   | 🧾 Description    | 🎨 HEX Code |
| ------- | ----------------- | ----------- |
| Shade 1 | Very Light Skin   | `#F5E0D8`   |
| Shade 2 | Light Skin        | `#F2C9B1`   |
| Shade 3 | Fair Skin         | `#EAB7A1`   |
| Shade 4 | Light Medium Skin | `#E3A58D`   |

---

## 🧰 Built With

* 🧠 `Scikit-learn` – ML modeling
* ⚡ `FastAPI` – Web framework
* 📸 `OpenCV` – Image processing
* 🎬 `FFmpeg` – Advanced image/video processing
* 🐍 `Python 3.8+` - Python Language
* 📊 `Pandas / NumPy` – Data operations
* 💾 `Joblib` – Model serialization

---

## 📬 Sample cURL Request

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict/' \
  -F 'file=@your_image.jpg'
```

---

## 🛠️ Future Enhancements

* 📱 Mobile-ready skin tone prediction app (Flutter/React Native)
* 🌐 Streamlit Web App interface
* 🧪 Diverse & inclusive dataset training
* 🎯 Real-time video-based detection
* 🗃️ Color palette suggestions based on tone

---

## 🛡 License

📜 This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Maintainer

**Atul Sharma**
🔗 [LinkedIn](https://www.linkedin.com/in/atul-sharma2002)
💻 [GitHub](https://github.com/Alok-2002)

---

## 🌟 Show Your Support

If you found this helpful, give it a ⭐ on GitHub and share it with friends or developers who might benefit!

> *"Empowering personalized tech through color & code."* 🎨🧠
