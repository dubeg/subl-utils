import sublime
import sublime_plugin
import os
import json

PROJECTS_REL_DIR = '\\User\\Projects'

# ====================================================
# Project
# ====================================================
class Project:
	FOLDERS_KEY = "folders"
	PATH_KEY = 'path'
	# --------------------------------
	def __init__(self, name, path):
		self.name = name
		self.path = path
		self.folders = set()
		self.load()
	# --------------------------------
	# Exceptions:
	# File does not exists
	# Invalid JSON 
	# JSON does not contain 'folders' lists
	def load(self):
		# 1. Load JSON file 
		with open(self.path) as file:
			data = json.load(file)
		
		# 2. Load folders from JSON
		folderEntries = data[self.FOLDERS_KEY]
		for folderEntry in folderEntries:
			if self.PATH_KEY in folderEntry:
				self.folders.add(folderEntry[self.PATH_KEY])
		return None
	# --------------------------------



# ====================================================
# Project Manager
# ====================================================
class ProjectMgr():
	# Static
	# --------------------------------
	PROJECT_FILE_EXT = ".sublime-project"
	# --------------------------------
	@classmethod 
	def get_projects(cls, project_dir):
		projects = list()
		if os.path.exists(project_dir) and os.path.isdir(project_dir):
			# Load names of project-files.
			for filename in os.listdir(project_dir):
				if filename.endswith(cls.PROJECT_FILE_EXT):
					projectName = os.path.splitext(filename)[0]
					path = os.path.join(project_dir, filename)
					try:
						projects.append(Project(projectName, path))
					except:
						print("Project: file error " + path)
		else:
			print("Project: directory error, not found: " + project_dir)
		return projects
	# --------------------------------
	@classmethod
	def save_project(cls, name, jsonData):
		path = os.path.join(cls.PROJECTS_DIR, name + cls.PROJECT_FILE_EXT)
		
		with open(path, 'w') as file:
			json.dump(jsonData, file)

		return None



# ====================================================
# Command: Close Project
# ====================================================
class ProjectCloseCommand(sublime_plugin.WindowCommand):
	# --------------------------------
	def run(self):
		self.window.run_command("close_project")   # Close folders
		self.window.run_command("close_workspace") # Close workspace (file history, actions history, etc.)
		# self.window.run_command("close_all")	   # Close files
		return


# ====================================================
# Command: Open Project
# ====================================================
class ProjectOpenCommand(sublime_plugin.WindowCommand):
	# --------------------------------
	def run(self):
		# Init these properties 
		# only once.
		try:
			self.entries.clear()
		except:
			self.entries = []

		project_dir = sublime.packages_path() + PROJECTS_REL_DIR

		# Load entries (project names).
		self.projects = ProjectMgr.get_projects(project_dir)
		self._load_entries(self.entries, self.projects)

		# Prompt project selection.
		self.window.show_quick_panel(
			self.entries, # Entries
			self._on_entry_selected, # OnDone 
			sublime.MONOSPACE_FONT, # Flags
			0, # SelectedIndex
			None # OnHighlighted
			)
		return None
	# --------------------------------
	def _load_entries(self, entries, projects):
		for project in projects:
			self.entries.append([project.name, str(len(project.folders)) + " folders"])

		if len(self.entries) < 1:
			self.entries.append(["None", "No .sublime-project files were found in 'Users/Projects'."])
		return None
	# --------------------------------
	def _on_entry_selected(self, index):
		if(index >= 0):
			entry = self.entries[index]
			if entry[0] != "None":
				print("Loading project " + entry[0])
				project = self.projects[index]
				self._load_project(project)
				return

		# Entry "None" was selected, or
		# user cancelled the selection.
		# Do no more.
		return
	# --------------------------------
	def _load_project(self, project):
		# projectData: {}, dict()
		# folderEntries: [], list()
		projectData = self.window.project_data() 
		folderEntries = []

		if projectData is None:
			projectData = dict()

		for folderPath in project.folders:
			folderEntries.append({'path': folderPath})

		# 2. Set projectData of window
		projectData['folders'] = folderEntries
		self.window.set_project_data(projectData)
		self.window.project_name = project.name
		self.window.active_view().set_status("project_name", "Project | " + project.name)
		return None


# ====================================================
# Command: Save Project
# ====================================================
class ProjectSaveCommand(sublime_plugin.WindowCommand):
	# --------------------------------
	def run(self, save_as = False):
		name = None
		try:
			name = self.window.project_name
		except AttributeError:
			pass
		
		if name != None and save_as == False:
			self.save(name)
		else:
			self.window.show_input_panel(
				"Enter Name of Project", # caption
				"", # initial_text
				self._on_done, # on_done(str)
				None,# on_change(str)
				None# on_cancel(str)
			)
	# --------------------------------
	def _on_done(self, name):
		if name != "":
			self.save(name)
		else:
			print("No name of project entered.")
	# --------------------------------
	def save(self, name):
		project_data = self.window.project_data()
		ProjectMgr.save_project(name, project_data)
	# --------------------------------



# ====================================================
# Command: Print Sublime Project Info
# ====================================================
class ProjectInfoCommand(sublime_plugin.WindowCommand):		
	def run(self):
		print("--------- Info ----------")
		projectName = self.window.project_file_name()
		projectData = self.window.project_data()
		print(projectName)
		print(projectData)
		print("--------- End  ----------")
