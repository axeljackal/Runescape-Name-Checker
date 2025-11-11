# Changelog

All notable changes to the Runescape Name Checker project will be documented in this file.

## [1.8.0] - 2025-11-11

### Added

- **Enhanced Progress Tracking System**: Complete redesign with detailed per-name status
  - Per-name status tracking: `checked`, `error`, or `pending`
  - Detailed metadata: availability status, source, timestamp, error messages
  - Smart retry logic: errors marked as retryable, successful checks skipped
  - Statistics tracking: total checked, available, taken, and errors
  
- **Run-Specific Logging**: Comprehensive file-based logging system
  - Automatic log file creation with timestamp: `logs/rsn_checker_YYYYMMDD_HHMMSS.log`
  - Detailed logging of all operations: checks, errors, retries, exports
  - Persistent log history for debugging and audit trails
  - Console and file output in parallel

- **Drag & Drop File Loading**: Intuitive file loading UX
  - Drag .txt files from File Explorer directly onto the application window
  - Automatic file validation (only .txt files accepted)
  - Visual feedback in logs with 📂 icon
  - Works alongside existing "Load File" button
  - Updated placeholder text: "Enter usernames or drop .txt file here"

- **Improved Progress JSON Structure**:

  ```json
  {
    "name_status": {
      "PlayerName": {
        "status": "checked|error|pending",
        "available": true|false|null,
        "source": "OSRS Hiscores|RS3 Hiscores",
        "timestamp": "ISO-8601 timestamp",
        "error": "optional error message"
      }
    },
    "last_updated": "ISO-8601 timestamp",
    "version": "1.8"
  }
  ```

- **Enhanced Export Functionality**:
  - Added `STATUS` column to exports (CHECKED/ERROR)
  - Added `ERROR` column with error messages (when applicable)
  - Better error handling with detailed logging

### Changed

- Progress tracking now distinguishes between successful checks and errors
- Errors can be retried (not marked as permanently "checked")
- Export format includes status and error information
- Skip logic only applies to successfully checked names
- Better completion summaries with breakdown of checked/available/errors

### Technical

- Added `logging` module for file-based logging
- Added `tkinterdnd2` for drag & drop functionality
- New `name_status` dictionary for detailed state tracking
- `setup_logging()` method creates per-run log files
- `on_file_drop()` method handles drag & drop events
- Enhanced `check_single_name()` with comprehensive error tracking
- Updated `load_progress()` and `save_progress()` for new JSON structure
- Backward compatible with old progress.json format
- Root window uses `TkinterDnD.Tk()` for DnD support
- Window-level drag & drop registration via `drop_target_register(DND_FILES)`

### Dependencies

- Added `tkinterdnd2` to requirements.txt for drag & drop support

## [1.7.0] - 2025-11-11

### 🚀 Major Features

#### File Loading System

- **Load names from .txt files** - Click "Load File" button to select text files
- **One name per line support** - Simple format for batch processing
- **Auto-population** - File contents automatically fill the name entry field
- **User-friendly file dialog** - Standard OS file picker for easy navigation

#### Multi-Threading Engine

- **Parallel name checking** - Uses ThreadPoolExecutor for concurrent API calls
- **Configurable workers** - Slider control for 1-10 concurrent threads
- **Optimal performance** - Default 5 workers balances speed and API limits
- **Real-time worker adjustment** - Change worker count on the fly
- **Smart thread management** - Proper cleanup and error handling per thread

#### Progress Tracking & Resume

- **Automatic checkpoints** - Saves progress to `progress.json` after each batch
- **Resume capability** - Continue interrupted searches from where you left off
- **Smart skip logic** - Already-checked names automatically excluded
- **Timestamped saves** - Track when progress was last updated
- **Clear progress option** - Red button to reset checkpoint data
- **Persistent across sessions** - Progress survives app restarts

#### Export Functionality

- **CSV export** - Save results to comma-separated values format
- **XLSX export** - Create Excel-compatible spreadsheet files
- **Organized columns** - Clean NAME and AVAILABLE columns
- **Pandas integration** - Leverages pandas DataFrame for data handling
- **Openpyxl support** - Professional Excel file generation
- **File save dialog** - Choose export location and filename

### 🎨 UI Enhancements

- **Expanded window size** - Increased from 570x395 to 700x500 for better layout
- **Load File button** - New button at position (240, 35) for file loading
- **Workers slider** - Interactive slider (1-10 range) to control concurrent threads
- **Export Results button** - Green button for easy access to export functionality
- **Clear Progress button** - Red button at (y=425) to reset progress tracking
- **Repositioned controls** - Better spacing and organization of all UI elements
- **Larger logs area** - Expanded to 485x210 for more visible output
- **Progress bar enhancement** - Increased height to 60px for better visibility

### 🔧 Technical Implementation

#### New Methods

