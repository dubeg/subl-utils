import sublime
import sublime_plugin
import os

# ------------------------------------------------
# File Load, Save
# ------------------------------------------------
class NewFileListener(sublime_plugin.EventListener):
    def on_new_async(self, view):
        if view.window() and view.window().folders():
        	print(view.settings().get('default_dir'))
        	view.settings().set('default_dir', view.window().folders()[0])

class LoadFileListener(sublime_plugin.EventListener):
	def on_load(self, view):
		dir = os.path.dirname(view.file_name())
		view.settings().set('default_dir', dir)

class PostSaveFileListener(sublime_plugin.EventListener):
	def on_post_save(self, view):
		dir = os.path.dirname(view.file_name())
		view.settings().set('default_dir', dir)

# ------------------------------------------------
# File Rename, Create
# ------------------------------------------------
class RenameFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		filename = self.window.active_view().file_name()
		self.window.run_command("rename_path", {"paths":[filename]})


# Notes
# { "caption": "New File", "command": "new_file_at", "args": {"dirs": []} },
# { "caption": "Rename…", "command": "rename_path", "args": {"paths": []} },
# { "caption": "Delete File", "command": "delete_file", "args": {"files": []} },
# { "caption": "Open Containing Folder…", "command": "open_containing_folder", "args": {"files": []} },
# { "caption": "-", "id": "folder_commands" },
# { "caption": "New Folder…", "command": "new_folder", "args": {"dirs": []} },
# { "caption": "Delete Folder", "command": "delete_folder", "args": {"dirs": []} },
# { "caption": "Find in Folder…", "command": "find_in_folder", "args": {"dirs": []} },


