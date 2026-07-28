"""
Main GUI application module for Anode Tracking System.
"""

import logging
import os
from datetime import datetime
from typing import Optional

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from tkinter import Button, Frame, Label, StringVar, Toplevel, ttk, messagebox

from camera.camera_handler import CameraHandler
from config import AppConfig, ExportConfig
from database.db_manager import DatabaseManager
from gui.styles import Colors, Dimensions, Fonts
from ocr.ocr_engine import DetectionResult, OCREngine
from utils.helpers import format_time_delta

logger = logging.getLogger(__name__)


class AnodeTrackerApp:
    """Main application class for Anode Tracking System GUI."""
    
    def __init__(self, config: AppConfig):
        """Initialize the application.
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        self._current_anode: StringVar = StringVar(value="")
        
        # Initialize components
        self._camera = CameraHandler(config.camera)
        self._ocr = OCREngine(config.ocr)
        self._db = DatabaseManager(config.database)
        
        # Build GUI
        self._root = None
        self._camera_label: Optional[Label] = None
        self._anode_label: Optional[Label] = None
        
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def _create_root_window(self) -> None:
        """Create and configure the main root window."""
        import tkinter as tk
        
        self._root = tk.Tk()
        self._root.title(self.config.ui.app_title)
        self._root.configure(background=Colors.BACKGROUND)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_header(self) -> None:
        """Create the application header."""
        header_label = Label(
            self._root,
            text=self.config.ui.header_text,
            font=Fonts.HEADER,
            bg=Colors.HEADER_BG,
            fg=Colors.HEADER_FG,
        )
        header_label.pack(fill="x", padx=10, pady=10)
    
    def _create_camera_display(self) -> None:
        """Create the camera feed display area."""
        self._camera_label = Label(self._root, bg=Colors.CAMERA_BG)
        self._camera_label.pack(pady=Dimensions.CAMERA_LABEL_PADDING)
    
    def _create_anode_display(self) -> None:
        """Create the anode number display label."""
        self._anode_label = Label(
            self._root,
            textvariable=self._current_anode,
            font=Fonts.LABEL,
            bg=Colors.BACKGROUND,
        )
        self._anode_label.pack(side="bottom", fill="x", pady=Dimensions.LABEL_PADDING_Y)
    
    def _create_buttons(self) -> None:
        """Create action buttons."""
        # Info button
        info_button = Button(
            self._root,
            text="Info",
            command=self._show_info_window,
            font=Fonts.BUTTON,
            bg=Colors.BUTTON_INFO_BG,
            fg=Colors.BUTTON_INFO_FG,
            relief="flat",
        )
        info_button.pack(side="left", padx=Dimensions.BUTTON_PADDING_X, pady=Dimensions.BUTTON_PADDING_Y)
        
        # Save button
        save_button = Button(
            self._root,
            text="Save",
            command=self._on_save_clicked,
            font=Fonts.BUTTON,
            bg=Colors.BUTTON_SAVE_BG,
            fg=Colors.BUTTON_SAVE_FG,
            relief="flat",
        )
        save_button.pack(side="left", padx=Dimensions.BUTTON_PADDING_X, pady=Dimensions.BUTTON_PADDING_Y)
        
        # Close button
        close_button = Button(
            self._root,
            text="Close",
            command=self._on_close,
            font=Fonts.BUTTON,
            bg=Colors.BUTTON_CLOSE_BG,
            fg=Colors.BUTTON_CLOSE_FG,
            relief="flat",
        )
        close_button.pack(side="right", padx=Dimensions.BUTTON_PADDING_X, pady=Dimensions.BUTTON_PADDING_Y)
    
    def _build_gui(self) -> None:
        """Build the complete GUI."""
        self._create_root_window()
        self._create_header()
        self._create_camera_display()
        self._create_anode_display()
        self._create_buttons()
    
    def _convert_frame_to_photo(self, frame: np.ndarray) -> ImageTk.PhotoImage:
        """Convert OpenCV frame to Tkinter PhotoImage.
        
        Args:
            frame: OpenCV BGR frame
            
        Returns:
            PhotoImage for Tkinter display
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        return ImageTk.PhotoImage(image=frame_pil)
    
    def _draw_detections(
        self, frame: np.ndarray, detections: list
    ) -> np.ndarray:
        """Draw bounding boxes and text on frame.
        
        Args:
            frame: OpenCV frame to draw on
            detections: List of DetectionResult objects
            
        Returns:
            Frame with drawn detections
        """
        for detection in detections:
            bbox = detection.bbox.astype(np.int32)
            cv2.rectangle(
                frame,
                tuple(bbox[0]),
                tuple(bbox[2]),
                Colors.BBOX_COLOR,
                Dimensions.BBOX_THICKNESS,
            )
            cv2.putText(
                frame,
                detection.text,
                tuple(bbox[0]),
                cv2.FONT_HERSHEY_COMPLEX,
                Dimensions.TEXT_FONT_SCALE,
                Colors.TEXT_COLOR,
                Dimensions.TEXT_THICKNESS,
            )
        return frame
    
    def _update_camera_feed(self) -> None:
        """Update the camera feed display with OCR processing."""
        if not self._camera.is_running:
            return
        
        ret, frame = self._camera.read_frame()
        
        if ret and frame is not None:
            # Get all valid detections
            detections = self._ocr.get_all_valid_detections(frame)
            
            # Get best detection for display
            best_detection = self._ocr.get_best_detection(frame)
            
            # Update anode label
            if best_detection:
                self._current_anode.set(f"Anode Number: {best_detection.text}")
            else:
                self._current_anode.set("Anode Number: ")
            
            # Draw detections on frame
            if detections:
                frame = self._draw_detections(frame, detections)
            
            # Update display
            self._photo_image = self._convert_frame_to_photo(frame)
            self._camera_label.imgtk = self._photo_image
            self._camera_label.configure(image=self._photo_image)
        
        # Check for 's' key press to save text
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            self._save_text_to_file()
        
        # Schedule next update
        if self._root:
            self._root.after(10, self._update_camera_feed)
    
    def _save_text_to_file(self) -> None:
        """Save current detected text to file."""
        text = self._current_anode.get().split(": ")[-1]
        if text:
            try:
                with open("captured_text.txt", "w") as file:
                    file.write(text + "\n")
                logger.info(f"Saved text to file: {text}")
            except IOError as e:
                logger.error(f"Failed to save text to file: {e}")
    
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        text = self._current_anode.get().split(": ")[-1]
        
        if not text:
            messagebox.showwarning(
                "No Anode No Captured",
                "Please capture Anode No. first."
            )
            return
        
        success, message = self._db.save_or_update_anode(text)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def _show_info_window(self) -> None:
        """Display the info window with database records."""
        try:
            data = self._db.get_all_records()
            self._create_info_window(data)
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving data: {e}")
    
    def _create_info_window(self, data: list) -> None:
        """Create and populate the info window.
        
        Args:
            data: List of database records
        """
        info_window = Toplevel(self._root)
        info_window.title("Stem Analysis Info")
        info_window.configure(background="white")
        
        # Define columns
        columns = ("Pot Number", "Date Entry", "Time Entry", "Date Out", "Time Out")
        
        # Create treeview
        tree = ttk.Treeview(info_window, columns=columns, show="headings")
        tree.pack(fill="both", expand=True)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        
        # Insert data
        for row in data:
            # Format time deltas if needed
            formatted_row = []
            for item in row:
                if hasattr(item, 'total_seconds'):  # timedelta
                    formatted_row.append(format_time_delta(item))
                else:
                    formatted_row.append(str(item) if item else "")
            tree.insert("", "end", values=formatted_row)
        
        # Download button
        download_button = Button(
            info_window,
            text="Download",
            command=lambda: self._export_to_excel(data),
            font=Fonts.BUTTON,
            bg=Colors.BUTTON_DOWNLOAD_BG,
            fg=Colors.BUTTON_DOWNLOAD_FG,
            relief="flat",
        )
        download_button.pack(pady=10)
    
    def _export_to_excel(self, data: list) -> None:
        """Export data to Excel file.
        
        Args:
            data: List of database records
        """
        try:
            columns = ["Pot Number", "Date Entry", "Time Entry", "Date Out", "Time Out"]
            df = pd.DataFrame(data, columns=columns)
            
            # Format time columns
            for col in ["Time Entry", "Time Out"]:
                df[col] = df[col].apply(
                    lambda x: format_time_delta(x) if hasattr(x, 'total_seconds') else str(x) if x else ""
                )
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stem_analysis_{timestamp}.xlsx"
            filepath = os.path.join(self.config.export_config.download_dir, filename)
            
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Export Successful", f"Data exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {e}")
    
    def _on_close(self) -> None:
        """Handle application close."""
        logger.info("Closing application...")
        self._camera.close()
        self._db.close()
        if self._root:
            self._root.destroy()
    
    def run(self) -> None:
        """Run the application."""
        self._build_gui()
        
        # Open camera
        if not self._camera.open():
            messagebox.showerror(
                "Camera Error",
                "Failed to open camera. Please check your camera connection."
            )
            self._on_close()
            return
        
        # Start camera feed update loop
        self._root.after(100, self._update_camera_feed)
        
        # Run main loop
        self._root.mainloop()