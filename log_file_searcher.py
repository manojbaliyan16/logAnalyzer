import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from keyword_file_selector import KeywordFileSelector

class LogFileSearcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def get_log_file_path(self):
        log_file_path = filedialog.askopenfilename(title="Select Log File")
        if not log_file_path:
            messagebox.showerror("File not selected", "No log file selected")
            return
        return log_file_path

    def get_keyword_file_path(self):
        keyword_file_path = os.path.join(os.getcwd(), "keywords.json")
        if not os.path.exists(keyword_file_path):
            choice = messagebox.askyesno("Create Keyword File", "keywords.json file is not present in the current directory. "
                                                                "Do you want to create a new file?")
            if not choice:
                return
            self.create_json_file(keyword_file_path)

        return keyword_file_path

    def create_json_file(self, keyword_file_path):
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

        # Rename the created file to keywords.json
        os.rename(filename, keyword_file_path)

    def search_log_file(self, log_file_path, keyword_file_path):
        # Check if keyword file exists
        if not os.path.exists(keyword_file_path):
            # If not, ask user if they want to create a new file
            response = messagebox.askyesno("File not found", "keywords.json file is not present in the current directory. "
                                                             "Do you want to create a new file?")
            if response:
                # If yes, ask user to enter keywords and values
                keyword_dict = {}
                while True:
                    keyword = input("Enter a keyword (or 'done' to finish): ")
                    if keyword.lower() == 'done':
                        break
                    value = input("Enter the corresponding value: ")
                    keyword_dict[keyword] = value
                # Write the keywords and values to the file
                with open(keyword_file_path, 'w') as f:
                    json.dump(keyword_dict, f)
            else:
                # If no, exit the program
                messagebox.showerror("File not found", "keywords.json file is not present in the current directory")
                return

        # Open the log file and read its contents
        with open(log_file_path) as f:
            log_file = f.readlines()

        # Open the keyword file and load its contents as a dictionary
        with open(keyword_file_path) as f:
            keywords = json.load(f)

        # Search for keywords in the log file
        found_keyword = False
        for keyword, value in keywords.items():
            for line in log_file:
                if keyword in line:
                    messagebox.showinfo("Keyword found", value)
                    found_keyword = True
                    break

            if found_keyword:
                break

        # If no keywords are found, ask user if they want to add new keyword and value to the file
        if not found_keyword:
            response = messagebox.askyesno("Keyword not found", "No matching keyword found in log file. Do you want to add a new keyword and value?")
            if response:
                 # Ask user to enter a new keyword and value
                new_keyword = input("Enter a new keyword: ")
                new_value = input(f"Enter a value for '{new_keyword}': ")

                # Add the new keyword and value to the existing dictionary
                keywords[new_keyword] = new_value

                # Write the updated keywords to the file
                with open(keyword_file_path, 'w') as f:
                    json.dump(keywords, f)
                # Search the log file again for the new keyword
                self.search_log_file(log_file_path, keyword_file_path)
            else:
                 # If no, exit the program
                messagebox.showerror("Keyword not found", "No matching keyword found in log file")
            return
