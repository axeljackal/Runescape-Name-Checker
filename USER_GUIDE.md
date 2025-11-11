# RSNChecker User Guide (v1.7)

## Quick Start

### Installation
1. Download and install [Python](https://www.python.org/) (3.7 or higher)
2. Clone the repository: `git clone https://github.com/aellas/Runescape-Name-Checker.git`
3. Navigate to directory: `cd Runescape-Name-Checker`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python main.py`

---

## Features Guide

### 1. Basic Name Checking

**Manual Entry:**
- Type names separated by commas in the input field
- Example: `Player1, Player2, Player3`
- Select either OSRS or RS3 Hiscores
- Click "Check Name Availability"

**What happens:**
- Names are validated for proper format
- Each name is checked against the selected Hiscores
- Results appear in the Available Names section
- Logs show detailed progress

---

### 2. File Loading 📁

**How to use:**
1. Click the **"Load File"** button
2. Navigate to your .txt file
3. Select the file and click Open

**File format:**
- One name per line
- Plain text (.txt) files only
- Example file content:
  ```
  NameOne
  NameTwo
  NameThree
  ```

**After loading:**
- All names appear in the input field (comma-separated)
- Ready to check immediately

---

### 3. Multi-Threading ⚡

**Worker Control:**
- Use the **slider** to adjust concurrent workers (1-10)
- Default: 5 workers
- More workers = faster checking

**Performance tips:**
- Start with 5 workers (balanced)
- If experiencing timeouts, reduce workers
- If checking is fast, increase workers
- Optimal setting depends on your network speed

**How it works:**
- Multiple names checked simultaneously
- Each worker checks one name at a time
- Progress updates in real-time

---

### 4. Progress Tracking 💾

**Automatic saving:**
- Progress saves to `progress.json` after each batch
- Tracks which names have been checked
- Includes timestamp of last save

**Resume feature:**
- If you stop mid-search and restart the app
- Click "Check Name Availability" again
- Already-checked names are automatically skipped
- Only new names are checked

**Clear progress:**
- Click the **"Clear Progress"** button (red)
- Resets all tracking data
- Use before starting fresh batch

**When to clear:**
- Starting a new project
- Want to re-check old names
- Progress file corrupted

---

### 5. Export Results 📊

**How to export:**
1. After checking names, click **"Export Results"** (green button)
2. Choose format: CSV or XLSX
3. Select save location
4. Enter filename
5. Click Save

**File formats:**

**CSV (Comma-Separated Values):**
- Universal format
- Opens in Excel, Google Sheets, etc.
- Smaller file size
- Simple text-based format

**XLSX (Excel):**
- Native Excel format
- Better formatting
- Supports advanced Excel features
- Recommended for spreadsheet analysis

**Export structure:**
```
NAME          | AVAILABLE
--------------|----------
Username1     | Yes
Username2     | No
Username3     | Yes
```

**Use cases:**
- Data analysis in Excel
- Share results with others
- Archive checking sessions
- Filter available names

---

### 6. Random Name Generator ✨

**Generate random names:**
- Click "2 Letter", "3 Letter", or "2 Letter + Num"
- Generates 50 unique random names
- Automatically fills input field

**Customize generation:**
Edit the functions in `generate/random.py`:
```python
for _ in range(50)  # Change 50 to your desired number
```

**Best for:**
- Finding rare 2-3 letter names
- Testing name availability patterns
- Quick batch checking

---

## Workflow Examples

### Example 1: Quick Manual Check
```
1. Type: "DragonKing, SwordMaster, RuneKnight"
2. Select: OSRS
3. Click: "Check Name Availability"
4. View results in Available Names section
5. Click name to copy to clipboard
```

### Example 2: Large File Processing
```
1. Prepare names.txt with 200 names (one per line)
2. Click "Load File", select names.txt
3. Adjust workers slider to 8 (for faster checking)
4. Select RS3
5. Click "Check Name Availability"
6. Monitor progress in logs
7. After completion, click "Export Results"
8. Save as names_results.xlsx
9. Open in Excel for analysis
```

### Example 3: Interrupted Search Resume
```
Day 1:
1. Load file with 500 names
2. Start checking
3. After 250 names, need to stop
4. Close application (progress auto-saved)

Day 2:
1. Open application
2. Click "Load File", select same file
3. Click "Check Name Availability"
4. App automatically skips 250 already-checked names
5. Continues from name 251
6. Export final results
```

### Example 4: Multiple Sessions
```
Session 1 - Fantasy Names:
1. Load fantasy_names.txt
2. Check all names
3. Export to fantasy_results.xlsx
4. Click "Clear Progress"

Session 2 - Gaming Names:
1. Load gaming_names.txt
2. Check all names
3. Export to gaming_results.xlsx
4. Click "Clear Progress"
```

---

## Tips & Tricks

### Performance
- **Optimal workers**: Start with 5, adjust based on speed
- **Network issues**: Reduce workers to 2-3
- **Fast network**: Increase to 8-10 workers

### Organization
- **Name your files**: Use descriptive names (fantasy_names.txt, rare_2letter.txt)
- **Export regularly**: Save results after each batch
- **Clear progress**: Reset between different projects

### Best Practices
- **Validate input**: Ensure names follow RuneScape format rules
- **Monitor logs**: Watch for errors or API issues
- **Test small first**: Try 10 names before checking 1000
- **Use progress tracking**: For large batches, rely on auto-save

### Troubleshooting
- **Names not loading**: Check file format (must be .txt, one name per line)
- **Slow checking**: Reduce worker count or check network
- **Export failed**: Ensure you have write permissions to save location
- **Progress not saving**: Check if progress.json is locked/readonly

---

## Keyboard Shortcuts

- **Copy available name**: Click name in results area
- **Stop search**: Click "Stop Checking" button
- **Clear logs**: Scroll through logs textbox (auto-managed)

---

## File Locations

- **Application**: `main.py`
- **Progress tracking**: `progress.json` (auto-created)
- **Export location**: User-selected via dialog
- **Dependencies**: `requirements.txt`

---

## Common Questions

**Q: Can I check both OSRS and RS3 at once?**
A: No, select one platform per batch. For both, run two separate checks.

**Q: What's the maximum number of names I can check?**
A: No hard limit. Tested successfully with 500+ names.

**Q: Does progress tracking work across different files?**
A: Yes, it tracks all names regardless of source. Clear progress between projects.

**Q: Can I edit progress.json manually?**
A: Yes, but use "Clear Progress" button for safety.

**Q: What if a name errors during checking?**
A: It's logged, and you can retry by clearing progress and re-checking.

**Q: Export formats supported?**
A: CSV and XLSX (Excel).

---

## Support

- **Issues**: Report on [GitHub Issues](https://github.com/aellas/Runescape-Name-Checker/issues)
- **Feature requests**: Create an issue with tag "enhancement"
- **Documentation**: README.md and this guide

---

## Credits

- **Original Code**: [aellas](https://github.com/aellas) - Creator of RSNChecker
- **RS3 API**: [Luciano Feder](https://github.com/lucianofeder/runescape3-api-wrapper)
- **OSRS API**: [Chasesc](https://github.com/Chasesc/OSRS-API-Wrapper)
- **UI Framework**: CustomTkinter

---

**Version**: 1.7  
**Last Updated**: November 11, 2025  
**Author**: aellas
