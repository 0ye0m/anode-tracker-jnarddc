"""
OCR engine module for text detection and recognition.
Uses EasyOCR for optical character recognition.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import easyocr
import numpy as np

from config import OCRConfig

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Represents a single OCR detection result."""
    bbox: np.ndarray
    text: str
    confidence: float
    
    @property
    def top_left(self) -> Tuple[int, int]:
        """Get top-left corner of bounding box."""
        return tuple(self.bbox[0].astype(int))
    
    @property
    def bottom_right(self) -> Tuple[int, int]:
        """Get bottom-right corner of bounding box."""
        return tuple(self.bbox[2].astype(int))


class OCREngine:
    """Handles OCR operations using EasyOCR."""
    
    def __init__(self, config: OCRConfig):
        """Initialize OCR engine with configuration.
        
        Args:
            config: OCR configuration object
        """
        self.config = config
        self._reader = None
        self._initialize_reader()
    
    def _initialize_reader(self) -> None:
        """Initialize the EasyOCR reader."""
        try:
            self._reader = easyocr.Reader(
                self.config.languages,
                gpu=self.config.use_gpu,
                verbose=False
            )
            logger.info(
                f"OCR engine initialized with languages: {self.config.languages}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize OCR engine: {e}")
            raise
    
    def detect_text(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect text in an image frame.
        
        Args:
            frame: OpenCV image frame (BGR format)
            
        Returns:
            List of DetectionResult objects
        """
        if self._reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        try:
            raw_results = self._reader.readtext(frame)
            detections = []
            
            for bbox, text, confidence in raw_results:
                detection = DetectionResult(
                    bbox=np.array(bbox),
                    text=text,
                    confidence=confidence
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during text detection: {e}")
            return []
    
    def get_best_detection(
        self, frame: np.ndarray
    ) -> Optional[DetectionResult]:
        """Get the best (highest confidence) text detection.
        
        Args:
            frame: OpenCV image frame (BGR format)
            
        Returns:
            Best DetectionResult or None if no valid detection
        """
        detections = self.detect_text(frame)
        
        # Filter by confidence threshold
        valid_detections = [
            d for d in detections
            if d.confidence >= self.config.confidence_threshold
        ]
        
        if not valid_detections:
            return None
        
        # Return the highest confidence detection
        return max(valid_detections, key=lambda d: d.confidence)
    
    def get_detected_text(self, frame: np.ndarray) -> Optional[str]:
        """Get the text of the best detection.
        
        Args:
            frame: OpenCV image frame (BGR format)
            
        Returns:
            Detected text string or None
        """
        detection = self.get_best_detection(frame)
        return detection.text if detection else None
    
    def get_all_valid_detections(
        self, frame: np.ndarray
    ) -> List[DetectionResult]:
        """Get all detections above confidence threshold.
        
        Args:
            frame: OpenCV image frame (BGR format)
            
        Returns:
            List of valid DetectionResult objects
        """
        detections = self.detect_text(frame)
        return [
            d for d in detections
            if d.confidence >= self.config.confidence_threshold
        ]