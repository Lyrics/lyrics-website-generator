import os

import utils

def main(data):
    ## Loop through artist groups
    dbPath = os.path.join(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["SourcePath"],
    )
    dbPath = os.path.abspath(dbPath)
    groups = sorted(next(os.walk(dbPath))[1])
    for groupKey in groups:
        data["database"][groupKey] = {}
        dbGroupPath = os.path.join(
            dbPath,
            groupKey,
        )
        ## Loop through artists
        artists = sorted(next(os.walk(dbGroupPath))[1], key=str.lower)
        for artistKey in artists:
            dbGroupArtistPath = os.path.join(
                dbGroupPath,
                artistKey,
            )
            data["database"][groupKey][artistKey] = {
                "printable_name": artistKey,
                "releases":       [],
            }
            ## Loop through the artist’s releases
            releases = sorted(next(os.walk(dbGroupArtistPath))[1], key=str.lower)
            for releaseKey in releases:
                dbGroupArtistReleasePath = os.path.join(
                    dbGroupArtistPath,
                    releaseKey,
                )
                data["database"][groupKey][artistKey]["releases"].append({
                    "name":           releaseKey,
                    "printable_name": releaseKey,
                    "recordings":     [[]],
                })
                ## Loop through release’s recordings
                recordings = sorted(next(os.walk(dbGroupArtistReleasePath))[2], key=str.lower)
                for recordingKey in recordings:
                    dbGroupArtistReleaseRecordingPath = os.path.join(
                        dbGroupArtistPath,
                        releaseKey,
                        recordingKey,
                    )
                    rawContents = open(dbGroupArtistReleaseRecordingPath, "r").read().strip()
                    rawText = utils.getText(rawContents)
                    rawMetadata = utils.getMetadata(rawContents)
                    metadata = utils.parseMetadata(rawMetadata)
                    data["database"][groupKey][artistKey]["releases"][-1]["recordings"][0].append({
                        "name": recordingKey,
                        "printable_name": recordingKey,
                        "text":           rawText,
                        "metadata":       metadata,
                    })
                    ## Index path and keywords
                    data["paths"].append(groupKey + "/" +artistKey + "/" + releaseKey + "/" + recordingKey)
                    ## Replace useless and dangerous characters with spaces
                    for c in list("`~!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?…’“”–—∕№€（）꞉"):
                        rawText = rawText.replace(c, " ")
                    ## Split and remove empty strings
                    textKeywords = list(filter(None, rawText.split()))
                    for textKeyword in textKeywords:
                        textKeywordLowercase = textKeyword.lower()
                        if not textKeywordLowercase in data["keywords"]:
                            data["keywords"][textKeywordLowercase] = []
                        pathIndex = len(data["paths"]) - 1
                        if not pathIndex in data["keywords"][textKeywordLowercase]:
                            data["keywords"][textKeywordLowercase].append(pathIndex)
                    ## Index metadata values in addition to text keywords
                    for metadataKey in metadata:
                        if metadataKey in ["Name", "Artist", "Album", "Year", "Original text by"]:
                            metadataValues = metadata[metadataKey]
                            for metadataValue in metadataValues:
                                ## Replace useless and dangerous characters with spaces
                                for c in list("`~!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?…’“”–—∕№€（）꞉"):
                                    metadataValue = metadataValue.replace(c, " ")
                                ## Split and remove empty strings
                                metadataValueKeywords = list(filter(None, metadataValue.split()))
                                for metadataValueKeyword in metadataValueKeywords:
                                    metadataValueKeywordLowercase = metadataValueKeyword.lower()
                                    if metadataValueKeywordLowercase in data["keywords"]:
                                        data["keywords"][metadataValueKeywordLowercase].append(len(data["paths"]) - 1)
                                    else:
                                        data["keywords"][metadataValueKeywordLowercase] = [len(data["paths"]) - 1]
