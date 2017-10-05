import sublime
import sublime_api
import sublime_plugin
import os
import json

KEY_FOLDERS = 'folders'
KEY_PATH = 'path'
KEY_SETTINGS = 'settings'
KEY_FOLDER_EXCLUDE = 'folder_exclude_patterns'
FILE_EXT = ".sublime-project"

def plugin_loaded():
    base_dir = sublime.packages_path()
    rel_dir = "user\\projects"
    dir = os.path.join(base_dir, rel_dir)
    ProjectManager.PROJECTS_DIR = dir
    return


# ====================================================
# Project
# ====================================================
class Project:
    # --------------------------------
    # Class
    # --------------------------------
    @classmethod
    def GetFoldersFromData(cls, data):
        folders = []
        blocks = data[KEY_FOLDERS]
        for block in blocks:
            path = block[KEY_PATH]
            folders.append(path)
        return folders

    @classmethod
    def GetNameFromPath(cls, path):
        filename = os.path.basename(path)
        return os.path.splitext(filename)[0]

    @classmethod
    def LoadFromPath(cls, path):
        with open(path) as file:
            data = json.load(file)
        folders = cls.GetFoldersFromData(data)
        name = 'Project Name'
        if len(folders) > 0:
            name = cls.GetNameFromPath(folders[0])
        return Project(name, path, data)

    @classmethod
    def LoadFromData(cls, data, name = None):
        folders = cls.GetFoldersFromData(data)
        if name == None or name == "":
            name = cls.GetNameFromPath(folders[0])
        return Project(name, '', data)

    @classmethod 
    def New(cls, name, folders):
        blocks = []
        for folder in folders:
            blocks.append({ KEY_PATH : folder })
        data = { KEY_FOLDERS : blocks }
        return Project(name, '', data)

    # --------------------------------
    # Constructor
    # --------------------------------
    def __init__(self, name, path, data):
        self.name = name
        self.path = path
        self.data = data

    # --------------------------------
    # Private
    # --------------------------------
    def GeneratePath(self):
        filename = self.name + FILE_EXT
        path = os.path.join(PROJECTS_DIR, filename)
        return path


    # --------------------------------
    # Public
    # --------------------------------
    def SaveOnDisk(self):
        if self.path == None or self.path == '':
            self.path = self.GeneratePath()
        with open(self.path, 'w') as file:
            json.dump(self.data, file)
        return path

    def DeleteFromDisk(self):
        try:
            os.Remove(self.path)
            return self.path
        except OSError as e:
            print( "Project file could not be delete: " + e )
            return None

    def GetFolders(self):
        return Project.GetFoldersFromData(self.data)

        

