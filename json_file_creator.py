import json
import tkinter as tk
from tkinter import filedialog

class JSONFileCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def create_file(self):
        filename = filedialog.asksaveasfilename(title="Create JSON File", defaultextension=".json",
                                                filetypes=(("JSON Files", "*.json"),))
        if not filename:
            return

        keywords = {}
        while True:
            keyword = input("Enter a keyword (or type 'quit' to exit): ")
            if keyword == 'quit':
                break
            value = input(f"Enter a value for '{keyword}': ")
            keywords[keyword] = value

        with open(filename, 'w') as f:
            json.dump(keywords, f, indent=4)

        return filename
