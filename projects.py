import sublime
import sublime_plugin
import os
import json



# ====================================================
# Called when the API is ready to use.
# ====================================================
def plugin_loaded():
	# Default dir
	base_dir = sublime.packages_path()
	rel_dir = "user\\projects"
	dir = os.path.join(base_dir, rel_dir)
	# ---
	ProjectMgr.PROJECTS_DIR = dir

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
		self.folders = list()
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
			self.folders.append(folderEntry[self.PATH_KEY])
		

		return None
	# --------------------------------



# ====================================================
# Project Manager
# ====================================================
class ProjectMgr:
	# Static
	# --------------------------------
	PROJECTS_DIR = None
	PROJECT_FILE_EXT = ".sublime-project"
	# --------------------------------
	@classmethod 
	def get_projects(cls):
		project_dir = cls.PROJECTS_DIR
		project_file_ext = cls.PROJECT_FILE_EXT
		projects = list()

		if os.path.exists(project_dir) and os.path.isdir(project_dir):
			# Load names of project-files.
			for filename in os.listdir(project_dir):
				if filename.endswith(project_file_ext):
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
	def _get_path_from_name(cls, name):
		project_dir = cls.PROJECTS_DIR
		project_file_ext = cls.PROJECT_FILE_EXT
		return os.path.join(project_dir, name + project_file_ext)
		
	# --------------------------------
	@classmethod
	def save_project(cls, name, jsonData):
		path = cls._get_path_from_name(name)
		with open(path, 'w') as file:
			json.dump(jsonData, file)

		return None
	# --------------------------------
	@classmethod
	def remove_project(cls, name):
		path = cls._get_path_from_name(name)
		try:
			os.remove(path)
			return True
		except OSError as e:
			print( "Project file could not be delete: " + e )
			return False


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

		# Load entries (project names).
		self.projects = ProjectMgr.get_projects()
		self._load_entries(self.entries, self.projects)

		# Prompt project selection.
		self.window.show_quick_panel(
			self.entries, # Entries
			self._on_select_prompt_done, # OnDone 
			sublime.MONOSPACE_FONT, # Flags
			0, # SelectedIndex
			None # OnHighlighted
			)
		return None
	# --------------------------------
	def _load_entries(self, entries, projects):
		for project in projects:
			projectEntries = [project.name]
			projectEntries.append(next(iter(project.folders), "Empty"))
			# The following doesn't work since show_quick_panel contains a bug which 
			# make lists with different lengths to throw up an "index out of range" error.
			# projectEntries.extend(project.folders)
			self.entries.append(projectEntries)

		if len(self.entries) < 1:
			self.entries.append(["None", "No .sublime-project files were found in 'Users/Projects'."])
		return None
	# --------------------------------
	def _on_select_prompt_done(self, index):
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
		if name == None or name == "":
			sublime.status_message("Project: nothing opened.")
		elif save_as == False:
			self.save(name)
		else:
			self.window.show_input_panel(
				"Enter name of Project", # caption
				"", # initial_text
				self._on_saveas_prompt_done, # on_done(str)
				None,# on_change(str)
				None# on_cancel(str)
			)
	# --------------------------------
	def _on_saveas_prompt_done(self, input):
		if input != None and input != "":
			name = input
			self.save(name)
			self.window.project_name = name
			self.window.active_view().set_status("project_name", "Project | {0}".format(name))
		else:
			sublime.status_message("Project: not saved; empty name.")
	# --------------------------------
	def save(self, name):
		if name != None and name != "":
			project_data = self.window.project_data()
			ProjectMgr.save_project(name, project_data)
			sublime.status_message("Project: saved ({0}).".format(name))
		else:
			sublime.status_message("Project: not saved; empty name.")
	# --------------------------------


# ====================================================
# Command: Remove Project
# ====================================================
class ProjectRemoveCommand(sublime_plugin.WindowCommand):
	def run(self):
		# Init these properties 
		# only once.
		try:
			self.entries.clear()
		except:
			self.entries = []

		# Load entries (project names).
		self.projects = ProjectMgr.get_projects()
		self._load_entries(self.entries, self.projects)

		# Prompt project selection.
		self.window.show_quick_panel(
			self.entries, # Entries
			self._on_select_prompt_done, # OnDone 
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
	def _on_select_prompt_done(self, index):
		if(index >= 0):
			entry = self.entries[index]
			project_name = entry[0]
			if project_name != "None":
				if ProjectMgr.remove_project(project_name):
					sublime.status_message("Project: {0} was successfully removed.".format(project_name))
				else:
					sublime.status_message("Project: error when trying to remove '{0}'.".format(project_name))

		# Entry "None" was selected, or
		# user cancelled the selection.
		# Do no more.
		return

# ====================================================
# Command: Close Project/Folders
# ====================================================
class ProjectCloseCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.set_project_data(None)
		self.window.project_name = ""
		self.window.active_view().set_status("project_name", "")
		return None
		


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
		print("-------------------------")
