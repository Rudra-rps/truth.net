"""
Metadata Agent - EXIF and File Metadata Analysis
Analyzes image/video metadata for manipulation indicators
"""
import exifread
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import os


class MetadataAnalyzer:
    """Analyzes file metadata for manipulation indicators"""
    
    def __init__(self):
        """Initialize metadata analyzer"""
        pass
    
    def analyze_image(self, image_path: str) -> dict:
        """
        Analyze image file metadata for manipulation indicators
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict with metadata analysis results
        """
        signals = []
        metadata = {}
        risk_score = 0.0
        
        try:
            # Extract EXIF data
            exif_data = self._extract_exif(image_path)
            metadata["exif"] = exif_data
            
            # Check for missing/suspicious EXIF
            exif_signals = self._check_exif_integrity(exif_data)
            signals.extend(exif_signals)
            
            # Check file timestamps
            timestamp_signals = self._check_timestamps(image_path)
            signals.extend(timestamp_signals)
            
            # Check for editing software traces
            software_signals = self._check_software_traces(exif_data)
            signals.extend(software_signals)
            
            # Check file format consistency
            format_signals = self._check_format_consistency(image_path)
            signals.extend(format_signals)
            
            # Calculate risk score based on signals
            if signals:
                risk_score = min(
                    sum(s["confidence"] for s in signals) / len(signals),
                    1.0
                )
            
        except Exception as e:
            signals.append({
                "type": "analysis_error",
                "confidence": 0.3,
                "description": f"Error analyzing metadata: {str(e)}"
            })
            risk_score = 0.3
        
        return {
            "signals": signals,
            "risk_score": risk_score,
            "metadata": metadata
        }
    
    def analyze_video(self, video_path: str) -> dict:
        """
        Analyze video file metadata
        
        Args:
            video_path: Path to the video file
            
        Returns:
            dict with metadata analysis results
        """
        signals = []
        metadata = {}
        risk_score = 0.0
        
        try:
            # Check file timestamps
            timestamp_signals = self._check_timestamps(video_path)
            signals.extend(timestamp_signals)
            
            # Check file extension vs actual format
            format_signals = self._check_video_format(video_path)
            signals.extend(format_signals)
            
            # Get basic file info
            metadata["file_info"] = self._get_file_info(video_path)
            
            # Calculate risk score
            if signals:
                risk_score = min(
                    sum(s["confidence"] for s in signals) / len(signals),
                    1.0
                )
            
        except Exception as e:
            signals.append({
                "type": "analysis_error",
                "confidence": 0.3,
                "description": f"Error analyzing metadata: {str(e)}"
            })
            risk_score = 0.3
        
        return {
            "signals": signals,
            "risk_score": risk_score,
            "metadata": metadata
        }
    
    def _extract_exif(self, image_path: str) -> Dict[str, Any]:
        """Extract EXIF data from image"""
        exif_dict = {}
        
        try:
            # Try PIL first
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[str(tag)] = str(value)
        except:
            pass
        
        try:
            # Also try exifread for more comprehensive data
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                for tag, value in tags.items():
                    if tag not in ['JPEGThumbnail', 'TIFFThumbnail']:
                        exif_dict[tag] = str(value)
        except:
            pass
        
        return exif_dict
    
    def _check_exif_integrity(self, exif_data: Dict[str, Any]) -> List[Dict]:
        """Check for suspicious EXIF patterns"""
        signals = []
        
        # Check if EXIF data is completely missing
        if not exif_data or len(exif_data) == 0:
            signals.append({
                "type": "missing_exif",
                "confidence": 0.6,
                "description": "No EXIF data found - possible metadata stripping"
            })
        
        # Check for missing camera information
        camera_tags = ["Make", "Model", "EXIF Make", "EXIF Model"]
        has_camera_info = any(tag in exif_data for tag in camera_tags)
        
        if exif_data and not has_camera_info:
            signals.append({
                "type": "missing_camera_info",
                "confidence": 0.5,
                "description": "Camera information missing from EXIF"
            })
        
        # Check for datetime inconsistencies
        datetime_tags = [
            "DateTime", "DateTimeOriginal", "DateTimeDigitized",
            "EXIF DateTimeOriginal", "EXIF DateTimeDigitized"
        ]
        datetimes = []
        for tag in datetime_tags:
            if tag in exif_data:
                try:
                    dt_str = exif_data[tag]
                    datetimes.append(dt_str)
                except:
                    pass
        
        # If multiple datetimes exist and differ significantly, flag it
        if len(set(datetimes)) > 2:
            signals.append({
                "type": "datetime_mismatch",
                "confidence": 0.7,
                "description": "Inconsistent timestamps in EXIF data"
            })
        
        return signals
    
    def _check_timestamps(self, file_path: str) -> List[Dict]:
        """Check file system timestamps for anomalies"""
        signals = []
        
        try:
            stat_info = os.stat(file_path)
            
            created_time = stat_info.st_ctime
            modified_time = stat_info.st_mtime
            accessed_time = stat_info.st_atime
            
            # Check if modified time is before created time (impossible normally)
            if modified_time < created_time:
                signals.append({
                    "type": "timestamp_anomaly",
                    "confidence": 0.8,
                    "description": "File modified before creation - timestamp manipulation detected"
                })
            
            # Check if file is very recently created but claims to be old
            current_time = datetime.now().timestamp()
            age_days = (current_time - created_time) / (60 * 60 * 24)
            
            if age_days < 1:  # File created in last 24 hours
                signals.append({
                    "type": "recent_creation",
                    "confidence": 0.2,
                    "description": f"File created recently ({age_days:.1f} days ago)"
                })
        except Exception as e:
            pass
        
        return signals
    
    def _check_software_traces(self, exif_data: Dict[str, Any]) -> List[Dict]:
        """Check for editing software traces in EXIF"""
        signals = []
        
        editing_software = [
            "Adobe Photoshop", "GIMP", "Paint.NET", "Pixlr",
            "Corel", "Affinity", "Lightroom", "Photoshop Express"
        ]
        
        software_tags = ["Software", "ProcessingSoftware", "EXIF Software"]
        
        for tag in software_tags:
            if tag in exif_data:
                software_value = str(exif_data[tag])
                for editor in editing_software:
                    if editor.lower() in software_value.lower():
                        signals.append({
                            "type": "editing_software_detected",
                            "confidence": 0.4,
                            "description": f"Editing software detected: {editor}"
                        })
                        break
        
        return signals
    
    def _check_format_consistency(self, image_path: str) -> List[Dict]:
        """Check if file extension matches actual format"""
        signals = []
        
        try:
            with Image.open(image_path) as img:
                actual_format = img.format
                file_extension = Path(image_path).suffix.upper().replace('.', '')
                
                # Common format mismatches
                format_map = {
                    'JPG': 'JPEG',
                    'JPEG': 'JPEG',
                    'PNG': 'PNG',
                    'BMP': 'BMP',
                    'GIF': 'GIF'
                }
                
                expected_format = format_map.get(file_extension, file_extension)
                
                if actual_format != expected_format:
                    signals.append({
                        "type": "format_mismatch",
                        "confidence": 0.5,
                        "description": f"File extension ({file_extension}) doesn't match actual format ({actual_format})"
                    })
        except:
            pass
        
        return signals
    
    def _check_video_format(self, video_path: str) -> List[Dict]:
        """Check video file format consistency"""
        signals = []
        
        # Basic check - just verify file extension is common video format
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        file_ext = Path(video_path).suffix.lower()
        
        if file_ext not in video_extensions:
            signals.append({
                "type": "unusual_format",
                "confidence": 0.3,
                "description": f"Unusual video file extension: {file_ext}"
            })
        
        return signals
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        try:
            stat_info = os.stat(file_path)
            return {
                "size_bytes": stat_info.st_size,
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "file_name": Path(file_path).name,
                "file_extension": Path(file_path).suffix
            }
        except:
            return {}
