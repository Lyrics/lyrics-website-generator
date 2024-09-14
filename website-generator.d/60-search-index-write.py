import json
import sys

import utils

def main(data):
    ## Output progress status
    print(utils.indent("Writing website search index file"), file=sys.stderr)
    sys.stderr.flush()
    ## Create search index JSON file
    indexJson = json.dumps(data["paths"], separators=(',', ':'), ensure_ascii=False)
    searchIndexFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        "s.json",
    )
    searchIndexFile.write(indexJson)
    searchIndexFile.close()
