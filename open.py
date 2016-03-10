import sublime
import sublime_plugin
import os
import sys
import subprocess


class OpenInFileManager(sublime_plugin.WindowCommand):
    def run(self, dir):  
         
        path = dir.replace("$packages", sublime.packages_path())
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
        # Execute
        if os.path.isdir(path):
            #print([cmd, path])
            subprocess.Popen([cmd, path])
        else:
            #print([cmd, opts, path])
            subprocess.Popen([cmd, opts, path])
        
        # Just as reminder
        # ~~~~~~~~~~~~~~~~    
        # subprocess.check_call(['gnome-open', '--', path])
        # self.window.run_command("open_dir",{"dir": os.path.dirname(path)})
        # os.startfile(path)


class OpenFolder(sublime_plugin.WindowCommand):
    def run(self, paths):
        #settings = sublime.load_settings("OpenFolder.sublime-settings")
        #file_manager = settings.get("file_manager", "xdg-open '{0}'")

        for path in paths:
            #if os.path.isdir(path):
            #    call(file_manager.format(path), shell=True)
            #else:
                self.window.run_command(
                    "open_dir",
                    {"dir": os.path.dirname(path), "file": os.path.basename(path)}
                )

    def description(self, paths):
        settings = sublime.load_settings("OpenFolder.sublime-settings")
        display_for_files = settings.get('display_for_files', True)

        file_count = 0
        dir_count = 0

        for path in paths:
            if os.path.isdir(path):
                dir_count += 1
            else:
                file_count += 1

        if dir_count > 1 or (dir_count > 0 and file_count > 0):
            return "Open Folders"
        elif dir_count == 1:
            return "Open Folder"
        elif file_count > 1 and display_for_files:
            return u"Open Containing Folders\u2026"
        elif file_count > 0 and display_for_files:
            return u"Open Containing Folder\u2026"
        else:
            return None
