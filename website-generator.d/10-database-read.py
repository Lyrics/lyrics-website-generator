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
                    data["database"][groupKey][artistKey]["releases"][-1]["recordings"][0].append({
                        "name": recordingKey,
                        "printable_name": recordingKey,
                        "text":           rawText,
                        "metadata":       utils.parseMetadata(rawMetadata),
                    })
