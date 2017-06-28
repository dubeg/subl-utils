import sublime
import sublime_plugin
import os
import subprocess

# ---------------------------------------------------
# Make RenameFile available as window command.
# ---------------------------------------------------
class RenameFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		filename = self.window.active_view().file_name()
		self.window.run_command("rename_path", {"paths":[filename]})

# ---------------------------------------------------
# Pop out current file in new window.
# ---------------------------------------------------
class PopOutFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window
		view = window.active_view()
		filename = view.file_name()
		if filename != None and filename != "":
			subprocess.Popen(["subl", "-n", filename], shell=True)
			window.status_message("Pop: popped.")
		else:
			window.status_message("Pop: unsaved file not supported.")