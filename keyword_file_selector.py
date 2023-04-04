import os
import tkinter as tk
from tkinter import filedialog, messagebox
from json_file_creator import JSONFileCreator


class KeywordFileSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select Keyword File", filetypes=(("JSON Files", "*.json"),))
        if not file_path:
            choice = messagebox.askyesno("Create Keyword File", "Keywords.json file is not present in the current directory. "
                                                                "Do you want to create a new file?")
            if not choice:
                return
            else:
                json_file_creator = JSONFileCreator()
                file_path = json_file_creator.create_file()

        return file_path
