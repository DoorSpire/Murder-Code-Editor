import colors
import defaults

import os
import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
from PIL import ImageTk
from fontTools.ttLib import TTFont

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Murder Code")
        self.root.state("zoomed")

        self.textFontSize = 14
        self.customFontPath = "font/codenamecoderfree4f-bold.otf"

        self.fontFamily = self.loadCustomFont(self.customFontPath)
        self.textFont = font.Font(family=self.fontFamily, size=self.textFontSize)

        icon = ImageTk.PhotoImage(file='icon/MCode.png')
        self.root.wm_iconphoto(True, icon)

        tabSize = self.measureTabSize("    ")

        self.leftFrame = tk.Frame(self.root)
        self.leftFrame.pack(side='left', fill='y')

        self.style = ttk.Style()
        self.fileExplorer = ttk.Treeview(self.leftFrame)
        self.fileExplorer.pack(side='left', fill='y')
        self.fileExplorer.bind("<<TreeviewSelect>>", self.onFileSelect)

        self.scrollbar = ttk.Scrollbar(self.leftFrame, orient="vertical", command=self.fileExplorer.yview)
        self.fileExplorer.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        self.textFrame = tk.Frame(self.root)
        self.textFrame.pack(side='right', expand=True, fill='both')

        self.textArea = tk.Text(self.root, wrap='word', font=self.textFont, insertbackground="yellow", tabs=(tabSize,))
        self.textArea.pack(expand=True, fill='both', side='right')

        self.textArea.bind("<KeyRelease>", self.onKeyRelease)
        self.textArea.bind("<MouseWheel>", self.onKeyRelease)

        self.tokenizer = colors.Tokenizer(self.textArea)
        
        self.currentFilePath = None

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.fileMenu = tk.Menu(self.menu, tearoff=0)
        self.modeMenu = tk.Menu(self.menu, tearoff=0)
        self.fontMenu = tk.Menu(self.menu, tearoff=0)

        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.menu.add_cascade(label="Mode", menu=self.modeMenu)
        self.menu.add_cascade(label="Font", menu=self.fontMenu)

        self.fileMenu.add_command(label="New", command=self.newFile)
        self.fileMenu.add_command(label="Open Folder", command=self.openFolder)
        self.fileMenu.add_command(label="Save", command=self.saveFile)
        self.fileMenu.add_command(label="Save As", command=self.saveAsFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.exitApp)

        self.modeMenu.add_command(label="Dark", command=self.darkMode)
        self.modeMenu.add_command(label="Dark Contrast", command=self.darkContrastMode)
        self.modeMenu.add_command(label="Light", command=self.lightMode)
        self.modeMenu.add_command(label="Light Contrast", command=self.lightContrastMode)

        self.fontMenu.add_command(label="Small (14)", command=lambda: self.changeFontSize(14))
        self.fontMenu.add_command(label="Medium (21)", command=lambda: self.changeFontSize(21))
        self.fontMenu.add_command(label="Large (35)", command=lambda: self.changeFontSize(35))
        self.fontMenu.add_command(label="Extra Large (49)", command=lambda: self.changeFontSize(49))

        self.changeFontSize(defaults.defaultFontSize())
        
        if defaults.defaultTheme() == "Dark":
            self.darkMode()
        elif defaults.defaultTheme() == "Dark Contrast":
            self.darkContrastMode()
        elif defaults.defaultTheme() == "Light":
            self.lightMode()
        elif defaults.defaultTheme() == "Light Contrast":
            self.lightContrastMode()
        else:
            self.darkMode()

        self.tokenizer.detectWords()

    def loadCustomFont(self, fontPath):
        font = TTFont(fontPath)
        familyName = font['name'].getName(1, 3, 1, 1033).toUnicode()
        return familyName

    def measureTabSize(self, text):
        dummyLabel = tk.Label(self.root, text=text, font=self.textFont)
        dummyLabel.pack()
        width = dummyLabel.winfo_reqwidth()
        dummyLabel.destroy()
        return width

    def onKeyRelease(self, event=None):
        self.tokenizer.reload()

    def newFile(self):
        self.textArea.delete(1.0, tk.END)
        self.currentFilePath = None
        self.textArea.focus_set()

    def openFolder(self, folderPath=None):
        if not folderPath:
            folderPath = filedialog.askdirectory()
        if folderPath:
            self.populateFileExplorer(folderPath)

    def populateFileExplorer(self, folderPath):
        self.fileExplorer.delete(*self.fileExplorer.get_children())

        for rootDir, dirs, files in os.walk(folderPath):
            rootNode = self.fileExplorer.insert('', 'end', text=os.path.basename(rootDir), open=True)
            self.processDir(rootDir, dirs, files, rootNode)
            break

    def processDir(self, rootDir, dirs, files, parentNode):
        for directory in dirs:
            dirPath = os.path.join(rootDir, directory)
            dirNode = self.fileExplorer.insert(parentNode, 'end', text=directory, open=False)
            self.populateSubTree(dirPath, dirNode)

        for file in files:
            filePath = os.path.join(rootDir, file)
            self.fileExplorer.insert(parentNode, 'end', text=file, open=False, tags=(filePath,))

    def populateSubTree(self, directoryPath, parentNode):
        try:
            subDirs = next(os.walk(directoryPath))[1]
            subFiles = next(os.walk(directoryPath))[2]
            
            for subDir in subDirs:
                subDirPath = os.path.join(directoryPath, subDir)
                subDirNode = self.fileExplorer.insert(parentNode, 'end', text=subDir, open=False)
                self.populateSubTree(subDirPath, subDirNode)

            for subFile in subFiles:
                subFilePath = os.path.join(directoryPath, subFile)
                self.fileExplorer.insert(parentNode, 'end', text=subFile, open=False, tags=(subFilePath,))

        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {e}")

    def onFileSelect(self, event):
        selectedItem = self.fileExplorer.selection()[0]
        filePath = self.fileExplorer.item(selectedItem, "tags")
        if filePath:
            self.openFile(filePath[0])

    def openFile(self, filePath):
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    content = file.read()
                    self.textArea.delete(1.0, tk.END)
                    self.textArea.insert(tk.END, content)
                    self.currentFilePath = filePath
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        self.tokenizer.detectWords()

    def saveFile(self):
        if self.currentFilePath:
            try:
                with open(self.currentFilePath, 'w') as file:
                    content = self.textArea.get(1.0, tk.END)
                    file.write(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.saveAsFile()

    def saveAsFile(self):
        filePath = filedialog.asksaveasfilename(defaultextension=".npp", filetypes=[("N++ Source Files", "*.npp")])
        if filePath:
            try:
                with open(filePath, 'w') as file:
                    content = self.textArea.get(1.0, tk.END)
                    file.write(content)
                    self.currentFilePath = filePath
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def exitApp(self):
        self.root.quit()

    def changeFontSize(self, size):
        defaults.changeDefaultFontSize(size)
        self.textFontSize = size
        self.textFont.config(size=self.textFontSize)

    def changeTheme(self, bgColor, fgColor, name):
        self.textArea.config(bg=bgColor, fg=fgColor)
        self.root.config(bg=bgColor)
        self.leftFrame.config(bg=bgColor)
        self.textFrame.config(bg=bgColor)
        self.style.configure('Treeview', background=bgColor, fieldbackground=bgColor, foreground=fgColor, bordercolor=bgColor)
        self.style.configure('Treeview.Heading', background=bgColor, foreground=fgColor)
        self.style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe', 'children': [('Treeitem.padding', {'children': [('Treeitem.text', {'sticky': 'nswe'})]})]})])
        self.style.map('Treeview', background=[('selected', '#0078d7')], foreground=[('selected', 'white')])
        self.style.configure("Vertical.TScrollbar", background=bgColor, troughcolor=bgColor)
        self.menu.config(bg=bgColor, fg=fgColor)
        self.fileMenu.config(bg=bgColor, fg=fgColor)
        self.fontMenu.config(bg=bgColor, fg=fgColor)
        self.modeMenu.config(bg=bgColor, fg=fgColor)
        defaults.changeDefaultTheme(name)

    def darkMode(self):
        self.changeTheme("#222222", "white", "Dark")

    def darkContrastMode(self):
        self.changeTheme("black", "white", "Dark Contrast")

    def lightMode(self):
        self.changeTheme("#f0f0f0", "black", "Light")

    def lightContrastMode(self):
        self.changeTheme("white", "black", "Light Contrast")