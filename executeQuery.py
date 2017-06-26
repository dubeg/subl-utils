import sublime
import sublime_plugin
import os
import sys
import subprocess

# Untested
def execute_query(filename):
	process = subprocess.Popen(
	    ['sqlcmd', '-E', '-S', 'servername', '-i', 'query.sql'],
	    shell = True,
	    # stdin = subprocess.PIPE, # SQLCMD takes no input.
	    stdout = subprocess.PIPE,
	    stderr = subprocess.PIPE,
	    universal_newlines=True # This enables text mode. If you set this, you don't have to decode out/err.
	)
	# out and err both contain a sequence of bytes returned by the process,
	# unless passing universal_newlines = True in Popen(). 
	out, err = process.communicate() 
	errMsg = err
	outMsg = out
	print(errMsg)
	print(outMsg)
	# Alternative Solutions
	# ---------------------------------------
	# Solution 2: use method check_output to execute cmd and retrieve its output.
	# CheckOutput returns bytes, not a string.
	# from subprocess import check_output
	# out = check_output(["cmd.exe", "-opt"])
	# ---------------------------------------
	# Solution 3: reading output while it executes.
    # popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    # for stdout_line in iter(popen.stdout.readline, ""):
    #     yield stdout_line 
    # popen.stdout.close()
    # return_code = popen.wait()
    # if return_code:
    #     raise subprocess.CalledProcessError(return_code, cmd)


class ExecuteQueryCommand(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window
		view = window.active_view()
		filename = view.file_name()
		syntaxFilename = view.settings().get('syntax')
		# if "SQL" in syntaxFilename.upper():
		if True:
			execute_query(filename)