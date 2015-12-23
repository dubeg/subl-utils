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
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Methods
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def toggle(self):
		# Variables
		is_source_code = "source" in self.view.scope_name(0)
		word_wrap = self.get_word_wrap()

		if(word_wrap != False) and (is_source_code == False):
			self.toggleRuler()
			print("Ruler: toggled.")
		else:
			print("Ruler: no action taken")		

	def is_ruler_displayed(self):
		return ( len(self.get_rulers()) > 0 )

	def toggleRuler(self):
		rulers = self.get_rulers()
		if self.is_ruler_displayed() == False:
			rulers = [self.get_wrap_width()]
		else:
			rulers = []
		self.set_rulers(rulers)

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