- `load_file()` - Opens file dialog, reads .txt, populates entry field
- `load_progress()` - Loads checked names from progress.json
- `save_progress()` - Saves checked names and timestamp to JSON
- `clear_progress()` - Deletes progress file and resets tracking
- `check_single_name(name, source)` - Individual name check for thread pool, returns dict
- `update_workers(value)` - Callback for slider to adjust max_workers
- `export_results()` - Creates DataFrame and exports to CSV/XLSX

#### Modified Methods

- `search_name()` - Complete rewrite using ThreadPoolExecutor
  - Loads progress before starting
  - Skips already-checked names
  - Submits concurrent futures for parallel checking
  - Tracks progress with as_completed()
  - Saves progress after each batch
  - Proper cleanup with thread pool shutdown

#### New Imports

- `json` - For progress.json file handling
- `os, pathlib.Path` - For file operations
- `tkinter.filedialog` - For file/save dialogs
- `pandas` - For DataFrame creation and export
- `datetime` - For timestamp tracking
- `concurrent.futures.ThreadPoolExecutor, as_completed` - For multi-threading
- `queue.Queue` - For thread-safe result collection

#### New Instance Variables

- `self.max_workers = 5` - Default concurrent thread count
- `self.checked_names = set()` - Track which names already checked
- `self.results_data = []` - Store results for export
- `self.progress_file = "progress.json"` - Path to progress checkpoint file

### 📦 Dependencies

Added to requirements.txt:

- `pandas` - Data manipulation and export
- `openpyxl` - Excel file generation

Existing dependencies:

- rs3_api
- python-osrsapi
- customtkinter
- pyperclip

### 📝 Files Changed

- `main.py` - Major feature additions (7 new methods, 1 major rewrite, expanded UI)
- `requirements.txt` - Added pandas and openpyxl
- `README.md` - Updated to version 1.7 with comprehensive usage guide
- `CHANGELOG.md` - This file, updated with v1.7 changes

### 🎯 Use Cases Enabled

- **Bulk checking from files** - Load hundreds of names from organized text files
- **Interrupted workflows** - Resume long searches without starting over
- **Data analysis** - Export results to Excel for further analysis
- **Performance tuning** - Adjust worker count based on network/API performance
- **Progress monitoring** - Track which names have been checked across sessions

## [1.6] - 2025-11-11

### 🚀 Major Improvements

#### Threading & Performance

- **Replaced blocking asyncio with threading** - UI now remains responsive during searches
- **Implemented thread-safe GUI operations** - All widget updates use `root.after()` to prevent crashes
- **Fixed worker thread data access** - Input values now read on main thread before worker starts
- **Added threading.Event for stop control** - Replaced boolean flag with thread-safe Event object

#### Error Handling & Validation

- **Enhanced exception handling** - Distinguishes between "not found" (404) vs actual API/network errors
- **Improved input validation** - Now catches names with only special characters or spaces
- **Added validation logging** - Users see detailed feedback for why names fail validation
- **Better error reporting** - Network and API errors shown in logs with error messages

#### User Experience

- **Working stop button** - Can now properly interrupt searches mid-operation
- **Real-time progress updates** - Shows current name being checked
- **Comprehensive logging** - Timestamped logs for all operations
- **Search completion feedback** - Clear indication when search finishes
- **Button state management** - Search button disabled during operation to prevent multiple simultaneous searches

#### Code Quality

- **Added docstrings** - All major methods now documented
- **Consistent font usage** - Standardized on "Roboto Medium" across all UI elements
- **Proper package structure** - Added `__init__.py` to functions/ and generate/ directories
- **Removed dead code** - Eliminated unreachable code branches
- **Removed unused dependencies** - Removed aiohttp from requirements

### 🐛 Bug Fixes

- Fixed UI freezing during name searches
- Fixed race condition with stop flag (now using threading.Event)
- Fixed thread-unsafe Tkinter widget access
- Fixed missing stop_event initialization
- Fixed button not re-enabling after errors
- Fixed redundant validation checks
- Fixed unused variable (maybe_available_names)

### 🔧 Technical Changes

- Replaced `asyncio.run()` with `threading.Thread(daemon=True)`
- Changed `check_name_availability()` to return tuple for errors: `("error", message)`
- Added three thread-safe helper methods: `update_progress()`, `log_message()`, `add_result()`
- Modified `search_name()` to accept parameters instead of reading from widgets
- Updated error handling to use try-except-finally with proper cleanup

### 📦 Dependencies

- Removed: aiohttp (unused)
- Kept: rs3_api, python-osrsapi, customtkinter, pyperclip

### 📝 Files Changed

- `main.py` - Major refactoring (367 lines, fully thread-safe)
- `requirements.txt` - Removed aiohttp
- `functions/__init__.py` - Created
- `generate/__init__.py` - Created
- `README.md` - Updated to version 1.6
- `CHANGELOG.md` - Created (this file)

## [1.5] - Previous Version

- Initial tracked version
- Basic name checking functionality
- Generate random names feature
- Support for OSRS and RS3 Hiscores
- Original code by [aellas](https://github.com/aellas)
