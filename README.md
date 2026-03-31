# Metadata Remover

A web application that allows users to securely view and eliminate hidden metadata (EXIF data) from images, PDFs, and video files to help protect your privacy.

## Setup Instructions

Follow these steps to run the application on a new computer:

### 1. Open Terminal
Navigate to the folder where this project is located.
```bash
cd /path/to/meta_data_remover
```

### 2. Create and Activate a Virtual Environment
This keeps project dependencies isolated from the rest of your system.

**On Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Required Libraries
Wait for the terminal to show that the virtual environment is successfully activated, then install the dependencies required for the server to run:
```bash
pip install -r requirements.txt
```

### 4. Start the Application
Run the main web server:
**On Mac / Linux:**
```bash
python3 app.py
```

**On Windows:**
```cmd
python app.py
```

### 5. Access the Web Interface
Once the terminal displays that the server is active, open your favorite web browser and navigate to:
**http://127.0.0.1:5000**

---
*Note: If you prefer to test the alternative desktop application interface instead of the web version, you can run `python gui_app_1.py`.*

---

## How it Works

The project operates through a seamless connection between a web-based Frontend and a Python Backend.

**1. The User Interface (Frontend)**
- Built with standard **HTML, CSS, and JavaScript**.
- Users can drag and drop their files onto the webpage. 
- JavaScript securely sends the file to the backend server via an API request to either view or clean the file, depending on the button clicked.

**2. The Processing Logic (Backend)**
- Built in **Python** using the **Flask** web framework.
- It relies on specialized libraries to inspect file headers and extract or delete hidden data:
  - **Pillow (PIL)** for handling Images (strips EXIF tags).
  - **pypdf** for handling PDFs (wipes metadata dictionaries).
  - **ffmpeg-python** for handling Videos (copies the streams while discarding tags).

**3. Privacy & Security**
- Files are completely handled **in-memory** using temporary memory buffers (`io.BytesIO`). 
- When a file is "cleaned", the metadata is stripped and the new clean file is sent straight back to the user's browser for download. 
- The server does not permanently save, store, or log any user files, ensuring true privacy.

---

## Directory Structure

Here is a breakdown of the project layout:

```text
meta_data_remover/
├── app.py                # Main Flask web application (Entry point)
├── metadata_remover.py   # Core logic for reading and removing metadata
├── gui_app_1.py          # Alternative standalone desktop app (Tkinter)
├── requirements.txt      # Python dependencies list
├── static/               
│   ├── css/style.css     # Frontend cascading stylesheets
│   └── js/app.js         # Frontend JavaScript logic (handles API requests)
└── templates/            
    └── index.html        # Main HTML layout for the web app
```

## Detailed Code Working 

### `app.py` (The Routing Layer)
This file boots up a local Python **Flask** web server. It primarily relies on endpoints (`/api/metadata` and `/api/remove`) that patiently wait for the frontend to upload files. Once an HTTP POST request hits these routes, `app.py` takes the file object straight from Flask's request buffer, invokes functions inside `metadata_remover.py`, and securely passes the final JSON dictionary or a raw secure file stream back to the user.

### `metadata_remover.py` (The Heavy Lifting Logic)
This file is the engine of the project, executing the extraction and deletion logic:
- **`read_metadata(...)`**: Reads the extension of the uploaded byte stream, hooks it into the respective library (`Pillow`, `pypdf`, or `ffmpeg-python`), and pulls EXIF chunks and tags out, casting them into an easy-to-read dictionary.
- **`remove_metadata(...)`**: Creates completely new, clean versions of user files. 
  - *For Images*: It draws out just the raw visual pixel data onto a brand-new image canvas and natively avoids writing any previous EXIF attributes when generating a fresh snapshot.
  - *For PDFs*: Iterates and completely copies over visual pages into a new `PdfWriter` buffer while overriding the dictionary properties with an empty set.
  - *For Videos*: Temporarily uses system storage for `ffmpeg` bindings, duplicating the core visual and audio packet streams while utilizing `-map_metadata -1` to forcefully drop all tags.
