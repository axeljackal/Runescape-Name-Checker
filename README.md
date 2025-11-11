# 🔎 RSNChecker [Version: 1.8]

**RSNChecker** is an open-source project written in Python that allows you to search for a Runescape name to see if it's available. You can search for either a single username or enter multiple usernames (I've tested 500 usernames at once) with the added benefit of either checking OSRS Hiscores or RS3 Hiscores.

## ✨ What's New in Version 1.8

- 📋 **Enhanced Progress Tracking**: Detailed per-name status with retry capability for errors
- 📝 **Run-Specific Logging**: Automatic log file creation for each run (timestamped)
- 🔄 **Smart Retry Logic**: Failed checks are retryable, successful checks are skipped
- 📊 **Better Export**: CSV/XLSX exports now include status and error columns
- 🎯 **Detailed Statistics**: Track checked, available, taken, and error counts
- 🗂️ **Improved Progress Format**: JSON with per-name metadata (status, timestamp, error details)
- 🖱️ **Drag & Drop Support**: Drag .txt files directly onto the window to load names

## 🎯 Features

- **Enhanced Progress Tracking**: Per-name status tracking (checked/error/pending) with retry capability
- **Run-Specific Logging**: Automatic timestamped log files in `logs/` directory for debugging
- **Drag & Drop Support**: Simply drag .txt files onto the window to load names instantly
- **File Loading**: Load usernames from .txt files via button or drag & drop
- **Multi-Threading**: Check multiple names simultaneously (1-10 concurrent workers)
- **Export Results**: Save results to CSV or XLSX with status and error information
- **Batch Search**: Check multiple usernames at once (tested with 500+ names)
- **Dual Platform Support**: Search both OSRS and RS3 Hiscores
- **Random Name Generator**: Generate 2-3 letter/number combinations for rare names
- **Real-time Logging**: See detailed progress, validation, and results
- **Non-blocking UI**: Responsive interface that never freezes
- **Smart Validation**: Comprehensive input validation with helpful error messages

# 🧭 Demo

![Image](/images/image.png?raw=true "Demo")

# ✍️ Manual Setup

+ Download [Python](https://www.python.org/)
- Clone repo `https://github.com/axeljackal/Runescape-Name-Checker.git`
- Install requirements `pip install -r requirements.txt`
- Run code `python3 main.py` <br />

# 📖 How to Use

## Basic Search

1. Enter names separated by commas in the input field
2. Select OSRS or RS3 Hiscores
3. Click "Check Name Availability"

## File Loading

**Option 1: Button**

1. Click "Load File" button
2. Select a .txt file with one name per line (recommended to keep in `input/` folder)
3. Names will automatically populate the input field

**Option 2: Drag & Drop** 🆕

1. Place your .txt file in the `input/` folder
2. Drag the file and drop it anywhere on the RSNChecker window
3. Names will automatically populate the input field
4. See confirmation in logs: "📂 Dropped X names from: filename.txt"

## Multi-Threading

- Use the slider to adjust concurrent workers (1-10)
- More workers = faster checking (up to API limits)
- Default: 5 workers for balanced performance

## Progress Tracking

- Progress automatically saves to `progress.json`
- If interrupted, restart the app and continue searching
- Already-checked names are automatically skipped (errors are retryable)
- Click "Clear Progress" to reset checkpoint data
- Check `logs/` directory for detailed run logs with timestamps

## Export Results

1. After checking names, click "Export Results"
2. File automatically saves to `output/rsn_results_YYYYMMDD_HHMMSS.xlsx`
3. Opens in output folder with timestamp
4. Includes NAME, AVAILABLE, STATUS, and ERROR columns

# ✏️ Generate

You can now generate (50) unique 2/3 letter /+ number RSN's to check

![Image](/images/generate.png?raw=true "Generate")

You can change how many names to generate by editing the generate functions

```python
def two_letter_func(name_entry):
    names = ["".join(random.choices(string.ascii_letters, k=2)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))
```

Where it says `for _ in range(50)` change `50` to your desired number

# ❤️ Credits

+ [aellas](https://github.com/aellas) for original RSNChecker code and concept
- [Luciano Feder](https://github.com/lucianofeder) for [RS3 API Wrapper](https://github.com/lucianofeder/runescape3-api-wrapper)
- [Chasesc](https://github.com/Chasesc) for [OSRS API Wrapper](https://github.com/Chasesc/OSRS-API-Wrapper)
