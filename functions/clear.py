def clear_search_results(maybe_available_frame):
    """Clear all text from the results textbox."""
    maybe_available_frame.delete(1.0, "end")