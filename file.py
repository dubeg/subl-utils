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

# ---------------------------------------------------
# Split current file into multiple files based on line count
# ---------------------------------------------------
class SplitFileListInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "split_option"
		
	def list_items(self):
		return [
			["10,000 lines per file", "10000"],
			["5,000 lines per file", "5000"],
			["1,000 lines per file", "1000"],
			["Custom number of lines...", "custom"]
		]

class SplitFileCustomInputHandler(sublime_plugin.TextInputHandler):
	def name(self):
		return "lines_per_file"
		
	def placeholder(self):
		return "Enter number of lines per file"
		
	def initial_text(self):
		return "10000"
		
	def validate(self, text):
		try:
			value = int(text)
			return value > 0
		except ValueError:
			return False

class SplitFileCustomCommand(sublime_plugin.WindowCommand):
	def input(self, args):
		return SplitFileCustomInputHandler()
		
	def run(self, lines_per_file):
		view = self.window.active_view()
		filename = view.file_name()

		if not filename:
			self.window.status_message("Split: No file is currently open.")
			return
			
		# Get the content of the file
		content = view.substr(sublime.Region(0, view.size()))
		lines = content.split('\n')
		
		try:
			lines_per_file = int(lines_per_file)
			if lines_per_file <= 0:
				self.window.status_message("Split: Please enter a positive number.")
				return
		except ValueError:
			self.window.status_message("Split: Please enter a valid number.")
			return
			
		# Get the base filename and extension
		base, ext = os.path.splitext(filename)
		
		# Split the lines into chunks
		for i in range(0, len(lines), lines_per_file):
			chunk = lines[i:i + lines_per_file]
			chunk_filename = "{0}_part{1}{2}".format(base, i//lines_per_file + 1, ext)
			
			# Write the chunk to a new file
			with open(chunk_filename, 'w', encoding='utf-8') as f:
				f.write('\n'.join(chunk))
				
		self.window.status_message("Split: File split into {0} parts.".format(len(lines)//lines_per_file + 1))

class SplitFileCommand(sublime_plugin.WindowCommand):
	def input(self, args):
		return SplitFileListInputHandler()
		
	def run(self, split_option):
		if split_option == "custom":
			self.window.run_command(
				'show_overlay',
				{
					'overlay': 'command_palette', 
					'command': 'split_file_custom', 
					'args': {'lines_per_file': 0}
				},
			)
		else:
			view = self.window.active_view()
			filename = view.file_name()
			
			if not filename:
				self.window.status_message("Split: No file is currently open.")
				return
				
			# Get the content of the file
			content = view.substr(sublime.Region(0, view.size()))
			lines = content.split('\n')
			
			lines_per_file = int(split_option)
			
			# Get the base filename and extension
			base, ext = os.path.splitext(filename)
			
			# Split the lines into chunks
			for i in range(0, len(lines), lines_per_file):
				chunk = lines[i:i + lines_per_file]
				chunk_filename = "{0}_part{1}{2}".format(base, i//lines_per_file + 1, ext)
				
				# Write the chunk to a new file
				with open(chunk_filename, 'w', encoding='utf-8') as f:
					f.write('\n'.join(chunk))
					
			self.window.status_message("Split: File split into {0} parts.".format(len(lines)//lines_per_file + 1))