import sublime
import sublime_plugin
import os
import json

fileName = "fav.sublime-settings"
fileDir = sublime.packages_path() + '\\User'
filePath = os.path.join(fileDir, fileName)

class FavMgr():
	def __init__(self, filePath):
		self.filePath = filePath
		self.favs = None
		self.keys = None
		self.load()

	def load(self):
		if os.path.exists(filePath) and os.path.isfile(filePath):
			# Vars
			keyPath = 'paths'
			# Load JSON
			with open(self.filePath) as fileData:
				fileJSON = json.load(fileData)
				if keyPath in fileJSON:
					self.favs = fileJSON[keyPath]
					self.keys = list(self.favs.keys())
		
		if self.favs == None:
			self.favs = dict()
		if self.keys == None:
			self.keys = list()
	
	def list(self):
		return self.keys;

	def get_by_index(self, index):
		key = self.keys[index]
		return self.favs[key]

	def save(self):
		return None
	
	def add(self, path):
		return None
	
	def Remove(self, path):
		return None


# ------------------------ 
# On Selected Entry - QuickPanel
# ------------------------
def On_Selected_Entry(index):
	if index < 0:
		# Ignore: either 0 or -1 (no chosen)
		return
	else:
		# Open in sublime
		path = FavMgr(filePath).get_by_index(index)
		print(path)
		Open_Folder_In_Sublime(path)
		return
	return			


# ------------------------ 
# Open folder in active window
# ------------------------
def Open_Folder_In_Sublime(path):
	win = sublime.active_window()
	project = win.project_data()
	project['folders'].append( {'path':path} ) 
	print(project)
	win.set_project_data(project)


# ------------------------ 
# Command: Open fav (folder)
# ------------------------
class OpenFavCommand(sublime_plugin.WindowCommand):
	def run(self):
		favMgr = FavMgr(filePath)
		entries = favMgr.list();

		if len(entries) < 1:
			entries.append('None')

		self.window.show_quick_panel(
			entries, # Entries
			On_Selected_Entry, # OnDone 
			sublime.MONOSPACE_FONT, # Flags
			0, # SelectedIndex
			None # OnHighlighted
			)


# ------------------------ 
# Command: Add fav (folder)
# ------------------------
class AddFavCommand(sublime_plugin.WindowCommand):
	def run(self):
		favMgr = FavMgr(filePath)
		entries = favMgr.list();

		if len(entries) < 1:
			entries.append('None')

		self.window.show_quick_panel(
			entries, # Entries
			None, # OnDone 
			sublime.MONOSPACE_FONT, # Flags
			0, # SelectedIndex
			None # OnHighlighted
			)