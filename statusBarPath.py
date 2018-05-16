import os
import os.path
import sublime
import sublime_plugin


class CurrentPathStatusCommand(sublime_plugin.EventListener):

    def on_activated(self, view):
        path = view.file_name()
        if path != None and path != "":
            maxDirs = 3
            desiredNameLength = 12
            minHiddenChars = 4
            path = self.shortenPath(path, maxDirs, desiredNameLength, minHiddenChars)
            view.set_status('zPath', path)

    def shortenPath(self, path, maxDirs, desiredNameLength, minHiddenChars):
        path = os.path.normpath(path)
        parts = list(filter(None, path.split(os.sep)))
        # ---
        partsCount = len(parts)
        dirCount = partsCount - 2
        if dirCount < 1:
            return path;
        # Filename
        shortenedPath = parts[partsCount - 1] 
        # Directories
        for i in range(dirCount):
            if i == 0: 
                continue;
            if i > maxDirs:
                break;
            name = parts[partsCount - 1 - i];
            shortenedPath = name + os.sep + shortenedPath
        hiddenDirs = dirCount - maxDirs
        if hiddenDirs > 0:
            shortenedPath = '...' + os.sep + shortenedPath
        # Root (drive or unc mount)
        shortenedPath = parts[0] + os.sep + shortenedPath
        if path.startswith('\\\\'):
            shortenedPath = '\\\\' + shortenedPath
        return shortenedPath