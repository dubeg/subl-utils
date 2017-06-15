import sublime
import sublime_plugin
import os

# -------------------------------------------------------
# On PluginLoaded, SaveDirectory = UserProfile
# -------------------------------------------------------
def plugin_loaded():
	dir = '%USERPROFILE%'
	view = sublime.active_window().active_view()
	if view != None:
		view.settings().set('default_dir', dir)

# -------------------------------------------------------
# On NewBuffer, SaveDirectory = OpenedFolder
# -------------------------------------------------------
# class NewFileListener(sublime_plugin.EventListener):
#     def on_new_async(self, view):
#         if view.window() and view.window().folders():
#         	dir = view.window().folders()[0]
#         	view.settings().set('default_dir', dir)

# -------------------------------------------------------
# On FileLoaded, SaveDirectory = FileDirectory
# -------------------------------------------------------
class LoadFileListener(sublime_plugin.EventListener):
	def on_load(self, view):
		dir = os.path.dirname(view.file_name())
		view.settings().set('default_dir', dir)

# -------------------------------------------------------
# On FileSaved, SaveDirectory = FileDirectory
# -------------------------------------------------------
class PostSaveFileListener(sublime_plugin.EventListener):
	def on_post_save(self, view):
		dir = os.path.dirname(view.file_name())
		if dir != None and dir != "":
			view.settings().set('default_dir', dir)

# -------------------------------------------------------
# On NewWindow, SaveDirectory = UserProfile
# -------------------------------------------------------
# class OnNewWindowListener(sublime_plugin.EventListener):
# 	def on_window_command(self, window, cmdName, args):
# 		self.windowCount = 0
# 	def on_post_window_command(self, window, cmdName, args):
# 		windows = sublime.windows()
# 		newCount = len(windows)
# 		if self.windowCount < newCount:
# 			window = windows[-1]
# 			view = window.active_view()
# 			view.settings().set('default_dir', '%USERPROFILE%')
# 			windowCount = newCount

