# 🔒 Metadata (EXIF) Remover Project

## What is This Project?

This project removes **hidden metadata** from image files.  
Every photo taken on a phone or camera secretly stores extra information inside it — this is called **EXIF data**.

---

## 🤔 What is EXIF / Metadata?

**EXIF** stands for **Exchangeable Image File Format**.

When you take a photo, your device stores hidden information INSIDE the image file:

| Metadata Type     | What It Contains                    | Privacy Risk        |
|-------------------|-------------------------------------|---------------------|
| GPS Location      | Exact latitude & longitude          | ⚠️ HIGH - your home! |
| Date & Time       | When the photo was taken            | Medium              |
| Camera/Phone Model| Device name (e.g., iPhone 14)       | Low                 |
| Focal Length      | Camera zoom level                   | Low                 |
| ISO / Aperture    | Camera settings                     | Low                 |

---

## 📁 Project Structure

```
metadata_remover/
│
├── metadata_remover.py   ← Core logic (functions only, no GUI)
├── gui_app.py            ← Graphical User Interface (click-based)
├── requirements.txt      ← Python libraries needed
└── README.md             ← This file
```

---

## ⚙️ How to Install and Run

### Step 1: Install Python
Download from: https://www.python.org/downloads/

### Step 2: Install required library (Pillow)
Open Terminal or Command Prompt and type:
```
pip install Pillow
```

### Step 3: Run the GUI Application
```
python gui_app.py
```

### OR: Use the command-line version
```
python metadata_remover.py
```

---

## 🧠 How It Works (Simple Explanation)

```
ORIGINAL IMAGE FILE
│
├── Pixel Data     ← The actual picture (colors of each dot)
└── EXIF Metadata  ← Hidden secret notes (GPS, date, etc.)

                    ↓  OUR PROGRAM DOES THIS  ↓

STEP 1: Open original image
STEP 2: Extract ONLY the pixel data (ignore EXIF)
STEP 3: Create a brand new image with just pixel data
STEP 4: Save the new clean image

CLEAN IMAGE FILE
│
└── Pixel Data     ← Same picture, looks identical!
    (No EXIF!)     ← All secret notes deleted!
```

---

## 📖 Code Explanation

### metadata_remover.py

| Function | What It Does |
|---|---|
| `read_metadata(path)` | Opens image and returns dict of all EXIF tags |
| `remove_metadata(input, output)` | Removes all EXIF and saves clean image |
| `remove_metadata_from_folder(folder)` | Cleans all images in a folder |
| `compare_metadata(original, clean)` | Shows before/after comparison |

### gui_app.py

| Class/Method | What It Does |
|---|---|
| `MetadataRemoverApp` | Main app class (the entire GUI) |
| `__init__(root)` | Sets up window, calls `_build_ui()` |
| `_build_ui()` | Creates buttons, labels, text area |
| `browse_file()` | Opens file picker dialog |
| `view_metadata()` | Shows metadata in output area |
| `do_remove_metadata()` | Removes metadata and saves file |

---

## 🔑 Key Python Concepts Used

| Concept | Where Used | Explanation |
|---|---|---|
| `from PIL import Image` | Both files | Import Pillow library |
| `img.getdata()` | metadata_remover.py | Get raw pixel array |
| `Image.new()` | metadata_remover.py | Create blank image |
| `img.getexif()` | metadata_remover.py | Get EXIF dictionary |
| `ExifTags.TAGS` | metadata_remover.py | Convert tag numbers to names |
| `tk.Tk()` | gui_app.py | Create main window |
| `tk.Button()` | gui_app.py | Create clickable button |
| `filedialog` | gui_app.py | Open/Save file dialog |
| `StringVar` | gui_app.py | Variable linked to UI label |
| `root.mainloop()` | gui_app.py | Start GUI event loop |

---

## 🎯 Supported File Formats

- `.jpg` / `.jpeg` — Most common photo format
- `.png` — Lossless image format  
- `.bmp` — Bitmap format
- `.tiff` / `.tif` — High quality format

---

## ✅ Example Usage (Python Code)

```python
from metadata_remover import read_metadata, remove_metadata

# View metadata
data = read_metadata("my_photo.jpg")
print(data)
# Output: {'Make': 'Apple', 'Model': 'iPhone 14', 'GPSInfo': {...}}

# Remove metadata
remove_metadata("my_photo.jpg", "clean_photo.jpg")
# Creates clean_photo.jpg with all EXIF removed
```
