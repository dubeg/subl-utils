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
    FOLDERS_KEY = "folders"
    PATH_KEY = 'path'
    # --------------------------------
    def __init__(self, name, path, folders):
        self.name = name
        self.path = path
        self.folders = folders

    @classmethod
    def load(cls, path):
        name = ProjectUtils.get_name(path)
        # Load project file
        with open(path) as file:
            data = json.load(file)
        # Get folders
        folders = []
        folderEntries = data[cls.FOLDERS_KEY]
        for folderEntry in folderEntries:
            folders.append(folderEntry[cls.PATH_KEY])
        # Return
        return Project(name, path, folders)

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

    def __init__(self, window):
        self.window = window
        self.projects = ProjectUtils.get_projects()

    def prompt(self, on_prompt_done):
        promptItems = []
        for project in self.projects:
            item = [project.name]
            item.append(next(iter(project.folders), "Empty"))
            # The command show_quick_panel is bugged.
            # It is best to have two lines per item (lists of 2).
            promptItems.append(item)
        # Set empty item if needed.
        if len(promptItems) < 1:
            promptItems.append(["None", "No .sublime-project files were found in 'Users/Projects'."])
        # Prompt selection of a project.
        self.window.show_quick_panel(
            promptItems,
            on_prompt_done, # OnDone 
            sublime.MONOSPACE_FONT, # Flags
            0, # SelectedIndex
            None # OnHighlighted
            )

    def prompt_open(self):
        self.prompt(self.on_prompt_open_done)

    def prompt_remove(self):
        self.prompt(self.on_prompt_remove_done)

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
    # ----------------------
    def open_project_from_path(self, path):
        branch, leaf = os.path.split(path)
        project = Project(leaf, "", [path])
        self.open_project(project)

    def open_project(self, project):
        # Set projectData
        projectData = self.window.project_data() 
        folderEntries = []
        if projectData is None:
            projectData = dict()
        for folderPath in project.folders:
            folderEntries.append({'path': folderPath})
        projectData['folders'] = folderEntries
        self.window.set_project_data(projectData)
        self.window.active_project = project
        # Display 
        view = self.window.active_view()
        view.set_status("project_name", "Project | " + project.name)
        view.settings().set('default_dir', project.folders[0])

    def close_project(self):
        projectName = 'folders'
        if hasattr(self.window, 'active_project') and self.window.active_project != None:
            projectName = self.window.active_project.name
            self.window.active_project = None

        self.window.set_project_data(None)
        self.window.active_view().set_status("project_name", "")
        sublime.status_message("Project: {0} closed.".format(projectName))
        view = self.window.active_view()
        if view != None:
            view.settings().set('default_dir', '%USERPROFILE%')
        return None

    def new_project(self, name):
        projectData = self.window.project_data()
        path = ProjectUtils.new_project(name, projectData)
        self.window.active_project = Project.load(path)

    def save_project(self):
        project = getattr(self.window, 'active_project', None)
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
    # ----------------------
    def on_prompt_open_done(self, index):
        projects = self.projects
        if (index >= 0):
            if len(projects) > 0:
                project = projects[index]
                print("Loading project " + project.name)
                self.open_project(project)
                return
        # Entry "None" was selected, or
        # user cancelled the selection.
        # Do no more.
        return

    def on_prompt_remove_done(self, index):
        if self.projects != None and len(self.projects) > 0:
            project = self.projects[index]
            if ProjectUtils.remove_project(project.path):
                sublime.status_message("Project: {0} removed.".format(project.name))
            else:
                sublime.status_message("Project: error when removing '{0}'.".format(project.name))

    def on_prompt_create_done(self, projectName):
        self.new_project(projectName)
        sublime.status_message("Project: {0} created.".format(projectName))

# ====================================================
# Commands
# ====================================================
# Command for a SideBar directory.
# Close currently opened folders and open this one as root 
# in Sublime.
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


class ProjectOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_open()

class ProjectSaveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).save_project()

class ProjectRemoveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).prompt_remove()

class ProjectCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).close_project()
        
class ProjectInfoCommand(sublime_plugin.WindowCommand):     
    def run(self):
        print("--------- Info ----------")
        projectName = self.window.project_file_name()
        projectData = self.window.project_data()
        print(projectName)
        print(projectData)
        print("-------------------------")
