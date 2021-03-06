import sublime
import sublime_plugin
import os
import subprocess

# ---------------------------------------------------
# Make RenameFile available as window command.
# ---------------------------------------------------
class RenameFileUtilCommand(sublime_plugin.WindowCommand):
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
			window.run_command('close_file')
			
			sublime.run_command("new_window")
			sublime.active_window().open_file(filename)
			sublime.active_window().set_sidebar_visible(False)
		else:
			window.status_message("Pop: unsaved file not supported.")