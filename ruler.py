import sublime
import sublime_plugin


class ViewUtil(object):
	def __init__(self, view):
		self.view = view;
		self.settings = view.settings();

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Getters
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def get_rulers(self):
		return self.settings.get("rulers")

	def get_word_wrap(self):
		return self.settings.get("word_wrap")

	def get_wrap_width(self):
		return self.settings.get("wrap_width")
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Setters 
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def set_rulers(self, value):
		self.settings.set("rulers", value)

	def set_word_wrap(self, value):
		self.settings.set("word_wrap", value)

	def set_wrap_width(self, value):
		self.settings.set("wrap_width", value);
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Set Wrap
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def setWrap(self, width):
		rulers = self.get_rulers()
		word_wrap = self.get_word_wrap()
		status = "Wrap: N/A"

		if (width > 0): 
			rulers = [width];
			word_wrap = True;
			status = "Wrap: ON";
		else:
			rulers = [];
			word_wrap = False;
			status = "Wrap: OFF"

		self.set_rulers(rulers)
		self.set_word_wrap(word_wrap)
		self.set_wrap_width(width)
		sublime.status_message(status)
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Set Wrap At Cursor
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def setWrapAtCursor(self):
		print("~~~")

		pointOfHighestCol = None
		rowOfHighestCol = -1
		highestCol = -1
		for s in self.view.sel():
			(row,col) =  self.view.rowcol(s.end())
			if col > highestCol:
				highestCol = col
				rowOfHighestCol = row
				pointOfHighestCol = s.end()

		lineRegion = self.view.full_line(pointOfHighestCol)
		lineContent = self.view.substr(lineRegion)
 	
		# Get tab size.
		settings = self.view.settings()
		useTabStop = settings.get("use_tab_stops", False)
		tabSize = settings.get("tab_size", 1)

		# Count totals
		total = 0
		nextStop = tabSize
		for i, char in enumerate(lineContent):
			if i > (highestCol - 1):
				break

			if char == "\t":
				total += nextStop
			else:
				total += 1

			if (total % 4) == 0:
				nextStop = tabSize
			else:
				nextStop -= 1
		
		# Print infos.
		print( "Cursor.Y: " + str(rowOfHighestCol) )
		print( "Cursor.X: " + str(total) )
		# Set wrap width
		self.setWrap(total)
	# --------------
	# Update Rulers
	# --------------
	def update_ruler(self):
		rulers = self.get_rulers()
		wrap_width = self.get_wrap_width()
		
		if (wrap_width is not None) and (wrap_width > 0):
			rulers = [wrap_width];
		else:
			rulers = [];
		
		self.set_rulers(rulers);
		return;



class DisableWrap(sublime_plugin.TextCommand):
	def run(self, edit):		
		viewUtil = ViewUtil(self.view);
		viewUtil.setWrap(0);
		return;

class SetWrap(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.view = view;
		return;
		#view.settings().add_on_change("wrap_width", on_wrapwidth_changed);

	def run(self, edit, width):		
		viewUtil = ViewUtil(self.view);
		viewUtil.setWrap(width);
		return;

class SetWrapAtCursor(sublime_plugin.TextCommand):
	def run(self, edit):
		viewUtil = ViewUtil(self.view);
		viewUtil.setWrapAtCursor();
		return;