import os
import os.path
import sublime
import sublime_plugin


class CurrentPathStatusCommand(sublime_plugin.EventListener):

    def on_activated(self, view):
        path = view.file_name()
        if path != None and path != "":
            maxDirs = 3
            path = self.shortenPath(path, maxDirs)
            view.set_status('zPath', path)

    # --------------------------------
    # Shorten path by hidding directories,
    # exluding the root. 
    # --------------------------------
    def shortenPath(self, path, maxDirs):
        path = os.path.normpath(path)
        parts = list(filter(None, path.split(os.sep)))
        # ---
        partsCount = len(parts)

        dirCount = partsCount - 1 # Minus fileName.
        if dirCount < maxDirs:
            return path;

        # Add filename
        shortenedPath = parts[partsCount - 1] 

        # Add directories
        for i in range(dirCount):
            if i == 0: 
                continue;
            if i > maxDirs:
                break;
            name = parts[partsCount - 1 - i];
            shortenedPath = name + os.sep + shortenedPath
        
        # Add "..." if necessary
        hiddenDirs = dirCount - maxDirs
        if hiddenDirs > 0:
            shortenedPath = '...' + os.sep + shortenedPath
        
        # Add root
        shortenedPath = parts[0] + os.sep + shortenedPath
        if path.startswith('\\\\'):
            shortenedPath = '\\\\' + shortenedPath
        return shortenedPath