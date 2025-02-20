## Creates search page along with its JS file

import time

import pystache

import utils

def main(data):
    homeBreadcrumbsLink = utils.getWebPageLink("/", "Home")
    searchBreadcrumbsLink = utils.getWebPageLink("/" + data["definitions"]["filenames"]["search"], "Search")

    html = pystache.render(data["templates"]["page"], {
        "title":       "Search",
        "description": "Find lyrics using GitHub’s code search engine",
        "logo":        pystache.render(data["templates"]["link"], {
            "href": ".",
            "content": "Lyrics",
        }),
        "navigation":  utils.generateTopBarNavigation(data["config"]["Site"]["DbPath"] + "/"),
        "css":         data["definitions"]["filenames"]["css"],
        "search":      "",
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homeBreadcrumbsLink, searchBreadcrumbsLink),
        "name":        "search",
        "content":     pystache.render(data["templates"]["search-page-contents"], {
            "archiveLinkBranch": data["config"]["Source"]["DefaultBranch"],
            "timestamp": time.time(),
        }),
    })
    searchFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["search"],
    )
    searchFile.write(html)
    searchFile.close()
    ## Add search page relative path to sitemap
    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
        data["sitemap"].append(data["definitions"]["filenames"]["search"])