# ====================================================
# Project Manager
# ====================================================
class ProjectManager:
    SELECT_FILE_ONLY = 1
    SELECT_DIR_ONLY = 2
    SELECT_BOTH = 3
    PROJECTS_DIR = ''

    # ----------------------------------------
    # Constructor
    # ----------------------------------------
    def __init__(self, window):
        self.window = window
        self.projects = self.GetProjects()

    # ----------------------------------------
    # Get projects from directory.
    # ----------------------------------------
    def GetProjects(self):
        dir = ProjectManager.PROJECTS_DIR
        projects = list()
        if os.path.exists(dir) and os.path.isdir(dir):
            for filename in os.listdir(dir):
                if filename.endswith(FILE_EXT):
                    # try:
                        path = os.path.join(dir, filename)
                        project = Project.LoadFromPath(path)
                        projects.append(project)
                    # except:
                        # print("Project: error " + path)
        else:
            print("Project: directory not found; " + dir)
        return projects

    # ----------------------------------------
    # Select file or folder from opened folders.
    # ----------------------------------------
    def PromptSelectFileOrFolder(self, rootFolders, selectType, onPromptDone):
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
            onPromptDone,
            flags,
            selectedIndex,
            onItemHighlighted
            )

    # ----------------------------------------
    # Select project from saved projects.
    # ----------------------------------------
    def PromptSelectProject(self, onPromptDone):
        promptItems = []
        for project in self.projects:
            item = [project.name]
            item.append(next(iter(project.GetFolders()), "Empty"))
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
            onPromptDone,
            flags,
            selectedIndex,
            onItemHighlighted
            )

    # ----------------------------------------
    # Open folder from saved projects.
    # ----------------------------------------
    def PromptOpenFromProject(self):
        self.PromptSelectProject(self.PromptOpenFromProject_SelectProjectDone)

    def PromptOpenFromProject_SelectProjectDone(self, index):
        projects = self.projects
        if (index >= 0 
            and projects != None
            and len(projects) > 0):
            project = projects[index]
            self.PromptSelectFileOrFolder(project.GetFolders(), self.SELECT_BOTH, self.PromptOpenFromProject_SelectFolderDone)
        return

    def PromptOpenFromProject_SelectFolderDone(self, index):
        if index >= 0:
            item = self.promptItems[index]
            path = item[1]
            if os.path.isdir(path):
                self.OpenProjectFromPath(item[1])
            else:
                self.window.open_file(path)


    # ----------------------------------------
    # Set folder as root
    # ----------------------------------------
    def PromptScopeTo(self):
        folders = self.window.folders()
        self.PromptSelectFileOrFolder(folders, self.SELECT_DIR_ONLY, self.PromptScopeToDone)

    def PromptScopeToDone(self, index):
        if index >= 0:
            item = self.promptItems[index]
            self.OpenProjectFromPath(item[1])

    # ----------------------------------------
    # Open project from saved projects.
    # ----------------------------------------
    def PromptOpen(self):
        self.PromptSelectProject(self.PromptOpenDone)

    def PromptOpenDone(self, index):
        projects = self.projects
        if (index >= 0 
            and projects != None
            and len(projects) > 0):
            project = projects[index]
            self.OpenProject(project)
            return
        # Entry "None" was selected, or
        # user cancelled the selection.
        # Do no more.
        return

    # ----------------------------------------
    # Remove project from saved projects.
    # ----------------------------------------
    def PromptRemove(self):
        self.PromptSelectProject(self.PromptRemoveDone)

    def PromptRemoveDone(self, index):
        projects = self.projects
        if (index >= 0 and projects != None and len(projects) > 0):
            project = projects[index]
            project.DeleteFromDisk()

    # ----------------------------------------
    # Create and save project
    # ----------------------------------------
    def PromptCreate(self):
        folders = self.window.folders()
        if len(folders) > 0:
            promptLabel = "Project Name"
            promptDefaultValue = os.path.basename(folders[0])
            self.window.show_input_panel(
                promptLabel, 
                promptDefaultValue,
                self.PromptCreateDone,
                None, # on_change,
                None # on_cancel
                )
        else:
            sublime.status_message("Project: there are no folders to save.")

    def PromptCreateDone(self, projectName):
        self.NewProject(projectName)
        sublime.status_message("Project: {0} created.".format(projectName))

    # ----------------------------------------
    # Public
    # ----------------------------------------
    def OpenProjectFromPath(self, path):
        branch, leaf = os.path.split(path)
        name = leaf
        project = Project.New(name, [path])
        self.OpenProject(project)

    def OpenProject(self, project):
        self.window.set_project_data(project.data)
        self.window.active_project = project

    def OpenParentFolder(self):
        project = self.GetActiveProject()
        parentPath = ''
        if project == None:
            data = self.window.project_data()
            if data != None:
                project = Project.LoadFromData(data)
        if project != None:
            folders = project.GetFolders()
            path = folders[0]
            parentPath = os.path.dirname(path)
            self.OpenProjectFromPath(parentPath)
        return None

    def GetActiveProject(self):
        if hasattr(self.window, 'active_project') and self.window.active_project != None:
            return self.window.active_project
        return None

    def CloseProject(self):
        project = self.GetActiveProject()
        projectName = 'folders'

        if project != None:
            projectName = project.name

        self.window.set_project_data(None)
        sublime.status_message("Project: {0} closed.".format(projectName))
        return None

    def NewProject(self, name):
        projectData = self.window.project_data()
        project = Project.LoadFromData(projectData, name)
        project.SaveOnDisk()
        self.window.active_project = project

    def SaveProject(self):
        project = self.GetActiveProject()
        canSave = (
            project is not None 
            and project.path is not None
            and project.path.strip() != ""
            )
        if canSave:
            project.data = self.window.project_data()
            project.SaveOnDisk()
            sublime.status_message("Project: {0} saved.".format(project.name))
        else:
            self.PromptCreate()

    def EditProject(self):
        err = ''
        project = self.GetActiveProject()
        if project != None:
            if project.path != None and project.path.strip() != '':
                if os.path.exists(project.path):
                    self.window.open_file(project.path)
                else:
                    err = 'project''s sublime-project file was not found, ' + project.path
            else:
                err = 'project has no associated sublime-project file'
        else:
            err = 'no project opened'
        if err != '':
            sublime.status_message("Project: {0}".format(err))


# ====================================================
# Commands
# ====================================================
# ----------------------------------------
# PaletteCommand:
# Open parent folder of first opened folder
# ----------------------------------------
class ProjectOpenParentFolderAsProject(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).OpenParentFolder()

# ----------------------------------------
# PaletteCommand:
# Open folder as root or file from saved projects
# ----------------------------------------
class ProjectOpenFromProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).PromptOpenFromProject()

# ----------------------------------------
# SideBarCommand:
# Open selected as root
# ----------------------------------------
class ProjectOpenFromPathCommand(sublime_plugin.WindowCommand):
    def run(self, paths):
        if len(paths) < 1: 
            return
        path = paths[0]
        if not os.path.isdir(path):
            return
        ProjectManager(self.window).OpenProjectFromPath(path)

    def is_enabled(self, paths):
        if len(paths) > 0:
            path = paths[0]
            if os.path.isdir(path):
                return True
        return False

# ----------------------------------------
# PaletteCommand:
# Open as root a folder from opened folders
# ----------------------------------------
class ProjectScopeToCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).PromptScopeTo()

# ----------------------------------------
# PaletteCommand:
# Open as root a project from saved projects
# ----------------------------------------
class ProjectOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).PromptOpen()

# ----------------------------------------
# PaletteCommand:
# Save opened folders as project
# ----------------------------------------
class ProjectSaveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).SaveProject()

# ----------------------------------------
# PaletteCommand:
# Remove project from saved projects
# ----------------------------------------
class ProjectRemoveCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).PromptRemove()

# ----------------------------------------
# PaletteCommand:
# Close opened folders
# ----------------------------------------
class ProjectCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).CloseProject()

# ----------------------------------------
# PaletteCommand:
# Open .sublime-project of opened project
# ----------------------------------------
class ProjectEditCommand(sublime_plugin.WindowCommand):
    def run(self):
        ProjectManager(self.window).EditProject()

# ----------------------------------------
# Print information for debugging
# ----------------------------------------   
class ProjectDebugCommand(sublime_plugin.WindowCommand):     
    def run(self):
        project = ProjectManager(self.window).GetActiveProject()
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
