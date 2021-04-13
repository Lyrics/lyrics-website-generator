import pystache

import utils

def main(data):
    ## Take the unsorted 2D array of recordings, parse their metadata, and sort them into sub-arrays that represent discs
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = group[artistKey]
            for release in artist["releases"]:
                source_recordings = release["recordings"].pop()
                i = 0
                for recording in source_recordings:
                    metadata = recording["metadata"]
                    ## Determine disc number
                    discNo = int(metadata["Disc no"][0]) if "Disc no" in metadata else 0
                    if discNo > 0:
                        ## Make sure there’s an array for this disc
                        while len(release["recordings"]) <= discNo:
                            release["recordings"].append([])
                        release["recordings"][discNo].append(source_recordings.pop(i))
                    i += 1
                ## Make recordings that don’t have disc number appear after ones that do (on the bottom)
                if len(source_recordings) > 0:
                    release["recordings"].append(source_recordings)
