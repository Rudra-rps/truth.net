"""
Visual Agent - Face Detection and Artifact Analysis
Uses MediaPipe for face detection (no cmake required on Windows)
"""
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import List, Tuple


class VisualAnalyzer:
    """Analyzes visual media for deepfake artifacts"""
    
    def __init__(self):
        # Initialize MediaPipe Face Detection
        try:
            # Try new API first (mediapipe 0.10+)
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # Download face detection model if needed
            model_path = self._get_face_detection_model()
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceDetectorOptions(base_options=base_options)
            self.face_detector = vision.FaceDetector.create_from_options(options)
            self.use_new_api = True
        except:
            # Fall back to legacy API
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
            self.use_new_api = False
    
    def _get_face_detection_model(self) -> str:
        """Download face detection model if needed"""
        import urllib.request
        from pathlib import Path
        
        model_dir = Path.home() / ".mediapipe" / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "detector.tflite"
        
        if not model_path.exists():
            url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
            urllib.request.urlretrieve(url, model_path)
        
        return str(model_path)
        
    def analyze_image(self, image_path: str) -> dict:
        """Analyze a single image for artifacts"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self._detect_faces(rgb_image)
        
        # Analyze artifacts
        artifacts = []
        risk_score = 0.0
        
        if len(faces) == 0:
            artifacts.append({
                "type": "no_faces_detected",
                "confidence": 0.3,
                "description": "No faces detected in the image"
            })
            risk_score = 0.2
        else:
            # Check for artifacts in face regions
            for face_box in faces:
                face_artifacts = self._analyze_face_region(image, face_box)
                artifacts.extend(face_artifacts)
                
            # Calculate risk score based on artifacts
            if artifacts:
                risk_score = min(sum(a["confidence"] for a in artifacts) / len(artifacts), 1.0)
        
        return {
            "faces_detected": len(faces),
            "artifacts": artifacts,
            "risk_score": risk_score
        }
    
    def analyze_video(self, video_path: str, sample_frames: int = 10) -> dict:
        """Analyze video by sampling frames"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(total_frames // sample_frames, 1)
        
        all_artifacts = []
        frame_count = 0
        analyzed_frames = 0
        
        while cap.isOpened() and analyzed_frames < sample_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                faces = self._detect_faces(rgb_frame)
                
                # Analyze each face
                for face_box in faces:
                    face_artifacts = self._analyze_face_region(frame, face_box)
                    all_artifacts.extend(face_artifacts)
                
                analyzed_frames += 1
            
            frame_count += 1
        
        cap.release()
        
        # Calculate overall risk score
        risk_score = 0.0
        if all_artifacts:
            risk_score = min(sum(a["confidence"] for a in all_artifacts) / len(all_artifacts), 1.0)
        
        return {
            "total_frames": total_frames,
            "analyzed_frames": analyzed_frames,
            "artifacts": all_artifacts,
            "risk_score": risk_score
        }
    
    def _detect_faces(self, rgb_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using MediaPipe"""
        faces = []
        h, w, _ = rgb_image.shape
        
        if self.use_new_api:
            # Use new API
            from mediapipe.tasks.python.components.containers import NormalizedRect
            from mediapipe import Image, ImageFormat
            
            # Convert numpy array to MediaPipe Image
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_image)
            
            # Detect faces
            detection_result = self.face_detector.detect(mp_image)
            
            if detection_result.detections:
                for detection in detection_result.detections:
                    bbox = detection.bounding_box
                    x = bbox.origin_x
                    y = bbox.origin_y
                    width = bbox.width
                    height = bbox.height
                    faces.append((x, y, width, height))
        else:
            # Use legacy API
            results = self.face_detection.process(rgb_image)
            
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    faces.append((x, y, width, height))
        
        return faces
    
    def _analyze_face_region(self, image: np.ndarray, face_box: Tuple[int, int, int, int]) -> List[dict]:
        """Analyze a face region for artifacts"""
        x, y, w, h = face_box
        face_region = image[y:y+h, x:x+w]
        
        if face_region.size == 0:
            return []
        
        artifacts = []
        
        # 1. Check for blurriness (common in deepfakes)
        blur_score = self._calculate_blur(face_region)
        if blur_score > 100:  # High blur = suspicious
            artifacts.append({
                "type": "face_blur",
                "confidence": min(blur_score / 200, 1.0),
                "description": f"Unusual blur detected in face region (score: {blur_score:.2f})"
            })
        
        # 2. Check for edge artifacts
        edge_score = self._detect_edge_artifacts(face_region)
        if edge_score > 0.3:
            artifacts.append({
                "type": "edge_artifacts",
                "confidence": edge_score,
                "description": f"Edge inconsistencies detected around face"
            })
        
        # 3. Check for color inconsistencies
        color_score = self._detect_color_artifacts(face_region)
        if color_score > 0.4:
            artifacts.append({
                "type": "color_artifacts",
                "confidence": color_score,
                "description": f"Color inconsistencies in face region"
            })
        
        return artifacts
    
    def _calculate_blur(self, image: np.ndarray) -> float:
        """Calculate Laplacian variance (blur detection)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def _detect_edge_artifacts(self, face_region: np.ndarray) -> float:
        """Detect edge artifacts (simple implementation)"""
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        
        # Check edge density
        edge_density = np.sum(edges > 0) / edges.size
        
        # High edge density can indicate artifacts
        if edge_density > 0.15:
            return min(edge_density * 2, 1.0)
        
        return 0.0
    
    def _detect_color_artifacts(self, face_region: np.ndarray) -> float:
        """Detect color inconsistencies"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
        
        # Calculate standard deviation of hue channel
        hue_std = np.std(hsv[:, :, 0])
        
        # Unusually high variance can indicate manipulation
        if hue_std > 30:
            return min(hue_std / 60, 1.0)
        
        return 0.0
    
    def cleanup(self):
        """Cleanup resources"""
        if self.use_new_api:
            self.face_detector.close()
        else:
            self.face_detection.close()
