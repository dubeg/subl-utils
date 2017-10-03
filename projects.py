import sublime
import sublime_api
import sublime_plugin
import os
import json

def plugin_loaded():
    # Set default directory containing projects.
    base_dir = sublime.packages_path()
    rel_dir = "user\\projects"
    dir = os.path.join(base_dir, rel_dir)
    ProjectUtils.PROJECTS_DIR = dir
    return

# ====================================================
# Project
# ====================================================
class Project:
    KEY_FOLDERS = "folders"
    KEY_PATH = 'path'
    KEY_SETTINGS = 'settings'
    KEY_FOLDER_EXCLUDE = 'folder_exclude_patterns'
    # --------------------------------
    def __init__(self, name, path, folders, data):
        self.name = name
        self.path = path
        self.folders = folders
        self.data = data

    @classmethod
    def load(cls, path):
        name = ProjectUtils.get_name(path)
        
        # Load project file
        with open(path) as file:
            data = json.load(file)
        
        # Get folders (array of dict)
        folders = []
        folderEntries = data[cls.KEY_FOLDERS]
        for folderEntry in folderEntries:
            folders.append(folderEntry[cls.KEY_PATH])

        return Project(name, path, folders, data)

# ====================================================
# Project Management Utilities
# ====================================================
class ProjectUtils:
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
            for filename in os.listdir(project_dir):
                if filename.endswith(project_file_ext):
                    path = os.path.join(project_dir, filename)
                    try:
                        projects.append(Project.load(path))
                    except:
                        print("Project: file error " + path)
        else:
            print("Project: directory error, not found: " + project_dir)
        return projects

    @classmethod
    def save_project(cls, path, jsonData):
        with open(path, 'w') as file:
            json.dump(jsonData, file)
        return path

    @classmethod
    def new_project(cls, name, jsonData):
        path = cls.get_path(name)
        cls.save_project(path, jsonData)
        return path

    @classmethod
    def remove_project(cls, path):
        try:
            os.remove(path)
            return path
        except OSError as e:
            print( "Project file could not be delete: " + e )
            return None
    
    @classmethod
    def get_path(cls, projectName):
        filename = projectName + cls.PROJECT_FILE_EXT
        filepath = os.path.join(cls.PROJECTS_DIR, filename)
        return filepath

    @classmethod
    def get_name(cls, path):
        name = os.path.basename(path)
        name = os.path.splitext(name)[0]
        return name

