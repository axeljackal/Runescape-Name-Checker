# Progress Tracking System v1.8

## Overview

RSNChecker v1.8 introduces a comprehensive progress tracking system that maintains detailed status information for each name checked. This replaces the simple "checked/not-checked" system with a robust state-based tracking mechanism.

## Key Features

### 1. Per-Name Status Tracking

Each name has a detailed status record with the following information:

- **status**: Current state (`checked`, `error`, or `pending`)
- **available**: Availability result (`true`, `false`, or `null`)
- **source**: Which API was used (`OSRS Hiscores` or `RS3 Hiscores`)
- **timestamp**: ISO-8601 formatted timestamp of last check
- **error**: Error message if check failed (optional)

### 2. Smart Skip/Retry Logic

- ✅ **Successfully checked names** (status: `checked`) are automatically skipped
- 🔄 **Error names** (status: `error`) can be retried on subsequent runs
- ⏭️ **Pending names** (status: `pending`) will be processed normally

This ensures you never waste API calls on names already verified, while allowing you to retry temporary errors.

### 3. Run-Specific Logging

Every time you run RSNChecker, a new log file is created in the `logs/` directory:

```text
logs/rsn_checker_20251111_185210.log
logs/rsn_checker_20251111_192345.log
logs/rsn_checker_20251111_203001.log
```

Each log contains:

- Startup information
- Every name check (success or failure)
- Error details with full stack traces
- Export operations
- Progress save operations
- Summary statistics

### 4. Enhanced Export

CSV/XLSX exports now include:

| Column | Description |
|--------|-------------|
| NAME | The username checked |
| AVAILABLE | YES, NO, or ERROR |
| STATUS | CHECKED or ERROR |
| ERROR | Error message (if applicable) |

## JSON Structure

### New Progress Format (v1.8)

```json
{
  "name_status": {
    "PlayerName1": {
      "status": "checked",
      "available": false,
      "source": "OSRS Hiscores",
      "timestamp": "2025-11-11T18:52:10.123456",
      "error": null
    },
    "PlayerName2": {
      "status": "checked",
      "available": true,
      "source": "RS3 Hiscores",
      "timestamp": "2025-11-11T18:52:11.234567",
      "error": null
    },
    "PlayerName3": {
      "status": "error",
      "available": null,
      "source": "OSRS Hiscores",
      "timestamp": "2025-11-11T18:52:12.345678",
      "error": "Connection timeout after 10 seconds"
    }
  },
  "last_updated": "2025-11-11T18:52:12.345678",
  "version": "1.8"
}
```

### Old Progress Format (v1.7 - still supported)

```json
{
  "checked_names": ["PlayerName1", "PlayerName2", "PlayerName3"],
  "last_updated": "2025-11-11T18:52:10.123456"
}
```

The system is **backward compatible** - it can load old v1.7 progress files and will upgrade them to the new format on save.

## Usage Scenarios

### Scenario 1: Retry Failed Checks

You run a check with poor internet connection. Some names fail with errors:

**First run:**

```text
[result] Player1 not found on OSRS -> potentially available
[error] Player2: Connection timeout
[result] Player3 found on OSRS -> taken
[error] Player4: API rate limit exceeded
```

**Second run:**
The system automatically:

- ✅ Skips `Player1` (already successfully checked as available)
- 🔄 Retries `Player2` (marked as error)
- ✅ Skips `Player3` (already successfully checked as taken)
- 🔄 Retries `Player4` (marked as error)

### Scenario 2: Debugging Issues

Something went wrong? Check the log files:

```text
logs/rsn_checker_20251111_185210.log
```

Contains detailed information:

