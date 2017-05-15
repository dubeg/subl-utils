import sublime_plugin
import os

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