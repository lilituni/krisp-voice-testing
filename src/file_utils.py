"""Small file read/write helpers shared across test cases."""

def read_text_file(path: str) -> str:
    """Read the contents of a text file and return it as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_text_file(path: str, text: str) -> None:
    """Write the given text to a file at the specified path."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)