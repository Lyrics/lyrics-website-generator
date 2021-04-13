## Creates 404 page

import pystache

import utils

def main(data):
    html = pystache.render(data["templates"]["page"], {
        "title":       "Page not found",
        "description": "Error 404: page not found",
        "navigation":  data["definitions"]["abc"],
        "name":        "error",
        "content":     pystache.render(data["templates"]["not-found-page-contents"]),
        "search":      data["definitions"]["filenames"]["search"],
    })
    notFoundFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["notfound"],
    )
    notFoundFile.write(html)
    notFoundFile.close()
