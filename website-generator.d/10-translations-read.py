import os

import utils

def main(data):
    ## Loop through languages
    trPath = os.path.join(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["SourcePathTranslations"],
    )
    trPath = os.path.abspath(trPath)
    languages = sorted(next(os.walk(trPath))[1])
    for languageKey in languages:
        data["translations"][languageKey] = {}
        trLanguagePath = os.path.join(
            trPath,
            languageKey,
        )
        ## Loop through artist groups
        groups = sorted(next(os.walk(trLanguagePath))[1])
        for groupKey in groups:
            data["translations"][languageKey][groupKey] = {}
            trLanguageGroupPath = os.path.join(
                trLanguagePath,
                groupKey,
            )
            ## Loop through artists start begin with
            artists = sorted(next(os.walk(trLanguageGroupPath))[1], key=str.lower)
            for artistKey in artists:
                trLanguageGroupArtistPath = os.path.join(
                    trLanguageGroupPath,
                    artistKey,
                )
                data["translations"][languageKey][groupKey][artistKey] = {
                    "printable_name": artistKey,
                    "releases":       [],
                }
                ## Loop through artist’s releases
                releases = sorted(next(os.walk(trLanguageGroupArtistPath))[1], key=str.lower)
                for releaseKey in releases:
                    trLanguageGroupArtistReleasePath = os.path.join(
                        trLanguageGroupArtistPath,
                        releaseKey,
                    )
                    data["translations"][languageKey][groupKey][artistKey]["releases"].append({
                        "name":           releaseKey,
                        "printable_name": releaseKey,
                        "recordings":     [[]],
                    })
                    ## Loop through release’s recordings
                    recordings = sorted(next(os.walk(trLanguageGroupArtistReleasePath))[2], key=str.lower)
                    for recordingKey in recordings:
                        trLanguageGroupArtistReleaseRecordingPath = os.path.join(
                            trLanguageGroupArtistReleasePath,
                            recordingKey,
                        )
                        rawContents = open(trLanguageGroupArtistReleaseRecordingPath, "r").read().strip()
                        rawText = utils.getText(rawContents)
                        rawMetadata = utils.getMetadata(rawContents)
                        data["translations"][languageKey][groupKey][artistKey]["releases"][-1]["recordings"][0].append({
                            "name":           recordingKey,
                            "printable_name": recordingKey,
                            "text":           rawText,
                            "metadata":       utils.parseMetadata(rawMetadata),
                        })
