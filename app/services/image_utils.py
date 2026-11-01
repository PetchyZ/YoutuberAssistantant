import cv2
import numpy as np

class ImageAnalyzerUtil:
    @staticmethod
    def analyze_basic_metrics(image_bytes: bytes) -> dict:
        """
        calculate contrast and brightness from Image Bytes
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) #data and reading method (read with colors)

        if img is None:
            raise ValueError("Could not decode image bytes.")

        # Convert to Grayscale
        #Y = 0.299xR + 0.587xG + 0.114xB
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Brightbess = Mean of grayscale values
        #gpt-gen
        brightness = float(np.mean(gray))
        
        # Contrast = Standard deviation of grayscale values
        contrast = float(np.std(gray))

        return {
            "brightness_score" : round(brightness, 2), #0-255 (Optimal ~100-180)
            "contrast_score": round(contrast, 2), # Higher mean more contrast
            "resolution": f"{img.shape[1]}x{img.shape[0]}" 
        }