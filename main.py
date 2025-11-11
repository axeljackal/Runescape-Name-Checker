from rs3_api.hiscores import Hiscore
from osrs_api import Hiscores
from typing import List, Set
import customtkinter as ctk
import threading
import functions.clear
import functions.copy
import functions.time
import generate.random
import json
import os
from pathlib import Path
from tkinter import filedialog
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class RunescapeNameChecker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("700x500")
        self.root.title("RSNChecker v1.7")
        self.root.resizable(False, False)
        
        # Initialize stop flag for thread control
        self.stop_event = threading.Event()
        
        # Thread lock for shared data structures
        self.data_lock = threading.Lock()
        
        # Initialize progress tracking
        self.progress_file = "progress.json"
        self.checked_names: Set[str] = set()
        self.results_data = []  # Store results for export
        self.max_workers = 5  # Number of concurrent threads
        
        # Load progress after GUI is created (moved to end of __init__)
        
        # ======= Search Frame =========
        
        self.search_frame = ctk.CTkFrame(self.root, width=355, height=110)
        self.search_frame.place(x=10, y=10)
        
        # Search Label
        self.search_label = ctk.CTkLabel(
            self.search_frame,
            text="Search",
            font=("Roboto Medium", 14, "bold"),
        )
        self.search_label.place(x=10, y=3)
        
        # Search entry
        self.name_entry = ctk.CTkEntry(
            self.search_frame,
            width=220,
            font=("Roboto Medium", 12),
            placeholder_text="Enter usernames or load file",
        )
        self.name_entry.place(x=10, y=35)
        
        # Load file button
        self.load_file_button = ctk.CTkButton(
            self.search_frame,
            text="Load File",
            command=self.load_file,
            font=("Roboto Medium", 10),
            text_color="white",
            width=80,
            height=25,
        )
        self.load_file_button.place(x=240, y=35)
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Check",
            command=self.check_name,
            font=("Roboto Medium", 12),
            text_color="white",
            width=80,
            height=30,
            
        )
        self.search_button.place(x=240, y=65)
        
        # Stop button
        self.stop_button = ctk.CTkButton(
            self.search_frame,
            text="Stop",
            command=self.stop_search,
            font=("Roboto Medium", 12),
            text_color="white",
            width=80,
            height=30,
            
        )
        self.stop_button.place(x=240, y=100)
        
        # Progress bar
        self.progress_bar = ctk.CTkFrame(
            self.search_frame,
            width=220,
            height=60
        )
        self.progress_bar.place(x=10, y=70)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_bar,
            text="",
            font=("Roboto Medium", 10),
            text_color="white",
        )
        self.progress_label.place(x=5, y=0)
        
        # Workers control
        self.workers_label = ctk.CTkLabel(
            self.search_frame,
            text="Workers:",
            font=("Roboto Medium", 10),
        )
        self.workers_label.place(x=10, y=140)
        
        self.workers_slider = ctk.CTkSlider(
            self.search_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            width=100,
            command=self.update_workers,
        )
        self.workers_slider.set(5)
        self.workers_slider.place(x=75, y=143)
        
        self.workers_value_label = ctk.CTkLabel(
            self.search_frame,
            text="5",
            font=("Roboto Medium", 10),
        )
        self.workers_value_label.place(x=185, y=140)
        
        
        # ========= Source (Right) Frame =========
        
        self.source_frame = ctk.CTkFrame(self.root, width=177, height=110)
        self.source_frame.place(x=380, y=10)
        
        self.configure_label = ctk.CTkLabel(
            self.source_frame,
            text="Search Options",
            font=("Roboto Medium", 14, "bold"),
        )
        self.configure_label.place(x=32, y=18)
        
        # Source Selection
        self.selection_var = ctk.StringVar(value="OSRS Hiscores")
        self.selection_options = ["OSRS Hiscores", "RS3 Hiscores"]
        self.source_selection = ctk.CTkOptionMenu(
            self.source_frame,
            values = self.selection_options,
            variable= self.selection_var,
            font=("Roboto Medium", 12),
        )
        self.source_selection.place(x=18, y=55)
        
        # ========= Guide (Left) Frame =========
        
        self.guide_textbox = ctk.CTkTextbox(
            self.root,
            width=178,
            height=181,
            border_color="white",
            border_width=1,
            font=("Roboto Medium", 12),
        )
        self.guide_textbox.place(x=380, y=130)
                
        self.copy_button = ctk.CTkButton(
            self.root,
            text="Copy to Clipboard",
            text_color="white",
            command=lambda: functions.copy.copy_maybe_available(
                self.guide_textbox, self.copy_button
            ),
            font=("Roboto Medium", 12),
            width=178,
            fg_color="#2F8C56",
        )     
        self.copy_button.place(x=380, y=320)
        
        self.clear_button = ctk.CTkButton(
            self.root,
            text="Clear Results",
            text_color="white",
            command=lambda: functions.clear.clear_search_results(self.guide_textbox),
            width=178
        )
        self.clear_button.place(x=380, y=355)
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.root,
            text="Export Results",
            text_color="white",
            command=self.export_results,
            width=178,
            fg_color="#2E7D32",
        )
        self.export_button.place(x=380, y=390)
        
        # Clear progress button
        self.clear_progress_button = ctk.CTkButton(
            self.root,
            text="Clear Progress",
            text_color="white",
            command=self.clear_progress,
            width=178,
            fg_color="#D32F2F",
        )
        self.clear_progress_button.place(x=380, y=425)

        self.random_frame = ctk.CTkFrame(self.root, width=355, height=90)
        self.random_frame.place(x=10, y=170)

        self.two_letter = ctk.CTkButton(
            self.random_frame,
            text="Two Letters",
            command=lambda: generate.random.two_letter_func(self.name_entry),
            font=("Roboto Medium", 12),
            text_color="white",
            width=90,
        )
        self.two_letter.place(x=10, y=10)

        self.three_letter = ctk.CTkButton(
            self.random_frame,
            text="Three Letters",
            command=lambda: generate.random.three_letter_func(self.name_entry),
            font=("Roboto Medium", 12),
            text_color="white",
            width=90,
        )
        self.three_letter.place(x=10, y=50)

        self.two_letter_numbers = ctk.CTkButton(
            self.random_frame,
            text="(Two) L + N",
            command=lambda: generate.random.two_letter_and_number_func(self.name_entry),
            font=("Roboto Medium", 12),
            text_color="white",
            width=100,
        )
        self.two_letter_numbers.place(x=240, y=10)

        self.three_letter_numbers = ctk.CTkButton(
            self.random_frame,
            text="(Three) L + N",
            command=lambda: generate.random.three_letter_and_number_func(
                self.name_entry
            ),
            font=("Roboto Medium", 12),
            text_color="white",
            width=100,
        )
        self.three_letter_numbers.place(x=240, y=50)

        self.placeholder_button = ctk.CTkButton(
            self.random_frame,
            text="Two Numbers",
            command=lambda: generate.random.two_number_func(self.name_entry),
            font=("Roboto Medium", 12),
            text_color="white",
            width=105,
        )
        self.placeholder_button.place(x=117, y=10)

        self.placeholder2_button = ctk.CTkButton(
            self.random_frame,
            text="Three Numbers",
            command=lambda: generate.random.three_number_func(self.name_entry),
            font=("Roboto Medium", 12),
            text_color="white",
            width=105,
        )
        self.placeholder2_button.place(x=117, y=50)
        
        # Logs text
        self.logs_text = ctk.CTkTextbox(
            self.root,
            width=485,
            height=210,
            font=("Roboto Medium", 10),
            border_color="white",
            border_width=1
        )
        self.logs_text.insert('end', f"RSNChecker v1.7\n")
        self.logs_text.insert('end', f"https://github.com/Aellas/RSNChecker\n")
        self.logs_text.insert('end', f"\n{functions.time.get_time()}: GUI started\n")

        self.logs_text.place(x=10, y=270)
        
        # Load progress after all widgets are created
        self.load_progress()
        
    def check_name_availability(self, name: str, source: str):
        """Check if a name is available on the specified platform."""
        if source == "RS3 Hiscores":
            try:
                Hiscore().user(name)
                return False
            except Exception as e:
                # Name not found means it's potentially available
                # Log actual errors for debugging
                error_str = str(e).lower()
                if "not found" in error_str or "404" in error_str:
                    return True
                else:
                    # Network or API error - return error message
                    return ("error", str(e)[:50])
        elif source == "OSRS Hiscores":
            try:
                Hiscores(username=name)
                return False
            except Exception as e:
                error_str = str(e).lower()
                if "not found" in error_str or "404" in error_str:
                    return True
                else:
                    return ("error", str(e)[:50])

    def update_progress(self, text):
        """Thread-safe progress label update."""
        self.root.after(0, lambda: self.progress_label.configure(text=text))
    
    def log_message(self, message):
        """Thread-safe log insertion with line limit."""
        def _insert():
            self.logs_text.insert("end", message + "\n")
            # Keep only last 1000 lines to prevent memory growth
            lines = int(self.logs_text.index('end-1c').split('.')[0])
            if lines > 1000:
                self.logs_text.delete('1.0', f'{lines-1000}.0')
        self.root.after(0, _insert)
    
    def add_result(self, name):
        """Thread-safe result addition."""
        self.root.after(0, lambda: self.guide_textbox.insert("end", name + "\n"))
    
    def load_progress(self):
        """Load previously checked names from progress file."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    with self.data_lock:
                        self.checked_names = set(data.get('checked_names', []))
                    if self.checked_names:
                        self.log_message(f"{functions.time.get_time()}: Loaded {len(self.checked_names)} previously checked names")
        except Exception as e:
            with self.data_lock:
                self.checked_names = set()
            print(f"Error loading progress: {e}")
    
    def save_progress(self):
        """Save checked names to progress file (thread-safe)."""
        try:
            with self.data_lock:
                checked_names_copy = list(self.checked_names)
            
            with open(self.progress_file, 'w') as f:
                json.dump({
                    'checked_names': checked_names_copy,
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def clear_progress(self):
        """Clear progress file and checked names."""
        with self.data_lock:
            self.checked_names = set()
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        self.log_message(f"{functions.time.get_time()}: Progress cleared")
    
    def load_file(self):
        """Load usernames from a text file."""
        file_path = filedialog.askopenfilename(
            title="Select a file with usernames",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace newlines with commas
                    names = content.replace('\n', ',').replace('\r', '')
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, names)
                    
                    # Count names
                    name_count = len([n.strip() for n in names.split(',') if n.strip()])
                    self.log_message(f"Loaded {name_count} names from file: {os.path.basename(file_path)}")
            except Exception as e:
                self.log_message(f"[error] Failed to load file: {str(e)}")
    
    def update_workers(self, value):
        """Update the number of worker threads."""
        self.max_workers = int(value)
        self.workers_value_label.configure(text=str(self.max_workers))
    
    def check_single_name(self, name: str, source: str) -> dict:
        """Check a single name and return result as dict."""
        result = self.check_name_availability(name, source)
        
        result_dict = {
            'name': name,
            'source': source,
            'available': None,
            'error': None
        }
        
        if result is True:
            result_dict['available'] = True
        elif result is False:
            result_dict['available'] = False
        elif isinstance(result, tuple) and result[0] == "error":
            result_dict['available'] = False
            result_dict['error'] = result[1]
        
        # Small delay to avoid API rate limiting
        time.sleep(0.1)
        
        return result_dict
    
    def export_results(self):
        """Export results to CSV or XLSX file."""
        if not self.results_data:
            self.log_message("[info] No results to export")
            return
        
        # Ask user for file type and location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            title="Save results as"
        )
        
        if file_path:
            try:
                # Create DataFrame
                df = pd.DataFrame(self.results_data)
                df['AVAILABLE'] = df['available'].apply(lambda x: 'YES' if x else 'NO')
                
                # Select and reorder columns
                export_df = df[['name', 'AVAILABLE']].copy()
                export_df.columns = ['NAME', 'AVAILABLE']
                
                # Export based on file extension
                if file_path.endswith('.csv'):
                    export_df.to_csv(file_path, index=False)
                else:
                    export_df.to_excel(file_path, index=False, engine='openpyxl')
                
                self.log_message(f"[success] Results exported to: {os.path.basename(file_path)}")
            except Exception as e:
                self.log_message(f"[error] Export failed: {str(e)}")

    def search_name(self, name_entry_text: str, source: str):
        """Main search function that runs in a separate thread with multi-threading."""
        try:
            self.stop_event.clear()
            self.results_data = []  # Clear previous results

            names: List[str] = name_entry_text.split(",")
            
            # Filter and validate names
            valid_names = []
            for name in names:
                stripped_name = name.strip()
                
                # Skip empty names
                if not stripped_name:
                    continue
                
                # Thread-safe check for already checked names
                with self.data_lock:
                    already_checked = stripped_name in self.checked_names
                
                if already_checked:
                    self.log_message(f"[skipped] {stripped_name} - already checked")
                    continue
                    
                # Validate name length
                if len(stripped_name) > 12:
                    self.log_message(f"[validation] {stripped_name} is too long (>12 chars)")
                    continue
                    
                # Validate characters
                if not all(
                    char.isalnum() or char.isspace() or char == "_" or char == "-"
                    for char in stripped_name
                ):
                    self.log_message(f"[validation] {stripped_name} has invalid characters")
                    continue
                    
                # Check if name is only special characters or spaces
                if all(char in "_- " for char in stripped_name):
                    self.log_message(f"[validation] {stripped_name} is only special characters or spaces")
                    continue
                
                valid_names.append(stripped_name)
            
            if not valid_names:
                self.log_message("[info] No valid names to check")
                self.update_progress("No valid names")
                self.root.after(0, lambda: self.search_button.configure(state="normal"))
                self.root.after(0, lambda: self.export_button.configure(state="normal"))
                return
            
            total_names = len(valid_names)
            self.log_message(f"[info] Starting check for {total_names} names with {self.max_workers} workers")
            
            # Use ThreadPoolExecutor for concurrent checking
            completed = 0
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_name = {
                    executor.submit(self.check_single_name, name, source): name 
                    for name in valid_names
                }
                
                # Process completed tasks
                for future in as_completed(future_to_name):
                    if self.stop_event.is_set():
                        self.log_message(f"{functions.time.get_time()}: Search stopped by user")
                        break
                    
                    name = future_to_name[future]
                    try:
                        result_dict = future.result()
                        
                        # Thread-safe: Add to checked names and save progress
                        with self.data_lock:
                            self.checked_names.add(name)
                            self.results_data.append(result_dict)
                        
                        # Update UI
                        if result_dict['available'] is True:
                            self.add_result(name)
                            self.log_message(f"[result] {name} not found on {source} -> potentially available")
                        elif result_dict['available'] is False:
                            if result_dict['error']:
                                self.log_message(f"[error] {name}: {result_dict['error']}")
                            else:
                                self.log_message(f"[result] {name} found on {source} -> taken")
                        
                        completed += 1
                        self.update_progress(f"Checked {completed}/{total_names} names")
                        
                        # Save progress every 10 names or on last name for better performance
                        if completed % 10 == 0 or completed == total_names:
                            self.save_progress()
                        
                    except Exception as e:
                        self.log_message(f"[error] {name}: {str(e)}")
                        completed += 1
            
            # Save final progress
            self.save_progress()
            
            # Search completed
            if not self.stop_event.is_set():
                self.update_progress(f"Complete: {completed}/{total_names}")
                self.log_message(f"{functions.time.get_time()}: Search completed - {completed} names checked")
            
        except Exception as e:
            # Handle any unexpected errors
            self.log_message(f"[FATAL ERROR] {str(e)}")
            self.update_progress("Error occurred")
        finally:
            # Always re-enable buttons
            self.root.after(0, lambda: self.search_button.configure(state="normal"))
            self.root.after(0, lambda: self.export_button.configure(state="normal"))
            

    def check_name(self):
        """Start the name checking process in a separate thread."""
        # Disable search button to prevent multiple simultaneous searches
        self.search_button.configure(state="disabled")
        # Disable export button during search
        self.export_button.configure(state="disabled")
        
        # Clear previous results
        self.guide_textbox.delete(1.0, "end")
        
        # Read input values BEFORE starting thread (thread-safe)
        name_entry_text = self.name_entry.get().strip()
        source = self.selection_var.get()
        
        # Run search in separate thread to keep UI responsive
        search_thread = threading.Thread(
            target=self.search_name, 
            args=(name_entry_text, source),
            daemon=True
        )
        search_thread.start()        

    def stop_search(self):
        """Stop the current search operation."""
        self.stop_event.set()
        self.log_message(f"{functions.time.get_time()}: Stop requested by user")
        self.update_progress("Stopping...")

    def run(self):
        self.root.mainloop()

def main():
    checker = RunescapeNameChecker()
    checker.run()

if __name__ == "__main__":
    main()
