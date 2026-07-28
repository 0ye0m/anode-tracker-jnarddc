"""
UI styling constants for Anode Tracking System.
"""


class Colors:
    """Color palette for the application."""
    BACKGROUND = "#FBEEC1"
    HEADER_BG = "#0077cc"
    HEADER_FG = "white"
    CAMERA_BG = "#f0f0f0"
    BUTTON_SAVE_BG = "#cc0000"
    BUTTON_SAVE_FG = "white"
    BUTTON_INFO_BG = "#009933"
    BUTTON_INFO_FG = "white"
    BUTTON_CLOSE_BG = "#333333"
    BUTTON_CLOSE_FG = "white"
    BUTTON_DOWNLOAD_BG = "#2196F3"
    BUTTON_DOWNLOAD_FG = "white"
    BBOX_COLOR = (0, 255, 0)  # Green
    TEXT_COLOR = (255, 0, 0)  # Blue (OpenCV BGR)


class Fonts:
    """Font configurations for the application."""
    HEADER = ("Times New Roman", 25, "bold")
    LABEL = ("Times New Roman", 14)
    BUTTON = ("Times New Roman", 14)
    TABLE_HEADER = ("Times New Roman", 12, "bold")
    TABLE_CELL = ("Times New Roman", 11)


class Dimensions:
    """Size and spacing constants."""
    BBOX_THICKNESS = 5
    TEXT_THICKNESS = 2
    TEXT_FONT_SCALE = 0.65
    BUTTON_PADDING_X = 10
    BUTTON_PADDING_Y = 5
    LABEL_PADDING_Y = 10
    CAMERA_LABEL_PADDING = 10