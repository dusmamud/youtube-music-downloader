import re


def sanitize_name(text: str, allow_spaces: bool = True) -> str:
    """
    Sanitizes string for filenames, removing invalid characters: / \ : * ? " < > |
    """
    cleaned = re.sub(r'[\\/*?:"<>|]', '', text)
    if not allow_spaces:
        # Replace spaces, parentheses and commas with hyphen or underscore
        cleaned = re.sub(r'[\s,()]+', '-', cleaned)
        cleaned = re.sub(r'[-_]{2,}', '-', cleaned)
    cleaned = cleaned.strip(" -_")
    return cleaned or "Unknown"


def format_filename(artist: str, title: str, quality_tag: str, ext: str, naming_style: str = "clean") -> str:
    """
    Formats filename according to user preference:
    - 'clean' (Option 1): Artist-Title-320kbps.mp3 (no spaces, hyphens only)
    - 'formal' (Option 2): Artist - Title (320kbps).mp3
    """
    safe_artist_formal = sanitize_name(artist, allow_spaces=True)
    safe_title_formal = sanitize_name(title, allow_spaces=True)
    safe_ext = ext.lstrip(".").lower()

    # Normalize quality tag
    m = re.search(r'\d+', str(quality_tag))
    if m:
        q_num = m.group(0)
        q_label_clean = f"{q_num}kbps"
        q_label_formal = f"{q_num}kbps"
    elif quality_tag:
        q_label_clean = str(quality_tag).lower().replace(" ", "").replace("(", "").replace(")", "")
        q_label_formal = str(quality_tag)
    else:
        q_label_clean = ""
        q_label_formal = ""

    if naming_style in ("clean", "1"):
        safe_artist_clean = sanitize_name(artist, allow_spaces=False)
        safe_title_clean = sanitize_name(title, allow_spaces=False)
        if q_label_clean:
            return f"{safe_artist_clean}-{safe_title_clean}-{q_label_clean}.{safe_ext}"
        return f"{safe_artist_clean}-{safe_title_clean}.{safe_ext}"
    else:
        # Formal style
        if q_label_formal:
            return f"{safe_artist_formal} - {safe_title_formal} ({q_label_formal}).{safe_ext}"
        return f"{safe_artist_formal} - {safe_title_formal}.{safe_ext}"
