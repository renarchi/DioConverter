import tkinter as tk
from ui import App
import logging_config  # Log konfigürasyonunu dahil ettik

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.iconbitmap("Dio.ico")  # Add your icon path here
    root.mainloop()
