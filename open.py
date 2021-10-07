import sublime
import sublime_plugin
import os
import sys
import subprocess

# --------------------------------
# Open path in FileManager
# --------------------------------
class OpenInFileManager(sublime_plugin.WindowCommand):
    def run(self, path):  
        variables = self.window.extract_variables()
        path = sublime.expand_variables(path, variables)
        path = path.replace('/', '\\')

        platLinux = 'linux2' # linux2/3
        platMacOSX = 'darwin'
        platWindows = 'win32'

        cmdWin = 'explorer'
        optWinSelect = '/select,'
        
        cmdOSX = 'open'
        optOSX = ''

        cmdLinux = 'xdg-open'
        optLinux = ''

        cmd = None
        opts = None

        if sys.platform == platWindows:
            cmd = cmdWin
            opts = [ optWinSelect ]
        elif sys.platform == platMacOSX:
            cmd = cmdOSX
            opts = [ optOSX ]
        elif sys.platform.startswith( platLinux ):
            cmd = cmdLinux
            opts = [ optLinux ]    
        
        if os.path.isdir(path):
            subprocess.Popen([cmd, path])
        else:
            subprocess.Popen([cmd, opts, path])
        
        # Just as reminder
        # ~~~~~~~~~~~~~~~~    
        # subprocess.check_call(['gnome-open', '--', path])
        # self.window.run_command("open_dir",{"dir": os.path.dirname(path)})
        # os.startfile(path)

# --------------------------------
# Add folder to current window.
# --------------------------------
class AddFolderCommand(sublime_plugin.WindowCommand):
    def run(self, path):
        variables = self.window.extract_variables()
        path = sublime.expand_variables(path, variables)
        path = os.path.expandvars(path)
        path = path.replace('/', '\\')

        project = self.window.project_data()
        if project is None:
            project = { 'folders' : [] }
        else:
            # If user removes last folder by right-click in sidebar,
            # then the key 'folders' is removed from the dictionary.
            # Odd, but heh, here's a fix.
            if 'folders' not in project:
                project['folders'] = []
        
        folderAlreadyAdded = False
        for folder in project['folders']:
            # print(folder)
            if folder['path'] == path:
                folderAlreadyAdded = True
                break

        if folderAlreadyAdded == False:
            project['folders'].append({ 'path': path })
            self.window.set_project_data(project)

# --------------------------------
# Open folder from the sidebar 
# in FileManager.
# --------------------------------
class OpenFolder(sublime_plugin.WindowCommand):
    def run(self, paths):
        for path in paths:
            self.window.run_command(
                "open_dir",
                {"dir": os.path.dirname(path), "file": os.path.basename(path)}
            )


# --------------------------------
# Open file using default program.
# --------------------------------
class OpenFileUsingShell(sublime_plugin.WindowCommand):
    def run(self, files):
        for x in files:
            os.startfile(x)
    
    def is_visible(self, files):
        if len(files) > 0:
            x = files[0]
            if os.path.isdir(x):
                return False
        return True
