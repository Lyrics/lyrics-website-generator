import json
import sys

import utils

def main(data):
    ## Output progress status
    print(utils.indent("Writing search keywords files"), file=sys.stderr)
    sys.stderr.flush()
    ## Create directory that will contain search keywords files
    utils.mkdir(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        "s",
    )
    ## Create search keywords JSON files
    keywordGroups = {}
    for keyword in data["keywords"]:
        if keyword[0] in keywordGroups:
            keywordGroups[keyword[0]][keyword] = data["keywords"][keyword]
        else:
            keywordGroups[keyword[0]] = { keyword: data["keywords"][keyword] }
    for keywordGroup in keywordGroups:
        keywordGroupJson = json.dumps(keywordGroups[keywordGroup], separators=(',', ':'))
        searchKeywordsGroupFile = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            "s",
            keywordGroup + ".json",
        )
        searchKeywordsGroupFile.write(keywordGroupJson)
        searchKeywordsGroupFile.close()
