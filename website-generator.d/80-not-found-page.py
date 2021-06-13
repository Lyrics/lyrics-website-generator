## Creates 404 page

import pystache

import utils

def main(data):
    html = pystache.render(data["templates"]["page"], {
        "title":       "Page not found",
        "description": "Error 404: page not found",
        ## Since we don't know the depth of this page relative to the root,
        ## we have to assume the db directory is located in the root of this web resource
        "navigation":  utils.generateTopBarNavigation("/" + data["config"].get("Site", "DbPath")),
        "name":        "error",
        "content":     pystache.render(data["templates"]["not-found-page-contents"]),
        ## Since we don't know the depth of this page relative to the root,
        ## we have to assume the search page is located in the root of this web resource
        "search":      "/" + data["definitions"]["filenames"]["search"],
    })
    notFoundFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"].get("Filesystem", "DestinationDirPath"),
        data["definitions"]["filenames"]["notfound"],
    )
    notFoundFile.write(html)
    notFoundFile.close()
