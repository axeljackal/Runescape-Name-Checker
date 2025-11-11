import pyperclip

def copy_maybe_available(maybe_available_frame, copy_button):
    """Copy available names to clipboard with error handling."""
    try:
        text = maybe_available_frame.get("1.0", "end-1c")
        if not text.strip():
            copy_button.configure(text="Nothing to copy")
            copy_button.after(2000, lambda: copy_button.configure(text="Copy to Clipboard"))
            return
        
        pyperclip.copy(text)
        copy_button.configure(text="Copied!")
        copy_button.after(2000, lambda: copy_button.configure(text="Copy to Clipboard"))
    except Exception as e:
        copy_button.configure(text="Copy failed!")
        copy_button.after(2000, lambda: copy_button.configure(text="Copy to Clipboard"))
        print(f"Error copying to clipboard: {e}")

