"""
Configuration management module for Anode Tracking System.
Handles loading settings from environment variables and providing defaults.
"""

import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "root"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("DB_NAME", "jnarddc"))
    
    @property
    def connection_params(self) -> dict:
        """Return database connection parameters as a dictionary."""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }


@dataclass
class OCRConfig:
    """OCR engine configuration."""
    confidence_threshold: float = field(
        default_factory=lambda: float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.5"))
    )
    languages: List[str] = field(
        default_factory=lambda: os.getenv("OCR_LANGUAGES", "en").split(",")
    )
    use_gpu: bool = False  # Set to True if CUDA is available


@dataclass
class CameraConfig:
    """Camera configuration."""
    index: int = field(
        default_factory=lambda: int(os.getenv("CAMERA_INDEX", "0"))
    )
    width: int = field(
        default_factory=lambda: int(os.getenv("CAMERA_WIDTH", "640"))
    )
    height: int = field(
        default_factory=lambda: int(os.getenv("CAMERA_HEIGHT", "480"))
    )


@dataclass
class ExportConfig:
    """Export configuration."""
    download_dir: str = field(
        default_factory=lambda: os.path.expanduser(
            os.getenv("DOWNLOAD_DIR", "~/Downloads")
        )
    )


@dataclass
class UIConfig:
    """User interface configuration."""
    app_title: str = field(
        default_factory=lambda: os.getenv("APP_TITLE", "Anode Tracker")
    )
    bg_color: str = field(
        default_factory=lambda: os.getenv("APP_BG_COLOR", "#FBEEC1")
    )
    header_text: str = "Jawaharlal Nehru Aluminum Research Development and Design Centre"
    header_font: tuple = ("Times New Roman", 25, "bold")
    header_bg_color: str = "#0077cc"
    header_fg_color: str = "white"
    button_font: tuple = ("Times New Roman", 14)


class AppConfig:
    """Main application configuration container."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.ocr = OCRConfig()
        self.camera = CameraConfig()
        self.export_config = ExportConfig()
        self.ui = UIConfig()


# Global configuration instance
config = AppConfig()