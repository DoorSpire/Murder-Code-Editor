import json

def readSettings():
    with open("settings/settings.json", 'r') as file:
        return json.load(file)

def writeSettings(data):
    with open("settings/settings.json", 'w') as file:
        json.dump(data, file, indent=4)

def defaultTheme():
    data = readSettings()
    return data.get("Default", {}).get("Theme")

def defaultFontSize():
    data = readSettings()
    return data.get("Default", {}).get("Font Size")

def changeDefaultTheme(new):
    data = readSettings()
    data["Default"]["Theme"] = new
    writeSettings(data)

def changeDefaultFontSize(new):
    data = readSettings()
    data["Default"]["Font Size"] = new
    writeSettings(data)