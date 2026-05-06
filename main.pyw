import tkinter as tk  # Standard Python interface to the Tk GUI toolkit
from tkinter import scrolledtext, Menu, filedialog  # Scrollable text widget, Menu, and file dialogs from tkinter
import threading  # Support for threading (concurrent execution)
import x_create  # Custom module for creating files, folders, or objects
import x_extract  # Custom module for extracting data or files
import sys  # Provides access to system-specific parameters and functions
import os  # OS-dependent functionality (file system operations)
import subprocess  # Running new applications or processes
import time  # Time-related functions
import shutil  # High-level operations on files and directories (e.g., deletion)
from translations import get_translations  # Import the function from translations.py

# Function to find resource paths when bundled with PyInstaller
def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and PyInstaller. """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class XISOToolApp:
    # ── Palette ────────────────────────────────────────────────────────────
    BG          = "#0f1117"   # near-black background
    PANEL       = "#1a1d27"   # slightly lighter panel
    BORDER      = "#2a2d3e"   # subtle border/separator
    TEXT        = "#e0e0e0"   # primary text
    TEXT_DIM    = "#6b7280"   # muted / author line
    ACCENT      = "#107bef"   # Xbox blue — primary actions
    ACCENT_HOV  = "#1a8fff"
    GREEN       = "#22c55e"   # create/extract
    GREEN_HOV   = "#16a34a"
    RED         = "#ef4444"   # destructive
    RED_HOV     = "#dc2626"
    ORANGE      = "#f97316"   # fix ISO
    ORANGE_HOV  = "#ea6f0e"
    CONSOLE_BG  = "#080b10"
    CONSOLE_FG  = "#a3e635"   # terminal green

    def __init__(self, root):
        self.root = root
        self.root.title("X360Forge")
        self.root.geometry("640x760")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)

        self.translations = get_translations()

        try:
            icon_path = self.resource_path('Images/Icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.create_widgets()

        self.original_stdout = sys.stdout
        sys.stdout = self

        self.update_texts()

    def resource_path(self, relative_path):
        """ Return the absolute path to a resource. """
        import os
        import sys
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def update_texts(self):
        tr = self.translations["English"]
        self.root.title(tr["title"])
        self.title_label.config(text=tr["title"])
        self.author_label.config(text=tr["author"])
        self.extract_btn.config(text=tr["extract"])
        self.create_btn.config(text=tr["create"])
        self.extract_delete_btn.config(text=tr["extract_delete"])
        self.delete_source_folders_btn.config(text=tr["delete"])
        self.fix_iso_btn.config(text=tr["fix_iso"])
        self.isotogod_btn.config(text=tr["iso2god"])
        self.godtoiso_btn.config(text=tr["god2iso"])
        self.help_btn.config(text=tr["help"])

    def _btn(self, parent, text, command, bg, hover_bg, fg="#ffffff"):
        """Create a styled flat button with hover effect."""
        b = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT, bd=0, cursor="hand2",
            padx=10, pady=8
        )
        b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _separator(self, parent):
        tk.Frame(parent, bg=self.BORDER, height=1).pack(fill=tk.X, padx=16, pady=4)
    
    def create_widgets(self):
        # ── Menu bar ───────────────────────────────────────────────────────
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        self.menubar = menubar

        # ── Header ─────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=self.PANEL)
        header.pack(fill=tk.X)

        try:
            self._app_icon_img = tk.PhotoImage(file=self.resource_path('Images/Icon.png'))
            tk.Label(header, image=self._app_icon_img, bg=self.PANEL, bd=0).pack(pady=(10, 4))
        except Exception:
            pass

        self.title_label = tk.Label(
            header, text="X360Forge",
            font=("Helvetica", 22, "bold"), fg=self.ACCENT, bg=self.PANEL
        )
        self.title_label.pack(pady=(0, 0))

        self.author_label = tk.Label(
            header, text="by WB2024",
            font=("Helvetica", 9), fg=self.TEXT_DIM, bg=self.PANEL
        )
        self.author_label.pack(pady=(0, 10))

        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill=tk.X)

        # ── Button panel ───────────────────────────────────────────────────
        button_frame = tk.Frame(self.root, bg=self.BG)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # --- ISO extraction / creation group ---
        self.extract_btn = self._btn(
            button_frame, "", self.extract_xiso, self.GREEN, self.GREEN_HOV
        )
        self.extract_btn.pack(fill=tk.X, padx=16, pady=(4, 2))

        self.create_btn = self._btn(
            button_frame, "", self.create_xiso, self.ACCENT, self.ACCENT_HOV
        )
        self.create_btn.pack(fill=tk.X, padx=16, pady=2)

        self._separator(button_frame)

        # --- Destructive actions group ---
        self.extract_delete_btn = self._btn(
            button_frame, "", self.extract_delete_xiso, self.RED, self.RED_HOV
        )
        self.extract_delete_btn.pack(fill=tk.X, padx=16, pady=2)

        self.delete_source_folders_btn = self._btn(
            button_frame, "", self.delete_source_folders, self.RED, self.RED_HOV
        )
        self.delete_source_folders_btn.pack(fill=tk.X, padx=16, pady=2)

        self._separator(button_frame)

        # --- Native tool group ---
        self.fix_iso_btn = self._btn(
            button_frame, "", self.run_fix_iso, self.ORANGE, self.ORANGE_HOV
        )
        self.fix_iso_btn.pack(fill=tk.X, padx=16, pady=2)

        self.isotogod_btn = self._btn(
            button_frame, "", self.run_iso2god, self.ACCENT, self.ACCENT_HOV
        )
        self.isotogod_btn.pack(fill=tk.X, padx=16, pady=2)

        self.godtoiso_btn = self._btn(
            button_frame, "", self.run_god2iso, self.ACCENT, self.ACCENT_HOV
        )
        self.godtoiso_btn.pack(fill=tk.X, padx=16, pady=(2, 4))

        self._separator(button_frame)

        # --- Help ---
        self.help_btn = self._btn(
            button_frame, "", self.show_help, self.PANEL, self.BORDER, fg=self.TEXT_DIM
        )
        self.help_btn.pack(fill=tk.X, padx=16, pady=(2, 8))

        # ── Status console ─────────────────────────────────────────────────
        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill=tk.X)

        console_frame = tk.Frame(self.root, bg=self.CONSOLE_BG)
        console_frame.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)

        scrollbar = tk.Scrollbar(console_frame, bg=self.BORDER, troughcolor=self.BG)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_text = tk.Text(
            console_frame,
            bg=self.CONSOLE_BG, fg=self.CONSOLE_FG,
            insertbackground=self.CONSOLE_FG,
            font=("Monospace", 10),
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD,
            padx=10, pady=8,
            yscrollcommand=scrollbar.set
        )
        self.status_text.pack(expand=True, fill=tk.BOTH)
        scrollbar.config(command=self.status_text.yview)

        # Legacy help_text_area (hidden — kept for compatibility)
        self.help_text_area = tk.Text(self.root, height=0)
        self.help_text_area.pack_forget()

    def clear_status(self):
        """ Clear the status text window. """
        self.status_text.delete('1.0', tk.END)

    def create_xiso(self):
        self.clear_status()
        source_dir = filedialog.askdirectory(title="Select folder containing game folders (must contain .xex or .xbe files)")
        if not source_dir:
            self.update_status("Cancelled.")
            return
        output_dir = filedialog.askdirectory(title="Select output folder for ISO files")
        if not output_dir:
            self.update_status("Cancelled.")
            return
        self.update_status(f"Create ISOs from game folders\nSource: {source_dir}\nOutput: {output_dir}\n\nScanning for game folders...")
        threading.Thread(target=self.run_create_xiso, args=(source_dir, output_dir)).start()

    def run_create_xiso(self, source_dir, output_dir):
        x_create.create_xiso_from_directories(source_dir, output_dir)

    def extract_xiso(self):
        self.clear_status()
        iso_folder = filedialog.askdirectory(title="Select folder containing ISO files")
        if not iso_folder:
            self.update_status("Cancelled.")
            return
        output_folder = filedialog.askdirectory(title="Select output folder for extracted game folders")
        if not output_folder:
            self.update_status("Cancelled.")
            return
        self.update_status(f"Extract ISOs\nSource: {iso_folder}\nOutput: {output_folder}\n\nExtracting...")
        threading.Thread(target=self.run_extract_xiso, args=(iso_folder, output_folder, False)).start()

    def extract_delete_xiso(self):
        self.clear_status()
        iso_folder = filedialog.askdirectory(title="Select folder containing ISO files")
        if not iso_folder:
            self.update_status("Cancelled.")
            return
        output_folder = filedialog.askdirectory(title="Select output folder for extracted game folders")
        if not output_folder:
            self.update_status("Cancelled.")
            return
        self.update_status(f"Extract ISOs (delete originals)\nSource: {iso_folder}\nOutput: {output_folder}\n\nExtracting...")
        threading.Thread(target=self.run_extract_xiso, args=(iso_folder, output_folder, True)).start()

    def run_extract_xiso(self, iso_folder, output_folder, delete_after):
        x_extract.extract_xiso_from_files(iso_folder, output_folder, delete_after)

    def update_status(self, message):
        """ Update the status text window with a message. """
        # Ensure the message does not repeat if already present
        if not self.status_text.get('1.0', tk.END).strip().endswith(message.strip()):
            self.status_text.insert(tk.END, message + "\n")          
            
    def write(self, message):
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)

    def flush(self):
        pass

    def show_help(self):
        # Create a new help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Help / README")
        help_window.geometry("720x700")
        help_window.configure(bg=self.BG)

        try:
            help_window.iconbitmap(self.resource_path('Images/Icon.ico'))
        except Exception:
            pass

        text_widget = tk.Text(
            help_window,
            bg=self.CONSOLE_BG, fg=self.TEXT,
            wrap=tk.WORD, font=("Monospace", 11),
            relief=tk.FLAT, bd=0,
            padx=16, pady=12
        )
        text_widget.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)

        scrollbar_y = tk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar_y.set)

        # Insert the help text into the text widget
        content = self.translations["English"]["help_text"]

        # Insert the help text into the text widget
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

    def run_fix_iso(self):
        self.clear_status()
        iso_file = filedialog.askopenfilename(
            title="Select ISO to fix with abgx360",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        if not iso_file:
            self.update_status("Cancelled.")
            return
        self.update_status(f"Fix ISO (abgx360)\nFile: {iso_file}\n\nRunning abgx360 AutoFix (level 3) + video padding fix...\n")
        threading.Thread(target=self.execute_fix_iso, args=(iso_file,)).start()

    def execute_fix_iso(self, iso_file):
        tool = self.resource_path('x_tool/abgx360')
        try:
            proc = subprocess.Popen(
                [tool, '--af3', '-p', '-s', '-o', '--', iso_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in proc.stdout:
                self.update_status(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self.update_status("\nDone. ISO fixed successfully.")
            else:
                self.update_status(f"\nabgx360 exited with code {proc.returncode}.")
        except Exception as e:
            self.update_status(f"Failed to run abgx360: {e}")

    def run_iso2god(self):
        self.clear_status()
        iso_file = filedialog.askopenfilename(
            title="Select ISO file to convert to GOD",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        if not iso_file:
            self.update_status("Cancelled.")
            return
        output_dir = filedialog.askdirectory(title="Select output folder for GOD files")
        if not output_dir:
            self.update_status("Cancelled.")
            return
        self.update_status(f"ISO to GOD\nSource: {iso_file}\nOutput: {output_dir}\n\nConverting...")
        threading.Thread(target=self.execute_iso2god, args=(iso_file, output_dir)).start()

    def execute_iso2god(self, iso_file, output_dir):
        tool = self.resource_path('x_tool/iso2god')
        try:
            result = subprocess.run(
                [tool, iso_file, output_dir],
                capture_output=True, text=True
            )
            self.update_status(result.stdout)
            if result.returncode != 0:
                self.update_status(f"Error:\n{result.stderr}")
            else:
                self.update_status("\nDone. GOD files written to output folder.")
        except Exception as e:
            self.update_status(f"Failed to run iso2god: {e}")

    def run_god2iso(self):
        self.clear_status()
        god_file = filedialog.askopenfilename(
            title="Select GOD package file (the file without extension, not the .data folder)",
            filetypes=[("All files", "*.*")]
        )
        if not god_file:
            self.update_status("Cancelled.")
            return
        output_dir = filedialog.askdirectory(title="Select output folder for ISO")
        if not output_dir:
            self.update_status("Cancelled.")
            return
        self.update_status(f"GOD to ISO\nSource: {god_file}\nOutput: {output_dir}\n\nConverting...")
        threading.Thread(target=self.execute_god2iso, args=(god_file, output_dir)).start()

    def execute_god2iso(self, god_file, output_dir):
        tool = self.resource_path('x_tool/god2iso')
        try:
            result = subprocess.run(
                [tool, god_file, output_dir],
                capture_output=True, text=True
            )
            self.update_status(result.stdout)
            if result.returncode != 0:
                self.update_status(f"Error:\n{result.stderr}")
            else:
                self.update_status("\nDone. ISO written to output folder.")
        except Exception as e:
            self.update_status(f"Failed to run god2iso: {e}")

    def delete_source_folders(self):
        self.clear_status()
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # Get directory of the executable
        
        # Exclude specific folders
        excluded_folders = ["x_tool", "x_ISO"]
        
        # Flag to check if any folder was deleted
        deleted_any_folders = False
        
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            
            # Check if it's a directory and not in the excluded list
            if os.path.isdir(folder_path) and folder_name not in excluded_folders:
                # Check if the folder contains .xex or .xbe files
                contains_target_files = any(
                    filename.endswith(('.xex', '.xbe')) for filename in os.listdir(folder_path)
                )
                
                if contains_target_files:
                    try:
                        shutil.rmtree(folder_path)  # Remove the folder and all its contents
                        self.update_status(f"\nDELETING: \n{folder_name}\n")
                        self.update_status("DONE.")
                        deleted_any_folders = True
                    except Exception as e:
                        self.update_status(f"\nFailed to delete folder {folder_name}: {e}\n")
        
        # Check if no folders were deleted
        if not deleted_any_folders:
            self.update_status("\nNO GAME FOLDERS TO DELETE")
        else:
            self.update_status("DONE.")
    
def main():
    root = tk.Tk()
    app = XISOToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
