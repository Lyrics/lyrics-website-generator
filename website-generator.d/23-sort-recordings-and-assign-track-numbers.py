import pystache

import utils

def main(data):
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = group[artistKey]
            for release in artist["releases"]:
                for recordingGroup in release["recordings"]:
                    ## Determine if tracks bear alphabetic or decimal enumeration
                    isOrderDecimal = False
                    for recording in recordingGroup:
                        if "track_no" in recording and recording["track_no"].isdecimal():
                            isOrderDecimal = True
                            break
                    ## Sort recordings list within release by track number/letter
                    if isOrderDecimal:
                        # By number, for CDs and WEB releases
                        recordingGroup.sort(key=utils.sortRecordingsByTrackNumber)
                    else:
                        # By letter (or letter + number, e.g. A, B1, B2), for LPs and cassette tapes
                        recordingGroup.sort(key=utils.sortRecordingsByTrackLetter)
                    ## Assign recording number/letter labels
                    for recording in recordingGroup:
                        utils.formatRecordingNumber(recording)
