import string
import random

def two_letter_func(name_entry):
    """Generate 50 random two-letter names and populate the entry field."""
    names = ["".join(random.choices(string.ascii_letters, k=2)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))

def three_letter_func(name_entry):
    """Generate 50 random three-letter names and populate the entry field."""
    names = ["".join(random.choices(string.ascii_letters, k=3)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))

def two_number_func(name_entry):
    """Generate 50 random two-digit numbers and populate the entry field."""
    names = ["".join(random.choices(string.digits, k=2)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))

def three_number_func(name_entry):
    """Generate 50 random three-digit numbers and populate the entry field."""
    names = ["".join(random.choices(string.digits, k=3)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))

def two_letter_and_number_func(name_entry):
    """Generate 50 random two-character alphanumeric names and populate the entry field."""
    characters = string.ascii_letters + string.digits
    names = ["".join(random.choices(characters, k=2)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))

def three_letter_and_number_func(name_entry):
    """Generate 50 random three-character alphanumeric names and populate the entry field."""
    characters = string.ascii_letters + string.digits
    names = ["".join(random.choices(characters, k=3)) for _ in range(50)]
    name_entry.delete(0, "end")
    name_entry.insert(0, ",".join(names))
