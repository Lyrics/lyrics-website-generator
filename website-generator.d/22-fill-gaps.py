import utils

def main(data):
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = group[artistKey]
            for release in artist["releases"]:
                for recordingGroup in release["recordings"]:
                    ## Fill missing tracks with empty disc items for retaining visual order
                    utils.fillTheGaps(data["definitions"], recordingGroup)
