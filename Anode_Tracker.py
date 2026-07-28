import cv2
import easyocr
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk
import pandas as pd
import os


# Set the database credentials
db_host = "localhost"
db_user = "root"
db_password = "root"
db_name = "jnarddc"

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"], gpu=False)

# Set a threshold for confidence score
threshold = 0.5

# Global variable to hold PhotoImage object
photo_image = None


# Function to capture text when 's' is clicked
def capture_text(frame):
    text_result = None
    text_results = reader.readtext(frame)
    for bbox, text, score in text_results:
        if score > threshold:
            text_result = text
            break
    return text_result


# Function to save captured text
def save_text(text_result):
    if text_result:
        with open("captured_text.txt", "w") as file:
            file.write(text_result + "\n")


# Function to create PhotoImage object
def create_photo_image(frame):
    global photo_image
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_pil = Image.fromarray(frame_rgb)
    photo_image = ImageTk.PhotoImage(image=frame_pil)


# Function to open camera window and perform OCR continuously
def open_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            text_result = capture_text(frame)
            if text_result:
                anode_number_label.config(text="Anode Number: " + text_result)
            else:
                anode_number_label.config(text="Anode Number: ")  # Clear the label if no text is recognized
            text_results = reader.readtext(frame)
            for bbox, text, score in text_results:
                if score > threshold:
                    bbox = np.array(bbox, dtype=np.int32)
                    cv2.rectangle(frame, tuple(bbox[0]), tuple(bbox[2]), (0, 255, 0), 5)
                    cv2.putText(
                        frame,
                        text,
                        tuple(bbox[0]),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.65,
                        (255, 0, 0),
                        2,
                    )
            # Call function to create PhotoImage object
            create_photo_image(frame)
            # Update the label with the new frame
            camera_label.imgtk = photo_image
            camera_label.configure(image=photo_image)
            # Keep the camera window open until closed manually
            root.update()
            if cv2.waitKey(1) & 0xFF == ord("s"):
                save_text(text_result)
                break
    cap.release()


# Function to retrieve and display stem_analysis table
def display_stem_analysis():
    try:
        connection = mysql.connector.connect(
            host=db_host, user=db_user, password=db_password, database=db_name
        )
        cursor = connection.cursor()

        # Fetch data from stem_analysis table
        cursor.execute(
            "SELECT pot_number, date_entry, time_in, date_out, time_out FROM stem_analysis"
        )
        data = cursor.fetchall()

        # Create a new window to display the data
        info_window = tk.Toplevel(root)
        info_window.title("Stem Analysis Info")
        info_window.configure(background="white")

        # Create a treeview to display the data
        tree = ttk.Treeview(
            info_window,
            columns=("Pot Number", "Date Entry", "Time Entry", "Date Out", "Time Out"),
            show="headings",
        )
        tree.pack(fill="both", expand=True)

        # Define column headings
        tree.heading("Pot Number", text="Pot Number")
        tree.heading("Date Entry", text="Date Entry")
        tree.heading("Time Entry", text="Time Entry")
        tree.heading("Date Out", text="Date Out")
        tree.heading("Time Out", text="Time Out")

        # Insert data into the treeview
        for row in data:
            tree.insert("", "end", values=row)

        # Add Download button to export data to Excel
        download_button = tk.Button(
            info_window, text="Download", command=lambda: export_to_excel(data)
        )
        download_button.pack()

    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving data: {e}")

    finally:
        if "connection" in locals():
            connection.close()
            print("Connection closed")


# Function to export data to Excel
def export_to_excel(data):
    try:
        df = pd.DataFrame(
            data,
            columns=["Pot Number", "Date Entry", "Time Entry", "Date Out", "Time Out"],
        )

        # Convert timedelta columns to strings representing time
        df["Time Entry"] = df["Time Entry"].astype(str).str[-8:]
        df["Time Out"] = df["Time Out"].astype(str).str[-8:]

        download_folder = os.path.expanduser("~/Downloads")
        excel_file = os.path.join(download_folder, "stem_analysis.xlsx")
        df.to_excel(excel_file, index=False)
        messagebox.showinfo("Export Successful", f"Data exported to {excel_file}")

    except Exception as e:
        messagebox.showerror("Export Error", f"Error exporting data: {e}")


def save_button_clicked():
    text_result = anode_number_label.cget("text").split(": ")[-1]
    if not text_result:
        messagebox.showwarning("No Anode No Captured", "Please capture Anode No. first.")
        return

    if text_result == "":
        messagebox.showerror("Anode No. Recognition Error", "No Anode No. recognized. Unable to save.")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    try:
        connection = mysql.connector.connect(
            host=db_host, user=db_user, password=db_password, database=db_name
        )
        cursor = connection.cursor()

        # Check if anode number already exists for today's date
        cursor.execute(
            "SELECT * FROM stem_analysis WHERE pot_number = %s AND date_entry = %s",
            (text_result, current_date),
        )
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Update the existing entry with date_out and time_out
            cursor.execute(
                "UPDATE stem_analysis SET date_out = %s, time_out = %s WHERE pot_number = %s AND date_entry = %s",
                (current_date, current_time, text_result, current_date),
            )
            connection.commit()
            messagebox.showinfo("Anode Updated", "Existing Anode entry updated with Date Out and Time Out.")
        else:
            # Insert new entry if no existing entry for today
            cursor.execute(
                "INSERT INTO stem_analysis (date_entry, time_in, pot_number) VALUES (%s, %s, %s)",
                (current_date, current_time, text_result),
            )
            connection.commit()
            messagebox.showinfo("Anode Saved", "Anode saved to the database")

    except Exception as e:
        messagebox.showerror("Error", f"Error saving Anode: {e}")

    finally:
        if "connection" in locals():
            connection.close()
            print("Connection closed")



def close_window():
    root.destroy()


# Create GUI window
root = tk.Tk()
root.title("Anode Tracker")
root.configure(background="#FBEEC1")  

# Create header label with increased font size
header_label = tk.Label(
    root,
    text="Jawaharlal Nehru Aluminum Research Development and Design Centre",
    font=("Times New Roman", 25, "bold"),  # Larger, bold font
    bg="#0077cc",  # Blue background
    fg="white",  # White text
)
header_label.pack(fill="x", padx=10, pady=10)

# Create Anode Number label
anode_number_label = tk.Label(
    root, text="Anode Number:", font=("Times New Roman", 14), bg="#FBEEC1"
)
anode_number_label.pack(side="bottom", fill="x", pady=10)

# Create label to display camera feed
camera_label = tk.Label(root, bg="#f0f0f0")
camera_label.pack(pady=10)

# Create buttons with increased font size and styled background
info_button = tk.Button(
    root,
    text="Info",
    command=display_stem_analysis,
    font=("Times New Roman", 14),
    bg="#009933",  # Green background
    fg="white",  # White text
    relief=tk.FLAT,  # Flat button style
)
info_button.pack(side="left", padx=10, pady=5)

save_button = tk.Button(
    root,
    text="Save",
    command=save_button_clicked,
    font=("Times New Roman", 14),
    bg="#cc0000",  # Red background
    fg="white",  # White text
    relief=tk.FLAT,  # Flat button style
)
save_button.pack(side="left", padx=10, pady=5)

close_button = tk.Button(
    root,
    text="Close",
    command=close_window,
    font=("Times New Roman", 14),
    bg="#333333",  # Dark gray background
    fg="white",  # White text
    relief=tk.FLAT,  # Flat button style
)
close_button.pack(side="right", padx=10, pady=5)

# Call open_camera after the root window is fully initialized
root.after(0, open_camera)

# Run the main loop
root.mainloop()