# ====================================================
# Project Manager View
# ====================================================
class ProjectManager:
    SELECT_FILE_ONLY = 1
    SELECT_DIR_ONLY = 2
    SELECT_BOTH = 3

    def __init__(self, window):
        self.window = window
        self.projects = ProjectUtils.get_projects()

    # ----------------------------------------
    # Prompt: select a folder from the folders
    # opened in the sidebar.
    # ----------------------------------------
    def prompt_select_folder(self, rootFolders, selectType, on_prompt_done):
        promptItems = []

        folderCount = len(rootFolders)
        if folderCount < 1: 
            return

        # if folderCount < 2:
        rootPath = rootFolders[0]
        folders = []
        for name in os.listdir(rootPath):
            path = os.path.join(rootPath, name)
            if selectType == self.SELECT_DIR_ONLY and not os.path.isdir(path):
                continue
            if selectType == self.SELECT_FILE_ONLY and not os.path.isfile(path):
                continue
            folders.append(path)
        # else:
        # Prompt to select one of the top folders,
        # then continue as we do here.

        for path in folders:
            branch, leaf = os.path.split(path)
            item = [leaf, path]
            promptItems.append(item)
        
        if len(promptItems) < 1:
            promptItems.append(["None", "There's no opened folders."])

        self.promptItems = promptItems
        flags = sublime.MONOSPACE_FONT
        selectedIndex = 0
        onItemHighlighted = None
        self.window.show_quick_panel(
            promptItems,
            on_prompt_done,
            flags,
            selectedIndex,
            onItemHighlighted
            )

    # ----------------------------------------
    # Prompt: select a project from the list of 
    # saved projects.
    # ----------------------------------------
    def prompt_select_project(self, on_prompt_done):
        promptItems = []
        for project in self.projects:
            item = [project.name]
            item.append(next(iter(project.folders), "Empty"))
            # The command show_quick_panel is bugged.
            # It is best to have two lines per item (lists of 2).
            promptItems.append(item)
        
        if len(promptItems) < 1:
            promptItems.append(["None", "No .sublime-project files were found in 'Users/Projects'."])

        flags = sublime.MONOSPACE_FONT
        selectedIndex = 0
        onItemHighlighted = None
        self.window.show_quick_panel(
            promptItems,
            on_prompt_done,
            flags,
            selectedIndex,
            onItemHighlighted
            )

    # ----------------------------------------
    # Open a folder from a project in the list
    # of saved projects.
    # ----------------------------------------
    def prompt_open_from_project(self):
        self.prompt_select_project(self.prompt_open_from_project_select_project_done)

    def prompt_open_from_project_select_project_done(self, index):
        projects = self.projects
        if (index >= 0 
            and projects != None
            and len(projects) > 0):
            project = projects[index]
            self.prompt_select_folder(project.folders, self.SELECT_BOTH, self.prompt_open_from_project_select_folder_done)
        return

    def prompt_open_from_project_select_folder_done(self, index):
        if index >= 0:
            item = self.promptItems[index]
            path = item[1]
            if os.path.isdir(path):
                self.open_project_from_path(item[1])
            else:
                self.window.run_command("open_file", {"file": path})


    # ----------------------------------------
    # Set the root folder in the sidebar
    # by selecting an opened folder.
    # ----------------------------------------
    def prompt_root_folder(self):
        folders = self.window.folders()
        self.prompt_select_folder(folders, self.SELECT_DIR_ONLY, self.on_prompt_root_done)

    def on_prompt_root_done(self, index):
        if index >= 0:
            item = self.promptItems[index]
            self.open_project_from_path(item[1])

    # ----------------------------------------
    # Open a project by selecting one from the
    # list of saved projects.
    # ----------------------------------------
    def prompt_open(self):
        self.prompt_select_project(self.on_prompt_open_done)

    def on_prompt_open_done(self, index):
        projects = self.projects
        if (index >= 0 
            and projects != None
            and len(projects) > 0):
            project = projects[index]
            print("Loading project " + project.name)
            self.open_project(project)
            return
        # Entry "None" was selected, or
        # user cancelled the selection.
        # Do no more.
        return

    # ----------------------------------------
    # Remove a saved project by selecting one
    # from the list of saved projects.
    # ----------------------------------------
    def prompt_remove(self):
        self.prompt_select_project(self.on_prompt_remove_done)

    def on_prompt_remove_done(self, index):
        projects = self.projects
        if (index >= 0
            and projects != None 
            and len(projects) > 0):
            project = projects[index]
            if ProjectUtils.remove_project(project.path):
                sublime.status_message("Project: {0} removed.".format(project.name))
            else:
                sublime.status_message("Project: error when removing '{0}'.".format(project.name))

    # ----------------------------------------
    # Create a project including the opened folders
    # by prompting for a name.
    # ----------------------------------------
    def prompt_create(self):
        folders = self.window.folders()
        if len(folders) > 0:
            promptLabel = "Project Name"
            promptDefaultValue = os.path.basename(folders[0])
            self.window.show_input_panel(
                promptLabel, 
                promptDefaultValue,
                self.on_prompt_create_done,
                None, # on_change,
                None # on_cancel
                )
        else:
            sublime.status_message("Project: there are no folders to save.")

    def on_prompt_create_done(self, projectName):
        self.new_project(projectName)
        sublime.status_message("Project: {0} created.".format(projectName))

    # ----------------------------------------
    def open_project_from_path(self, path):
        branch, leaf = os.path.split(path)
        project = Project(leaf, "", [path])
        self.open_project(project)

    # ----------------------------------------
    def open_project(self, project):
        self.window.set_project_data(project.data)
        self.window.active_project = project

        view = self.window.active_view()
        view.settings().set('default_dir', project.folders[0])

    # ----------------------------------------
    def get_active_project(self):
        if hasattr(self.window, 'active_project') and self.window.active_project != None:
            return self.window.active_project
        return None

    # ----------------------------------------
    def close_project(self):
        project = self.get_active_project()
        projectName = 'folders'

        if project != None:
            projectName = project.name

        self.window.set_project_data(None)
        self.window.active_view().set_status("project_name", "")
        sublime.status_message("Project: {0} closed.".format(projectName))
        view = self.window.active_view()
        if view != None:
            view.settings().set('default_dir', '%USERPROFILE%')
        return None

    # ----------------------------------------
    def new_project(self, name):
        projectData = self.window.project_data()
        path = ProjectUtils.new_project(name, projectData)
        self.window.active_project = Project.load(path)

    # ----------------------------------------
    def save_project(self):
        project = self.get_active_project()
        canSave = (
            project is not None 
            and project.path is not None
            and project.path.strip() != ""
            )
        if canSave:
            projectData = self.window.project_data()
            ProjectUtils.save_project(project.path, projectData)
            sublime.status_message("Project: {0} saved.".format(project.name))
        else:
            self.prompt_create()

    # ----------------------------------------
    def open_project_file(self):
        project = self.get_active_project()
        if project != None:
            self.window.open_file(project.path)
        else:
            sublime.status_message("Project: no opened project to edit.")


