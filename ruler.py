import sublime
import sublime_plugin


class RulerManager(object):
	def __init__(self, view):
		self.view = view
		self.settings = view.settings()
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
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Methods

	# --------------
	# Toggle (wrapper fn)
	# --------------
	def toggle(self):
		# Variables
		# is_source_code = "source" in self.view.scope_name(0)
		self.toggleRuler()

	# --------------
	# Is Ruler displayed?
	# --------------
	def is_ruler_displayed(self):
		return ( len(self.get_rulers()) > 0 )

	# --------------
	# Toggle ruler
	# --------------
	def toggleRuler(self):
		rulers = self.get_rulers()
		word_wrap = self.get_word_wrap()
		subl_msg = "Wrap: N/A"

		if self.is_ruler_displayed():
			rulers = []
			word_wrap = False
			subl_msg = "Wrap: OFF"
		else:
			rulers = [self.get_wrap_width()]
			word_wrap = True
			subl_msg = "Wrap: ON"

		self.set_rulers(rulers)
		self.set_word_wrap(word_wrap)
		sublime.status_message(subl_msg)

	# --------------
	# Adjust ruler
	# --------------
	def adjust_ruler(self):
		rulers = self.get_rulers()
		wrap_width = self.get_wrap_width()

		if self.is_ruler_displayed() == True: 
			rulers = [wrap_width]
			self.set_rulers(rulers)		
		return



class ToggleRuler(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.RulerManager = RulerManager(view)
		self.view = view

	def run(self, edit):
		self.RulerManager.toggle()
		return


class SetWordWrap(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.RulerManager = RulerManager(view)
		self.view = view
		self.view.settings().add_on_change("wrap_width", self.RulerManager.adjust_ruler)

	def run(self, edit, width):		
		settings = self.view.settings()
		settings.set("wrap_width", width)