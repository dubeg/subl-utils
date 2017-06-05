import sublime
import sublime_plugin
import os


# ------------------
# On load, defaultDir = UserProfile
# On folder opened, defaultDir = Folder
# On folder created, defaultDir = Folder
# On file saved, defaultDir = FileDir
# On file opened, defaultDir = FileDir
# On file created, defaultDir = FileDir
# ------------------
def plugin_loaded():
	dir = '%USERPROFILE%'
	sublime.active_window().active_view().settings().set('default_dir', dir)

# class NewFileListener(sublime_plugin.EventListener):
#     def on_new_async(self, view):
#         if view.window() and view.window().folders():
#         	dir = view.window().folders()[0]
#         	print("NewFile: " + dir)
#         	view.settings().set('default_dir', dir)

class LoadFileListener(sublime_plugin.EventListener):
	def on_load(self, view):
		dir = os.path.dirname(view.file_name())
		view.settings().set('default_dir', dir)

class PostSaveFileListener(sublime_plugin.EventListener):
	def on_post_save(self, view):
		dir = os.path.dirname(view.file_name())
		if dir != None and dir != "":
			view.settings().set('default_dir', dir)

# ------------------------------------------------
# File Rename, Create
# ------------------------------------------------
class RenameFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		filename = self.window.active_view().file_name()
		self.window.run_command("rename_path", {"paths":[filename]})