# ====================================================
# Commands
# ====================================================

# ----------------------------------------
# Palette command:
# Open either a folder as root or a file from a project in the list
# of saved projects.
# ----------------------------------------
class ProjectOpenFromProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_open_from_project()

# ----------------------------------------
# SideBar directory command:
# Close currently opened folders and open selected one as root.
# ----------------------------------------
class ProjectOpenFromPathCommand(sublime_plugin.WindowCommand):
    def run(self, paths):
        if len(paths) > 0:
            path = paths[0]
            if os.path.isdir(path):
                ProjectManager(self.window).open_project_from_path(path)

    def is_enabled(self, paths):
        if len(paths) > 0:
            path = paths[0]
            if os.path.isdir(path):
                return True
        return False

# ----------------------------------------
# Palette command:
# Open as root a folder from the list of
# opened folders.
# ----------------------------------------
class ProjectRootCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_root_folder()

# ----------------------------------------
# Palette command:
# Open as root a project from the list of
# saved projects.
# ----------------------------------------
class ProjectOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_open()

# ----------------------------------------
# Palette command:
# Save the opened folders as a project.
# ----------------------------------------
class ProjectSaveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).save_project()

# ----------------------------------------
# Palette command:
# Remove a project from the list of saved
# projects.
# ----------------------------------------
class ProjectRemoveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_remove()

# ----------------------------------------
# Close the opened project and/or
# the opened folders.
# ----------------------------------------
class ProjectCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).close_project()

# ----------------------------------------
# Open to Edit .sublime-project file
# ----------------------------------------
class ProjectEditCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).open_project_file()

# ----------------------------------------
# Print to the console some information 
# related to project data.
# ----------------------------------------   
class ProjectDebugCommand(sublime_plugin.WindowCommand):     
    def run(self):
        project = ProjectManager(self.window).get_active_project()
        plugProjectName = getattr(project, "name", None)
        plugProjectPath = getattr(project, "path", None)
        winProjectName = self.window.project_file_name()
        winProjectData = self.window.project_data()
        print("==========================")
        print("~ Project Debug ~")
        print("")
        print("Window ProjectPath: " + str(winProjectName))
        print("Window ProjectData: " + str(winProjectData))
        print("")
        print("Plugin ProjectName: " + str(plugProjectName))
        print("Plugin ProjectPath: " + str(plugProjectPath))
        print("==========================")
