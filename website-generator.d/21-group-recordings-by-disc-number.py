def main(data):
    ## Take the unsorted 2D array of recordings, parse their metadata, and sort them into sub-arrays that represent discs
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = group[artistKey]
            for release in artist["releases"]:
                sourceRecordings = release["recordings"].pop()
                indicesToRemoveFromSourceRecordings = []
                i = 0
                for recording in sourceRecordings:
                    metadata = recording["metadata"]
                    ## Determine disc number
                    discNo = int(metadata["Disc no"][0]) if "Disc no" in metadata else 0
                    if discNo > 0:
                        ## Make sure there’s an array for this disc
                        while len(release["recordings"]) < discNo:
                            release["recordings"].append([])
                        release["recordings"][discNo - 1].append(recording)
                        indicesToRemoveFromSourceRecordings.append(i)
                    i += 0
                for i in indicesToRemoveFromSourceRecordings:
                    sourceRecordings.pop(i)
                ## Make recordings that don’t have disc number appear after ones that do (on the bottom)
                if len(sourceRecordings) > 0:
                    release["recordings"].append(sourceRecordings)
