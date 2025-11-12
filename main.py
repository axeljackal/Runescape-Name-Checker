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
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import logging

class RunescapeNameChecker:
    def __init__(self):
        # Set appearance before creating window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create root with drag-and-drop support
        self.root = TkinterDnD.Tk()
        
        # Configure window background to match dark theme
        self.root.configure(bg='#2b2b2b')
        
        self.root.geometry("700x500")
        self.root.title("RSNChecker v1.8")
        self.root.resizable(False, False)
        
        # Ensure proper cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize stop flag for thread control
        self.stop_event = threading.Event()
        
        # Thread lock for shared data structures
        self.data_lock = threading.Lock()
        
        # Thread lock for executor access
        self.executor_lock = threading.Lock()
        
        # Track active executor for proper shutdown
        self.active_executor = None
        
        # Initialize progress tracking
        self.progress_file = "progress.json"
        self.checked_names: Set[str] = set()
        self.results_data = []  # Store results for export
        self.max_workers = 5  # Number of concurrent threads
        
        # New: Detailed name status tracking
        self.name_status = {}  # {name: {"status": "pending/checked/error", "available": True/False/None, "error": str, "timestamp": str}}
        
        # Setup logging
        self.setup_logging()
        
        # Load progress after GUI is created (moved to end of __init__)
        
        # ======= Search Frame =========
        
        self.search_frame = ctk.CTkFrame(self.root, width=355, height=160)
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
            placeholder_text="Enter usernames or drop .txt file here",
        )
        self.name_entry.place(x=10, y=35)
        
        # Enable drag & drop on the root window
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_file_drop)
        
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
            height=25
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
        self.workers_label.place(x=10, y=100)
        
        self.workers_slider = ctk.CTkSlider(
            self.search_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            width=100,
            command=self.update_workers,
        )
        self.workers_slider.set(5)
        self.workers_slider.place(x=75, y=103)
        
        self.workers_value_label = ctk.CTkLabel(
            self.search_frame,
            text="5",
            font=("Roboto Medium", 10),
        )
        self.workers_value_label.place(x=185, y=100)
        
        
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
        self.random_frame.place(x=10, y=180)

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
            width=355,
            height=210,
            font=("Roboto Medium", 10),
            border_color="white",
            border_width=1
        )
        self.logs_text.insert('end', f"RSNChecker v1.8\n")
        self.logs_text.insert('end', f"https://github.com/axeljackal/Runescape-Name-Checker\n")
        self.logs_text.insert('end', f"\n{functions.time.get_time()}: GUI started\n")

        self.logs_text.place(x=10, y=270)
        
        # Load progress after all widgets are created
        self.load_progress()
    
    def setup_logging(self):
        """Setup file logging for each run."""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create log file with timestamp
        log_filename = f"logs/rsn_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()  # Also print to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("RSNChecker v1.8 started")
        self.logger.info(f"Log file: {log_filename}")
        
    def check_name_availability(self, name: str, source: str):
        """Check if a name is available on the specified platform."""
        if source == "RS3 Hiscores":
            try:
                Hiscore().user(name)
                return False
            except Exception as e:
                # Name not found means it's potentially available
                error_str = str(e).lower()
                if "not found" in error_str or "404" in error_str or "unable to find" in error_str:
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
                if "not found" in error_str or "404" in error_str or "unable to find" in error_str:
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
        """Load previously checked names with detailed status."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with self.data_lock:
                        # Load detailed name status
                        self.name_status = data.get('name_status', {})
                        # For backward compatibility, build checked_names set
                        self.checked_names = {name for name, info in self.name_status.items() 
                                             if info.get('status') == 'checked'}
                    
                    if self.name_status:
                        checked_count = len(self.checked_names)
                        error_count = sum(1 for info in self.name_status.values() if info.get('status') == 'error')
                        self.log_message(f"{functions.time.get_time()}: Loaded progress - {checked_count} checked, {error_count} errors")
                        self.logger.info(f"Loaded progress: {checked_count} checked, {error_count} errors")
        except Exception as e:
            with self.data_lock:
                self.checked_names = set()
                self.name_status = {}
            self.logger.error(f"Error loading progress: {e}")
            print(f"Error loading progress: {e}")
    
    def save_progress(self):
        """Save detailed progress with name status (thread-safe)."""
        try:
            with self.data_lock:
                name_status_copy = self.name_status.copy()
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'name_status': name_status_copy,
                    'last_updated': datetime.now().isoformat(),
                    'version': '1.8'
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Progress saved: {len(name_status_copy)} names tracked")
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
            print(f"Error saving progress: {e}")
    
    def clear_progress(self):
        """Clear progress file and checked names."""
        try:
            with self.data_lock:
                self.checked_names = set()
                self.name_status = {}
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
            self.log_message(f"{functions.time.get_time()}: Progress cleared")
            self.logger.info("Progress cleared by user")
        except Exception as e:
            error_msg = f"[error] Failed to clear progress: {str(e)}"
            self.log_message(error_msg)
            self.logger.error(error_msg)
    
    def load_file(self):
        """Load usernames from a text file."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select a file with usernames",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not file_path:
                # User cancelled the dialog
                return
            
            # Validate file exists
            if not os.path.exists(file_path):
                error_msg = f"[error] File not found: {file_path}"
                self.log_message(error_msg)
                self.logger.error(error_msg)
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Replace newlines with commas
                names = content.replace('\n', ',').replace('\r', '')
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, names)
                
                # Count names
                name_count = len([n.strip() for n in names.split(',') if n.strip()])
                self.log_message(f"Loaded {name_count} names from file: {os.path.basename(file_path)}")
                self.logger.info(f"Loaded {name_count} names from file: {file_path}")
        except Exception as e:
            error_msg = f"[error] Failed to load file: {str(e)}"
            self.log_message(error_msg)
            self.logger.error(error_msg)
    
    def on_file_drop(self, event):
        """Handle drag & drop of .txt files."""
        # Get the file path from the drop event
        # The event.data may have curly braces if path has spaces
        file_path = event.data.strip('{}').strip()
        
        # Check if it's a .txt file
        if not file_path.lower().endswith('.txt'):
            self.log_message("[error] Only .txt files are supported for drag & drop")
            self.logger.warning(f"Attempted to drop non-txt file: {file_path}")
            return
        
        # Validate file exists
        if not os.path.exists(file_path):
            error_msg = f"[error] File not found: {file_path}"
            self.log_message(error_msg)
            self.logger.error(error_msg)
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Replace newlines with commas
                names = content.replace('\n', ',').replace('\r', '')
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, names)
                
                # Count names
                name_count = len([n.strip() for n in names.split(',') if n.strip()])
                self.log_message(f"📂 Dropped {name_count} names from: {os.path.basename(file_path)}")
                self.logger.info(f"Drag & drop loaded {name_count} names from: {file_path}")
        except Exception as e:
            error_msg = f"[error] Failed to load dropped file: {str(e)}"
            self.log_message(error_msg)
            self.logger.error(error_msg)
    
    def update_workers(self, value):
        """Update the number of worker threads."""
        self.max_workers = int(value)
        self.workers_value_label.configure(text=str(self.max_workers))
    
    def check_single_name(self, name: str, source: str) -> dict:
        """Check a single name with rate limiting and detailed status tracking."""
        # Check if stop was requested before starting
        if self.stop_event.is_set():
            return {
                'name': name,
                'source': source,
                'available': None,
                'error': 'Cancelled by user',
                'status': 'error'
            }
        
        # Rate limiting: 100ms delay per check
        time.sleep(0.1)
        
        # Check again after sleep in case stop was requested
        if self.stop_event.is_set():
            return {
                'name': name,
                'source': source,
                'available': None,
                'error': 'Cancelled by user',
                'status': 'error'
            }
        
        result_dict = {
            'name': name,
            'source': source,
            'available': None,
            'error': None,
            'status': 'pending'
        }
        
        try:
            result = self.check_name_availability(name, source)
            
            if result is True:
                result_dict['available'] = True
                result_dict['status'] = 'checked'
            elif result is False:
                result_dict['available'] = False
                result_dict['status'] = 'checked'
            elif isinstance(result, tuple) and result[0] == "error":
                result_dict['available'] = None  # Unknown due to error
                result_dict['error'] = result[1]
                result_dict['status'] = 'error'
            
            # Update name status
            with self.data_lock:
                self.name_status[name] = {
                    'status': result_dict['status'],
                    'available': result_dict['available'],
                    'source': source,
                    'timestamp': datetime.now().isoformat(),
                    'error': result_dict.get('error')
                }
            
            if result_dict['status'] == 'checked':
                self.logger.info(f"Checked {name} ({source}): {'Available' if result_dict['available'] else 'Taken'}")
            else:
                self.logger.error(f"Error checking {name} ({source}): {result_dict['error']}")
                
        except Exception as e:
            error_msg = str(e)
            result_dict['error'] = error_msg
            result_dict['status'] = 'error'
            
            # Mark as error (can be retried later)
            with self.data_lock:
                self.name_status[name] = {
                    'status': 'error',
                    'available': None,
                    'source': source,
                    'timestamp': datetime.now().isoformat(),
                    'error': error_msg
                }
            
            self.logger.error(f"Exception checking {name} ({source}): {error_msg}")
        
        return result_dict
    
    def export_results(self):
        """Export results to XLSX file with enhanced status tracking."""
        # Thread-safe: Create a copy of results_data
        with self.data_lock:
            if not self.results_data:
                self.log_message("[info] No results to export")
                self.logger.warning("Export attempted with no results")
                return
            results_copy = self.results_data.copy()
        
        # Create output directory if it doesn't exist
        if not os.path.exists('output'):
            os.makedirs('output')
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"output/rsn_results_{timestamp}.xlsx"
        
        try:
            # Create DataFrame from thread-safe copy
            df = pd.DataFrame(results_copy)
            
            # Add formatted columns
            df['AVAILABLE'] = df['available'].apply(lambda x: 'YES' if x else ('NO' if x is False else 'ERROR'))
            df['STATUS'] = df['status'].str.upper()
            
            # Select and reorder columns
            columns = ['name', 'AVAILABLE', 'STATUS']
            if 'error' in df.columns:
                columns.append('error')
            
            export_df = df[columns].copy()
            export_df.columns = [col.upper() for col in columns]
            
            # Auto-save to default filename
            export_df.to_excel(default_filename, index=False, engine='openpyxl')
            
            self.log_message(f"[success] Results exported to: {default_filename}")
            self.logger.info(f"Results exported to {default_filename} ({len(export_df)} rows)")
        except Exception as e:
            error_msg = f"[error] Export failed: {str(e)}"
            self.log_message(error_msg)
            self.logger.error(f"Export failed: {e}")

    def search_name(self, name_entry_text: str, source: str):
        """Main search function that runs in a separate thread with multi-threading."""
        try:
            self.stop_event.clear()
            # Clear previous results (thread-safe)
            with self.data_lock:
                self.results_data = []

            names: List[str] = name_entry_text.split(",")
            
            # Filter and validate names
            valid_names = []
            for name in names:
                stripped_name = name.strip()
                
                # Skip empty names
                if not stripped_name:
                    continue
                
                # Thread-safe check for name status
                with self.data_lock:
                    status_info = self.name_status.get(stripped_name, {})
                    status = status_info.get('status', 'pending')
                
                # Skip if already successfully checked (available or taken)
                if status == 'checked':
                    available = status_info.get('available')
                    status_text = 'Available' if available else 'Taken'
                    self.log_message(f"[skipped] {stripped_name} - already checked ({status_text})")
                    continue
                
                # Allow retries for errors
                if status == 'error':
                    self.log_message(f"[retry] {stripped_name} - retrying after previous error")
                    
                # Validate name length (RuneScape names: 1-12 characters)
                if len(stripped_name) < 1 or len(stripped_name) > 12:
                    self.log_message(f"[validation] {stripped_name} invalid length (must be 1-12 chars)")
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
            
            # Use optimal number of workers based on number of names
            # Don't use more workers than names available
            actual_workers = min(self.max_workers, total_names)
            self.log_message(f"[info] Starting check for {total_names} names with {actual_workers} workers")
            
            # Use ThreadPoolExecutor for concurrent checking
            completed = 0
            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                # Track active executor for proper shutdown (thread-safe)
                with self.executor_lock:
                    self.active_executor = executor
                
                # Submit all tasks
                future_to_name = {
                    executor.submit(self.check_single_name, name, source): name 
                    for name in valid_names
                }
                
                # Process completed tasks
                for future in as_completed(future_to_name):
                    if self.stop_event.is_set():
                        self.log_message(f"{functions.time.get_time()}: Search stopped by user")
                        self.logger.info(f"Search stopped by user at {completed}/{total_names}")
                        
                        # Cancel all pending futures
                        for f in future_to_name.keys():
                            f.cancel()
                        
                        # Force executor shutdown
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    name = future_to_name[future]
                    try:
                        result_dict = future.result()
                        
                        # Thread-safe: Add to results data
                        with self.data_lock:
                            # Only add to checked_names if successfully checked
                            if result_dict['status'] == 'checked':
                                self.checked_names.add(name)
                            self.results_data.append(result_dict)
                        
                        # Update UI based on result
                        if result_dict['status'] == 'checked':
                            if result_dict['available'] is True:
                                self.add_result(name)
                                self.log_message(f"[result] {name} not found on {source} -> potentially available")
                            elif result_dict['available'] is False:
                                self.log_message(f"[result] {name} found on {source} -> taken")
                        elif result_dict['status'] == 'error':
                            self.log_message(f"[error] {name}: {result_dict['error']}")
                        
                        completed += 1
                        self.update_progress(f"Checked {completed}/{total_names} names")
                        
                        # Save progress every 10 names or on last name for better performance
                        if completed % 10 == 0 or completed == total_names:
                            self.save_progress()
                        
                    except Exception as e:
                        self.log_message(f"[error] {name}: {str(e)}")
                        self.logger.error(f"Exception processing result for {name}: {e}")
                        completed += 1
            
            # Save final progress
            self.save_progress()
            
            # Calculate summary
            with self.data_lock:
                checked_count = sum(1 for r in self.results_data if r.get('status') == 'checked')
                error_count = sum(1 for r in self.results_data if r.get('status') == 'error')
                available_count = sum(1 for r in self.results_data if r.get('available') is True)
            
            # Search completed
            if not self.stop_event.is_set():
                summary = f"Complete: {checked_count} checked, {available_count} available, {error_count} errors"
                self.update_progress(summary)
                self.log_message(f"{functions.time.get_time()}: Search completed - {summary}")
                self.logger.info(f"Search completed: {summary}")
            
        except Exception as e:
            # Handle any unexpected errors
            self.log_message(f"[FATAL ERROR] {str(e)}")
            self.update_progress("Error occurred")
            self.logger.error(f"Fatal error in search_name: {e}")
        finally:
            # Clear active executor reference (thread-safe)
            with self.executor_lock:
                self.active_executor = None
            
            # Always re-enable buttons
            self.root.after(0, lambda: self.search_button.configure(state="normal"))
            self.root.after(0, lambda: self.export_button.configure(state="normal"))
            

    def check_name(self):
        """Start the name checking process in a separate thread."""
        # Disable search button to prevent multiple simultaneous searches
        self.search_button.configure(state="disabled")
        # Disable export button during search
        self.export_button.configure(state="disabled")
        
        # Clear results display
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
        self.logger.info("Stop requested by user")
        self.update_progress("Stopping...")
        
        # Force shutdown of active executor if it exists (thread-safe)
        with self.executor_lock:
            if self.active_executor:
                try:
                    self.active_executor.shutdown(wait=False, cancel_futures=True)
                    self.logger.info("Active executor shutdown initiated")
                except Exception as e:
                    self.logger.error(f"Error shutting down executor: {e}")
    
    def on_closing(self):
        """Handle window close event - ensure all threads are stopped."""
        self.logger.info("Application closing - stopping all operations")
        
        # Set stop event
        self.stop_event.set()
        
        # Force shutdown active executor (thread-safe)
        with self.executor_lock:
            if self.active_executor:
                try:
                    self.active_executor.shutdown(wait=False, cancel_futures=True)
                    self.logger.info("Executor shutdown on close")
                except Exception as e:
                    self.logger.error(f"Error during close: {e}")
        
        # Destroy the window
        self.root.destroy()

    def run(self):
        self.root.mainloop()

def main():
    checker = RunescapeNameChecker()
    checker.run()

if __name__ == "__main__":
    main()
