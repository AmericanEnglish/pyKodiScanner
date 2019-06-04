from multiprocessing import Process, Queue, freeze_support
from os import listdir
from os.path import abspath, isdir
from os.path import join as pjoin
import re
from time import sleep
from functools import reduce
class VideoWorker(Process):
    def __init__(self, queue, topDirectory, allTuples, outputFilename):
        super(VideoWorker, self).__init__()
        self.found = 0
        self.top = topDirectory
        # self.presentData = tuple(map(lambda entry: "{}{}".format(entry[0],entry[1]), allTuples))
        self.presentData = list(allTuples)
        # print(self.presentData)
        # There are possibly many more for videos for now this all I'm willing to type
        self.Dot = re.compile("^\\.[\\s\\S]*$")
        self.goodExtensions = re.compile("^[\\s\\S]*\\.(avi|m4v|mp4|m4a|mkv)$")
        self.queue = queue
        self.outputFilename = outputFilename
    def run(self):
        # Gather all media name and locations from selectedDirectory
        # collectedData = self.gather(topDirectory)
        # Use list -> set -> difference -> list to remove matching entries
        # Write out file that contains the name and locations of all missing media
        # Return the number of entries missing and filename that was written

        # Some silly tests
        # for i in range(10):
            # self.queue.put(str(i))
            # sleep(1)
        allFiles = self.gather(self.top, 0)
        # print(allFiles)
        # print("{} --- length == {}".format(allFiles, len(allFiles)))
        allFilesFlat = flattenList(allFiles)
        alltypes = list(set(list(map(type, allFilesFlat))))
        print("Datatypes in top level: {}".format(alltypes))
        print("List? {}".format(list(filter(lambda x: isinstance(x, list), allFilesFlat))))
        # print("{} --- length == {}".format(allFilesFlat, len(allFilesFlat)))
        # allFilesFlat.sort()
        # print(allFilesFlat)
        # firstSet = set(allFilesFlat)
        # secondSet = set(self.presentData)
        # Only movie names from Kodi
        # self.presentData = sorted(self.presentData)
        allDetectedKodi = list(map(lambda x: x[0], self.presentData))
        # Only detected movie names
        allDetectedMedia = list(map(lambda x: x[0], allFilesFlat))

        # A bad find style
        missing = list(filter(lambda x: not x[0], map(lambda x: (x[1] in allDetectedKodi,x[0]), enumerate(allDetectedMedia))))
        print(missing)
        # Generate collection of missing names
        missingNames = []
        for entry in missing:
            missingNames.append("{}{}".format(allFilesFlat[entry[1]][1], allFilesFlat[entry[1]][0]))
        self.queue.put(len(missing))
        with open(self.outputFilename, "w") as outfile:
            outfile.write("File Path,\n")
            outfile.write("\n".join(list(map(lambda entry: '"{}"'.format(entry), sorted(list(missingNames))))))


    def gather(self, myDirectory, depth):
        # Recurse into non .dirs
        children = listdir(myDirectory)
        # print(myDirectory, children)
        # filter out dot files and directories
        children = list(filter(lambda x: not self.Dot.match(x), children))
        # print(children)
        # Convert these to absolute paths
        children2 = list(map(lambda child: "{}/{}".format(myDirectory,child), children))
        # print(myDirectory, children)
        # Filter out files and take only directories
        allDirs = list(filter(isdir, children2))
        # print(allDirs)
        if len(allDirs) == 0:
            # Bottomed out. Return the files that matter
            self.queue.put("({})".format(myDirectory[:]))
            return list(map(lambda child: (child, myDirectory), filter(self.goodExtensions.match, children)))
        else:
            return list(map(lambda aDir: self.gather(aDir, depth + 1), allDirs))
def isFlat(someList):
    if len(someList) > 1:
        return bool(reduce(lambda x,y: x and y, map(lambda item: not isinstance(item, list), someList)))
    elif len(someList) == 1:
        return not isinstance(someList[0], list)
    else:
        return True
        


def flattenList(aList):
    # Check if the list is flat
    if not isFlat(aList):
        newList = []
        for item in aList:
            if isinstance(item, list):
                # Check if the sublist is flat:
                if len(item) >= 1 and not isFlat(item):
                    # Flatten it
                    # print(item)
                    item = flattenList(item)
                newList.extend(item)
            else:
                newList.append(item)
        return newList
    return aList
freeze_support()
