import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from download import download_video, get_available_formats, delete_webm_file
from utils import format_size, log_operation
import time
import logging
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DioConverter 1.0.0")
        self.root.geometry("700x400")  # Fixed window size
        self.root.resizable(False, False)  # Prevent window resizing
        self.setup_ui()
        self.apply_mode()
    
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.output_name_label = ttk.Label(self.root, text="Output File Name:", style="TLabelframe.TLabel")
        self.output_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.output_name_entry = ttk.Entry(self.root, width=50, style="TEntryBorder.TEntry")
        self.output_name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.url_label = ttk.Label(self.root, text="Video URL:", style="TLabelframe.TLabel")
        self.url_label.grid(row=1, column=0, padx=10, pady=10)
        self.url_entry = ttk.Entry(self.root, width=50, style="TEntryBorder.TEntry")
        self.url_entry.grid(row=1, column=1, padx=10, pady=10)
        self.refresh_button = ttk.Button(self.root, text="Refresh", command=self.update_formats, style="TButtonBorder.TButton")
        self.refresh_button.grid(row=1, column=2, padx=10, pady=10)

        self.output_label = ttk.Label(self.root, text="Output Directory:", style="TLabelframe.TLabel")
        self.output_label.grid(row=2, column=0, padx=10, pady=10)
        self.output_entry = ttk.Entry(self.root, width=50, style="TEntryBorder.TEntry")
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)
        self.output_button = ttk.Button(self.root, text="Browse...", command=self.browse_output, style="TButtonBorder.TButton")
        self.output_button.grid(row=2, column=2, padx=10, pady=10)

        self.resolution_label = ttk.Label(self.root, text="Resolution:", style="TLabelframe.TLabel")
        self.resolution_label.grid(row=3, column=0, padx=10, pady=10)
        self.resolution_combobox = ttk.Combobox(self.root, values=["Select a URL first"], style="TComboboxBorder.TCombobox")
        self.resolution_combobox.grid(row=3, column=1, padx=10, pady=10)
        self.resolution_combobox.set("Select a URL first")

        self.format_label = ttk.Label(self.root, text="Format:", style="TLabelframe.TLabel")
        self.format_label.grid(row=4, column=0, padx=10, pady=10)
        self.format_combobox = ttk.Combobox(self.root, values=['mp4', 'webm', 'mkv', 'mov'], style="TComboboxBorder.TCombobox")
        self.format_combobox.grid(row=4, column=1, padx=10, pady=10)
        self.format_combobox.set('mp4')
        self.format_combobox.bind("<<ComboboxSelected>>", self.show_conversion_info)

        # Add CUDA usage checkbox
        self.use_cuda_var = tk.BooleanVar()
        self.use_cuda_checkbox = ttk.Checkbutton(self.root, text="Use CUDA", variable=self.use_cuda_var, style="Custom.TCheckbutton")
        self.use_cuda_checkbox.grid(row=5, column=0, columnspan=3, pady=10)

        self.download_button = ttk.Button(self.root, text="Download", command=self.start_download, style="TButtonBorder.TButton")
        self.download_button.grid(row=6, column=0, columnspan=3, pady=20)

        self.progress_label = ttk.Label(self.root, text="", style="TLabelframe.TLabel")
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate", style="Green.Horizontal.TProgressbar")
        self.progress.grid(row=8, column=0, columnspan=3, pady=10)

        self.url_entry.bind("<FocusOut>", self.update_formats)
        self.url_entry.bind("<KeyRelease>", self.clear_done_message)
        self.output_name_entry.bind("<KeyRelease>", self.clear_done_message)
        self.output_entry.bind("<KeyRelease>", self.clear_done_message)
        self.refresh_button.bind("<Button-1>", self.clear_done_message)

        # Tooltip for Use CUDA checkbox
        self.use_cuda_checkbox.bind("<Enter>", self.show_tooltip)
        self.use_cuda_checkbox.bind("<Leave>", self.hide_tooltip)
        self.tooltip = tk.Label(self.root, text="", background="#3e3e3e", foreground="white", relief="solid", borderwidth=1)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)

    def update_formats(self, event=None):
        self.clear_done_message()
        url = self.url_entry.get()
        if not url:
            self.resolution_combobox['values'] = ["Select a URL first"]
            self.resolution_combobox.set("Select a URL first")
            return

        formats = get_available_formats(url)
        if formats:
            format_set = set()
            resolutions = {}
            for f in formats:
                if 'format_note' in f and f.get('filesize'):
                    ext = f['ext']
                    if ext != 'm4a':
                        if ext not in format_set:
                            format_set.add(ext)
                        if f.get('height') and f['height'] >= 720:
                            filesize = f['filesize']
                            height = f['height']
                            if height not in resolutions or resolutions[height][0] > filesize:
                                resolutions[height] = (filesize, f['format_id'])

            self.format_combobox['values'] = list(format_set) + ['mkv', 'mov']

            formatted_resolutions = [f"{res}p - {format_size(resolutions[res][0])}" for res in sorted(resolutions.keys(), reverse=True)]
            self.resolution_combobox['values'] = formatted_resolutions
            if formatted_resolutions:
                self.resolution_combobox.set(formatted_resolutions[0])
            else:
                self.resolution_combobox['values'] = ["No resolutions available"]
                self.resolution_combobox.set("No resolutions available")
        else:
            self.format_combobox['values'] = ["No formats available"]
            self.format_combobox.set("No formats available")
            self.resolution_combobox['values'] = ["No resolutions available"]
            self.resolution_combobox.set("No resolutions available")

    def progress_callback(self, d):
        if d['status'] == 'downloading':
            self.progress_label.config(text="Downloading...", font=("Helvetica", 12, "bold"))
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            self.progress['value'] = (downloaded / total) * 100
            self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            if self.converting:
                self.progress_label.config(text="Converting...", font=("Helvetica", 12, "bold"))
                if delete_webm_file(self.output_path, self.output_filename):
                    self.progress_label.config(text="Done.", font=("Helvetica", 12, "bold"))
            else:
                self.progress_label.config(text="Done.", font=("Helvetica", 12, "bold"))
                self.show_success_message()
        elif 'message' in d and '[VideoConvertor] Converting video from webm to mkv' in d['message']:
            self.progress_label.config(text="Converting...", font=("Helvetica", 12, "bold"))
        elif 'message' in d and 'Deleting original file' in d['message']:
            self.progress_label.config(text="Done.", font=("Helvetica", 12, "bold"))

    def show_success_message(self):
        self.progress_label.config(text="Done.", font=("Helvetica", 12, "bold"))

    def show_conversion_info(self, event=None):
        if self.format_combobox.get() in ['mkv', 'mov']:
            messagebox.showinfo("Conversion Notice", "The video will be downloaded in .webm format and then converted to the selected format.")

    def show_tooltip(self, event):
        self.tooltip.config(text="Default conversion uses CPU.\nEnable CUDA for faster conversion using GPU.\nONLY FOR NVIDIA GPUs.")
        self.tooltip.place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty() + 20)

    def hide_tooltip(self, event):
        self.tooltip.place_forget()
    
    def start_download(self):
        self.clear_done_message()
        url = self.url_entry.get()
        output_path = self.output_entry.get()
        resolution_entry = self.resolution_combobox.get().split(' ')[0]
        resolution = resolution_entry.replace('p', '')
        formats = get_available_formats(url)
        selected_format = self.format_combobox.get()
        use_cuda = self.use_cuda_var.get()

        if selected_format in ['mkv', 'mov']:
            self.progress_label.config(text="Downloading...", font=("Helvetica", 12, "bold"))
            format_id = [f['format_id'] for f in formats if f.get('height') == int(resolution) and f['ext'] == 'webm']
            self.converting = True
        else:
            self.progress_label.config(text="Downloading...", font=("Helvetica", 12, "bold"))
            format_id = [f['format_id'] for f in formats if f.get('height') == int(resolution) and f['ext'] == selected_format]
            self.converting = False

        if not format_id:
            messagebox.showerror("Error", "Selected resolution or format is not available.")
            return

        format_id = format_id[0]
        self.output_filename = self.output_name_entry.get()

        if not url or not output_path or not resolution or not selected_format:
            messagebox.showerror("Error", "Please fill all the fields.")
            return

        self.output_filename = self.output_filename if self.output_filename else os.path.splitext(os.path.basename(url))[0]
        output_file = os.path.join(output_path, f"{self.output_filename}.{selected_format}")
        if os.path.exists(output_file):
            overwrite = messagebox.askyesno("File Exists", f"{self.output_filename}.{selected_format} already exists. Do you want to overwrite it?")
            if not overwrite:
                return

        self.success_shown = False
        self.progress['value'] = 0
        self.root.update_idletasks()

        start_time = time.time()
        operation = "conversion" if selected_format in ['mkv', 'mov'] else "download"
        try:
            self.output_path = output_path
            download_video(url, format_id, output_path, self.output_filename, selected_format, use_cuda, self.progress_callback)
            end_time = time.time()
            log_operation(start_time, end_time, "success", use_cuda=use_cuda, operation=operation, format=selected_format, resolution=resolution)
            self.progress_label.config(text="Done.", font=("Helvetica", 12, "bold"))
        except Exception as e:
            end_time = time.time()
            log_operation(start_time, end_time, "failure", error_message=str(e), use_cuda=use_cuda, operation=operation, format=selected_format, resolution=resolution)
            messagebox.showerror("Error", str(e))

    def clear_done_message(self, event=None):
        if self.progress_label.cget("text") == "Done.":
            self.progress_label.config(text="")

    def apply_mode(self):
        bg_color = "#202120"
        fg_color = "#dcdcdc"
        widget_bg = "#303030"
        entry_bg = "#404040"
        active_bg = "#3e3e3e"
        border_color = "#dcdcdc"

        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        self.style.configure("TButton", background=widget_bg, foreground=fg_color, activebackground=active_bg, activeforeground=fg_color)
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        self.style.map("TCombobox", fieldbackground=[("readonly", entry_bg)], background=[("readonly", widget_bg)])

        self.style.configure("TLabelframe.TLabel", relief="solid", bordercolor=border_color, borderwidth=1, background=bg_color, foreground=fg_color)
        self.style.configure("TEntryBorder.TEntry", relief="solid", bordercolor=border_color, borderwidth=1, fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        self.style.configure("TButtonBorder.TButton", relief="solid", bordercolor=border_color, borderwidth=1, background=widget_bg, foreground=fg_color, activebackground=active_bg, activeforeground=fg_color)
        self.style.configure("TComboboxBorder.TCombobox", relief="solid", bordercolor=border_color, borderwidth=1, fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        self.style.configure("Green.Horizontal.TProgressbar", troughcolor=widget_bg, background='green', bordercolor=border_color, relief="solid", borderwidth=1)

        self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color, activebackground=active_bg, activeforeground=fg_color)
        self.style.map("TCheckbutton", background=[("selected", widget_bg)], foreground=[("selected", fg_color)], indicatorcolor=[("selected", fg_color)])

        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Label, ttk.Entry, ttk.Button, ttk.Combobox, ttk.Progressbar, ttk.Checkbutton)):
                widget.configure(style=widget.winfo_class())

        # Add custom checkbutton style for tick
        self.style.layout('Custom.TCheckbutton',
            [('Checkbutton.padding',
              {'sticky': 'nswe', 'children':
               [('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                ('Checkbutton.label', {'side': 'left', 'sticky': ''})]})])

        self.style.map('Custom.TCheckbutton',
                       indicatorcolor=[('selected', 'green'), ('!selected', 'grey')],
                       indicatorbackground=[('selected', 'green'), ('!selected', bg_color)],
                       indicatorforeground=[('selected', 'white'), ('!selected', 'grey')],
                       indicator=[('selected', u'\u2713'), ('!selected', u'\u2718')])

        self.use_cuda_checkbox.configure(style='Custom.TCheckbutton')