```text
2025-11-11 18:52:10,123 - INFO - RSNChecker v1.8 started
2025-11-11 18:52:10,234 - INFO - Loaded progress: 150 checked, 5 errors
2025-11-11 18:52:15,456 - INFO - Checked PlayerName (OSRS Hiscores): Available
2025-11-11 18:52:16,567 - ERROR - Error checking AnotherPlayer (OSRS Hiscores): Connection timeout
2025-11-11 18:52:30,890 - INFO - Search completed: 145 checked, 12 available, 5 errors
2025-11-11 18:52:35,012 - INFO - Results exported to results.xlsx (150 rows)
```

### Scenario 3: Analyzing Results

Export to Excel and filter by STATUS column:

- **Filter STATUS = "CHECKED"**: See all successfully verified names
- **Filter STATUS = "ERROR"**: See all failed checks that need retry
- **Filter AVAILABLE = "YES"**: See all available names
- **Sort by ERROR**: Group errors by type

## Implementation Details

### Thread Safety

All status updates are protected by `threading.Lock`:

```python
with self.data_lock:
    self.name_status[name] = {
        'status': 'checked',
        'available': True,
        # ...
    }
```

### Progress Save Optimization

Progress is saved:

- Every 10 names checked (reduces I/O operations)
- After the final name in a batch
- When search is stopped by user

### Error Handling

Three levels of error tracking:

1. **API errors** (from rs3_api/osrs_api): Marked as `error` status
2. **Exception errors** (network, timeout): Marked as `error` status
3. **Fatal errors** (system issues): Logged but don't corrupt progress

### Backward Compatibility

Loading old progress files:

```python
# Old format
data = {
    'checked_names': ['Player1', 'Player2']
}

# Automatically converted to:
self.name_status = {
    'Player1': {'status': 'checked', ...},
    'Player2': {'status': 'checked', ...}
}
```

## Migration Guide

### From v1.7 to v1.8

**No action needed!** Your existing `progress.json` will be:

1. ✅ Loaded automatically
2. ✅ Converted to new format
3. ✅ Saved in new format on next progress save

### Manual Migration (optional)

If you want to manually convert old format:

```python
# Old: List of names
checked_names = ["Player1", "Player2", "Player3"]

# New: Detailed status dict
name_status = {
    "Player1": {
        "status": "checked",
        "available": None,  # Unknown from old format
        "source": "Unknown",
        "timestamp": datetime.now().isoformat(),
        "error": None
    },
    # ... repeat for each name
}
```

## Best Practices

### 1. Regular Log Review

Check `logs/` directory periodically:

- Identify patterns in errors
- Monitor API performance
- Debug connectivity issues

### 2. Clear Old Logs

Log files can accumulate. Clean up old logs:

```powershell
# Keep only last 30 days of logs
Get-ChildItem logs/*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

### 3. Backup Progress

Before major runs, backup your progress:

```powershell
Copy-Item progress.json progress_backup.json
```

### 4. Export Regularly

Export results after each major batch:

- Provides backup of your data
- Allows external analysis in Excel
- Creates audit trail

## Troubleshooting

### Issue: Progress not saving

**Check:**

- ✅ Write permissions in directory
- ✅ Disk space available
- ✅ Check logs for errors

### Issue: All names being rechecked

**Possible causes:**

- progress.json was deleted
- File permissions changed
- Status was "error" (retry is intentional)

**Solution:**

- Check if `progress.json` exists
- Verify file contains `name_status` dict
- Review status values in JSON

### Issue: Too many errors

**Investigate:**

- Check log files for error patterns
- Verify internet connection
- Check API rate limiting
- Review error messages in export

## Future Enhancements

Potential improvements for future versions:

- 📊 **Statistics Dashboard**: Visual breakdown of checked/available/errors
- 🕒 **Retry Scheduler**: Automatic retry of errors after delay
- 📈 **Performance Metrics**: API response times, success rates
- 💾 **Database Backend**: SQLite for large-scale operations
- 🔔 **Notifications**: Alert when available names found
- 🌐 **Cloud Sync**: Sync progress across devices

## Credits

Enhanced progress tracking system developed for RSNChecker v1.8

Original RSNChecker by [aellas](https://github.com/aellas)
