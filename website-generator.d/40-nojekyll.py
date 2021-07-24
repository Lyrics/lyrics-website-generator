## Responsible for creating empty .nojekyll file
## That file tells GitHub pages to not treat these files as a Jekyll project

import utils

def main(data):
    fileHandle = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        ".nojekyll",
    )
    fileHandle.close()
