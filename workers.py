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
        self.presentData = list(map(lambda entry: "{}{}".format(entry[0],entry[1]), allTuples))
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
        print(allFiles)
        allFiles2 = flattenList(allFiles)
        self.queue.put(len(allFiles2))
        firstSet = set(allFiles2)
        secondSet = set(self.presentData)
        missing = firstSet - secondSet
        self.queue.put(len(missing))
        with open(self.outputFilename, "w") as outfile:
            outfile.write("File Path,\n")
            outfile.write("\n".join(list(map(lambda entry: '"{}"'.format(entry), sorted(list(missing))))))


    def gather(self, myDirectory, depth):
        # Recurse into non .dirs
        children = listdir(myDirectory)
        print(myDirectory, children)
        # filter out dot files and directories
        children = list(filter(lambda x: not self.Dot.match(x), children))
        # Convert these to absolute paths
        children = list(map(lambda child: "{}/{}".format(myDirectory,child), children))
        print(myDirectory, children)
        # Filter out files and take only directories
        allDirs = list(filter(isdir, children))
        print(allDirs)
        if len(allDirs) == 0:
            # Bottomed out. Return the files that matter
            self.queue.put(depth)
            return list(filter(self.goodExtensions.match, children))
        else:
            return list(map(lambda aDir: self.gather(aDir, depth + 1), allDirs))
def isFlat(someList):
    return bool(reduce(lambda x,y: x and y, map(lambda item: not isinstance(item, list), someList)))

def flattenList(aList):
    # Check if the list is flat
    if not isFlat(aList):
        newList = []
        for item in aList:
            if isinstance(item, list):
                # Check if the sublist is flat:
                if not isFlat(item):
                    # Flatten it
                    print(item)
                    item = flattenList(item)
                newList.extend(item)
            else:
                newList.append(item)
        return newList
    return aList
freeze_support()
