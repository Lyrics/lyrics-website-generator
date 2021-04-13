import pystache

import utils

def main(data):
    ## Assign readable names to artists/releases/recordings
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = group[artistKey]
            for release in artist["releases"]:
                for recording in release["recordings"][0]:
                    text = recording["text"]
                    metadata = recording["metadata"]
                    ## Make use of any available metadata values
                    if "Name" in metadata:
                        recording["printable_name"] = metadata["Name"][0]
                    if "Artist" in metadata:
                        artist["printable_name"] = metadata["Artist"][0]
                    if "Album" in metadata:
                        release["printable_name"] = metadata["Album"][0]
                    if "Track no" in metadata:
                        recording["track_no"] = metadata["Track no"][0]
                    if "Disc no" in metadata:
                        recording["disc_no"] = metadata["Disc no"][0]
                    if "Year" in metadata:
                        release["year"] = metadata["Year"][0]
                    ## Mark instrumental texts within parent page’s (album) list
                    if len(text) == 0:
                        recording["postfix"] = data["config"]["Site"]["InstrumentalLabel"]
