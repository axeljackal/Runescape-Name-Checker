# 🔎 RSNChecker [Version: 1.7]

**RSNChecker** is an open-source project written in Python that allows you to search for a Runescape name to see if it's available. You can search for either a single username or enter multiple usernames (I've tested 500 usernames at once) with the added benefit of either checking OSRS Hiscores or RS3 Hiscores.

## ✨ What's New in Version 1.7

- � **File Loading**: Load names from .txt files with one name per line
- ⚡ **Multi-Threading**: Parallel name checking with configurable workers (1-10)
- � **Progress Tracking**: Automatic checkpoint system - resume where you left off
- 📊 **Export Results**: Export available names to CSV or XLSX format
- 🎚️ **Worker Control**: Adjust concurrent threads with slider for optimal performance
- 🔄 **Smart Resume**: Automatically skips already-checked names
- �️ **Clear Progress**: Reset checkpoint data with one click

# 🧭 Demo

![Image](/images/image.png?raw=true "Demo")

## 🎯 Features

- **File Loading**: Load usernames from .txt files for easy batch processing
- **Multi-Threading**: Check multiple names simultaneously (1-10 concurrent workers)
- **Progress Tracking**: Automatic checkpoints - resume interrupted searches
- **Export Results**: Save available names to CSV or XLSX spreadsheets
- **Batch Search**: Check multiple usernames at once (tested with 500+ names)
- **Dual Platform Support**: Search both OSRS and RS3 Hiscores
- **Random Name Generator**: Generate 2-3 letter/number combinations for rare names
- **Real-time Logging**: See detailed progress, validation, and results
- **Non-blocking UI**: Responsive interface that never freezes
- **Smart Validation**: Comprehensive input validation with helpful error messages
- **Copy to Clipboard**: Easily copy available names with one click
- **Stop Anytime**: Interrupt long searches without waiting

# ✍️ Manual Setup
+ Download [Python](https://www.python.org/)
+ Clone repo `https://github.com/aellas/Runescape-Name-Checker.git`
+ Install requirements `pip install -r requirements.txt`
+ Run code `python3 main.py` <br />

# 📖 How to Use

## Basic Search
1. Enter names separated by commas in the input field
2. Select OSRS or RS3 Hiscores
3. Click "Check Name Availability"

## File Loading
1. Click "Load File" button
2. Select a .txt file with one name per line
3. Names will automatically populate the input field

## Multi-Threading
- Use the slider to adjust concurrent workers (1-10)
- More workers = faster checking (up to API limits)
- Default: 5 workers for balanced performance

## Progress Tracking
- Progress automatically saves to `progress.json`
- If interrupted, restart the app and continue searching
- Already-checked names are automatically skipped
- Click "Clear Progress" to reset checkpoint data

## Export Results
1. After checking names, click "Export Results"
2. Choose CSV or XLSX format
3. Select save location
4. Opens organized spreadsheet with NAME and AVAILABLE columns

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
+ [Luciano Feder](https://github.com/lucianofeder) for [RS3 API Wrapper](https://github.com/lucianofeder/runescape3-api-wrapper)
+ [Chasesc](https://github.com/Chasesc) for [OSRS API Wrapper](https://github.com/Chasesc/OSRS-API-Wrapper)
