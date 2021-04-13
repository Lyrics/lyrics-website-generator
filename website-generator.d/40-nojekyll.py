import utils

def main(data):
    fileHandle = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        ".nojekyll",
    )
    fileHandle.close()
