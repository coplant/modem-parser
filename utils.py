def remove_whitespace(text):
    text = text.replace("\n", "")
    text = " ".join(text.split())
    return text
