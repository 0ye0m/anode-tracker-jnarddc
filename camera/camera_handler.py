"""
Camera handler module for video capture and frame processing.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np

from config import CameraConfig

logger = logging.getLogger(__name__)


class CameraHandler:
    """Handles camera operations for video capture."""
    
    def __init__(self, config: CameraConfig):
        """Initialize camera handler with configuration.
        
        Args:
            config: Camera configuration object
        """
        self.config = config
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_running = False
    
    @property
    def is_running(self) -> bool:
        """Check if camera is currently running."""
        return self._is_running and self._cap is not None and self._cap.isOpened()
    
    def open(self) -> bool:
        """Open the camera.
        
        Returns:
            True if camera opened successfully, False otherwise
        """
        try:
            self._cap = cv2.VideoCapture(self.config.index)
            
            if not self._cap.isOpened():
                logger.error(f"Failed to open camera at index {self.config.index}")
                return False
            
            # Set camera resolution
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            
            self._is_running = True
            logger.info(
                f"Camera opened successfully at index {self.config.index}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a single frame from the camera.
        
        Returns:
            Tuple of (success: bool, frame: np.ndarray or None)
        """
        if not self.is_running:
            return False, None
        
        ret, frame = self._cap.read()
        return ret, frame
    
    def close(self) -> None:
        """Close the camera and release resources."""
        if self._cap is not None:
            self._cap.release()
            self._is_running = False
            logger.info("Camera closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()