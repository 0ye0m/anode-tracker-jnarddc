"""
Unit tests for OCR engine module.
"""

import numpy as np
import pytest
from unittest.mock import Mock, patch

from config import OCRConfig
from ocr.ocr_engine import OCREngine, DetectionResult


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""
    
    def test_top_left_property(self):
        bbox = np.array([[10, 20], [100, 20], [100, 100], [10, 100]])
        result = DetectionResult(bbox=bbox, text="TEST", confidence=0.95)
        assert result.top_left == (10, 20)
    
    def test_bottom_right_property(self):
        bbox = np.array([[10, 20], [100, 20], [100, 100], [10, 100]])
        result = DetectionResult(bbox=bbox, text="TEST", confidence=0.95)
        assert result.bottom_right == (100, 100)


class TestOCREngine:
    """Tests for OCREngine class."""
    
    @pytest.fixture
    def ocr_config(self):
        return OCRConfig(confidence_threshold=0.5, languages=["en"])
    
    @pytest.fixture
    def mock_reader(self):
        with patch("easyocr.Reader") as mock:
            yield mock
    
    def test_initialization(self, ocr_config, mock_reader):
        engine = OCREngine(ocr_config)
        mock_reader.assert_called_once_with(["en"], gpu=False, verbose=False)
    
    def test_detect_text_returns_empty_on_error(self, ocr_config, mock_reader):
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.side_effect = Exception("Test error")
        mock_reader.return_value = mock_reader_instance
        
        engine = OCREngine(ocr_config)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        results = engine.detect_text(frame)
        
        assert results == []
    
    def test_get_detected_text_returns_none_when_empty(self, ocr_config, mock_reader):
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = []
        mock_reader.return_value = mock_reader_instance
        
        engine = OCREngine(ocr_config)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        text = engine.get_detected_text(frame)
        
        assert text is None