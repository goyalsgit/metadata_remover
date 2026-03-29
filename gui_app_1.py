import tkinter as tk
from tkinter import filedialog, messagebox
import os
from metadata_remover import read_metadata, remove_metadata

class MetadataRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metadata Remover")
        self.root.geometry("600x500")
        self.root.configure(bg="#2d2d2d")
        
        self.selected_file_path = None
        self._build_ui()

    def _build_ui(self):
        # Header
        tk.Label(self.root, text="Metadata Remover", font=("Arial", 18, "bold"), bg="#2d2d2d", fg="white").pack(pady=15)

        # File Selection
        self.file_label = tk.Label(self.root, text="No file selected", bg="#2d2d2d", fg="#aaaaaa", font=("Arial", 10))
        self.file_label.pack(pady=5)
        
        tk.Button(self.root, text="Browse Image or PDF", command=self.browse_file, width=20).pack(pady=5)

        # Action Buttons
        btn_frame = tk.Frame(self.root, bg="#2d2d2d")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="View Metadata", command=self.view_metadata, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Remove & Save", command=self.remove_metadata, width=15).pack(side=tk.LEFT, padx=10)

        # Output Log Box
        self.log_box = tk.Text(self.root, height=15, width=65, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_box.pack(pady=10)
        self.log("App initialized. Select an image or PDF to begin.")

    def log(self, message):
        """Append text to the console log box."""
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media files", "*.jpg *.png *.jpeg *.tiff *.pdf *.mp4 *.mov *.avi *.mkv")])
        if file_path:
            self.selected_file_path = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.log(f"Loaded file: {file_path}")

    def view_metadata(self):
        if not self.selected_file_path:
            messagebox.showwarning("Error", "Please select a file first.")
            return

        self.log("\n--- Metadata ---")
        metadata = read_metadata(self.selected_file_path)
        
        if metadata:
            for key, value in metadata.items():
                self.log(f"{key}: {value}")
        else:
            self.log("No metadata found.")

    def remove_metadata(self):
        if not self.selected_file_path:
            messagebox.showwarning("Error", "Please select a file first.")
            return

        default_name = f"clean_{os.path.basename(self.selected_file_path)}"
        extension = os.path.splitext(self.selected_file_path)[1].lower()
        save_path = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=extension)
        
        if save_path:
            self.log("\nRemoving metadata...")
            success = remove_metadata(self.selected_file_path, save_path)
            
            if success:
                self.log(f"SUCCESS: Clean file saved at {save_path}")
                messagebox.showinfo("Success", "Metadata removed successfully!")
            else:
                self.log("ERROR: Failed to remove metadata.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataRemoverApp(root)
    root.mainloop()
