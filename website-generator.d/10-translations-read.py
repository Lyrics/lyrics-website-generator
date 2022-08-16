import os

import utils

def getOriginalLyricsText(data, groupKey, artistKey, releaseKey, recordingKey):
    dbPath = os.path.join(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["SourcePath"],
    )
    dbPath = os.path.abspath(dbPath)
    origLyricsFilePath = os.path.join(dbPath, groupKey, artistKey, releaseKey, recordingKey)
    return utils.getText(open(origLyricsFilePath, "r").read().strip()) if os.path.isfile(origLyricsFilePath) else ""

def main(data):
    trPath = os.path.join(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["SourcePathTranslations"],
    )
    trPath = os.path.abspath(trPath)
    ## Loop through languages
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
                        ## Skip translation mapping files
                        if (recordingKey.endswith(".ltrm")):
                            continue
                        trLanguageGroupArtistReleaseRecordingPath = os.path.join(
                            trLanguageGroupArtistReleasePath,
                            recordingKey,
                        )
                        rawContents = open(trLanguageGroupArtistReleaseRecordingPath, "r").read().strip()
                        rawText = utils.getText(rawContents)
                        rawMetadata = utils.getMetadata(rawContents)
                        trMapPath = trLanguageGroupArtistReleaseRecordingPath + ".ltrm"
                        trMapExists = os.path.isfile(trMapPath)
                        trMapData = open(trMapPath, "r").read() if trMapExists else ""
                        data["translations"][languageKey][groupKey][artistKey]["releases"][-1]["recordings"][0].append({
                            "name":           recordingKey,
                            "printable_name": recordingKey,
                            "text":           rawText,
                            "metadata":       utils.parseMetadata(rawMetadata),
                            "map":            trMapData,
                            "original_text":  getOriginalLyricsText(data, groupKey, artistKey, releaseKey, recordingKey),
                        })
