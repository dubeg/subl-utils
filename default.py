import sublime
import sublime_plugin
import os

# ---------------------------------------------------
# Make RenameFile available as window command.
# ---------------------------------------------------
class RenameFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		filename = self.window.active_view().file_name()
		self.window.run_command("rename_path", {"paths":[filename]})