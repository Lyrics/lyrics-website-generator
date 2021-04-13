## Creates search page along with its JS file

import pystache

import utils

def main(data):
    homeBreadcrumbsLink = utils.getWebPageLink("/", "Home")
    searchBreadcrumbsLink = utils.getWebPageLink("/" + data["definitions"]["filenames"]["search"], "Search")

    html = pystache.render(data["templates"]["page"], {
        "title":       "Search",
        "description": "Find lyrics using GitHub’s code search engine",
        "navigation":  data["definitions"]["abc"],
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homeBreadcrumbsLink, searchBreadcrumbsLink),
        "name":        "search",
        "content":     pystache.render(data["templates"]["search-page-contents"]),
        "search":      data["definitions"]["filenames"]["search"],
    })
    searchFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["search"],
    )
    searchFile.write(html)
    searchFile.close()
    ## Add search page relative path to sitemap
    data["sitemap"].append(data["definitions"]["filenames"]["search"])
