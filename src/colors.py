import re
from tkinter import END

colors = {
    'if': 'red',
    'while': 'red',
    'for': 'red',
    'else': 'red',
    'this': 'orange',
    'super': 'orange',
    'true': 'blue',
    'false': 'blue',
    'null': 'blue',
    'def': 'purple',
    'and': 'purple',
    'or': 'purple',
    'class': 'purple',
    'int': 'purple',
    'return': 'purple',
    ';': 'grey',
    '{': 'grey',
    '}': 'grey',
    '(': 'grey',
    ')': 'grey',
    ',': 'grey',
    '.': 'grey',
    '-': 'grey',
    '+': 'grey',
    '/': 'grey',
    '*': 'grey',
    '!': 'grey',
    '=': 'grey',
    '>': 'grey',
    '<': 'grey',
    '0': 'green',
    '1': 'green',
    '2': 'green',
    '3': 'green',
    '4': 'green',
    '5': 'green',
    '6': 'green',
    '7': 'green',
    '8': 'green',
    '9': 'green'
}

class Tokenizer:
    def __init__(self, textWidget):
        self.textWidget = textWidget

    def detectWords(self):
        textContent = self.textWidget.get("1.0", END)
        self.textWidget.tag_add("default", "1.0", END)
        self.textWidget.tag_config("default", foreground="yellow")

        pattern = r'(\".*?\"|\'.*?\')|\b(' + '|'.join(re.escape(word) for word in colors.keys()) + r')\b|[(){};,.!\-+/*<>]'

        for match in re.finditer(pattern, textContent):
            word = match.group(0)
            startIndex = f"1.0 + {match.start()}c"
            endIndex = f"1.0 + {match.end()}c"

            if word.startswith('"') or word.startswith("'"):
                self.textWidget.tag_add("string", startIndex, endIndex)
                self.textWidget.tag_config("string", foreground="lime green")
            else:
                color = colors.get(word, "yellow")
                self.textWidget.tag_add(word, startIndex, endIndex)
                self.textWidget.tag_config(word, foreground=color)

    def reload(self):
        self.clearAllTags()
        self.detectWords()

    def clearAllTags(self):
        self.textWidget.tag_remove("default", "1.0", END)
        self.textWidget.tag_add("default", "1.0", END)
        self.textWidget.tag_config("default", foreground="yellow")

        for word in colors.keys():
            self.textWidget.tag_remove(word, "1.0", END)
        
        self.textWidget.tag_remove("string", "1.0", END)