import sublime
import sublime_plugin


class ToggleRuler(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = self.view.settings()
		is_ruler_display = False
		is_wrap_enabled = False
		is_source_code = "source" in self.view.scope_name(0)
		word_wrap = settings.get("word_wrap")
		wrap_width = settings.get("wrap_width")
		rulers = settings.get("rulers")
		
		# Keys:
		# word_wrap
		# wrap_width
		# rulers
		if(word_wrap != False) and (is_source_code == False):
			is_wrap_enabled = True
			# Toggle ruler
			if (len(rulers) < 1): 
				rulers = [wrap_width]
			else:
				rulers = []
			settings.set("rulers", rulers)
			print("Ruler toggled.")
		else:
			print("Ruler: no action taken")

		# print( "IsCode: " + str(is_source_code) )
		# print( "Ruler: " + str(len(rulers)) )
		# print( "Wrap: " + str(word_wrap) )	
		# print( "Width: " + str(wrap_width) )
		return