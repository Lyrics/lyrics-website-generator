## Responsible for creating homepage HTML file

import pystache

import utils

def main(data):
    homePathWebPageLink = utils.getWebPageLink(".", "Home")
    ## Render HTML
    listHtml = pystache.render(data["templates"]["list"], {
        "links": [
            utils.getWebPageLink(data["config"]["Site"]["DbPath"] + "/", "Database"),
            utils.getWebPageLink(data["config"]["Site"]["TranslationsPath"] + "/", "Translations"),
        ],
    })
    html = pystache.render(data["templates"]["page"], {
        "title":       data["config"]["Site"]["Name"],
        "description": "Web interface for Open Lyrics Database",
        "logo":        pystache.render(data["templates"]["link"], {
            "href": ".",
            "content": "Lyrics",
        }),
        "navigation":  utils.generateTopBarNavigation(data["config"]["Site"]["DbPath"] + "/"),
        "css":         data["definitions"]["filenames"]["css"],
        "search":      data["definitions"]["filenames"]["search"],
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink),
        "name":        "home",
        "content":     listHtml + pystache.render(data["templates"]["home-page-contents"], {
            "archiveLinkBranch": data["config"]["Source"]["DefaultBranch"],
        }),
    })
    homepageFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["index"]
    )
    homepageFile.write(html)
    homepageFile.close()
    ## Add home page link to sitemap
    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
        data["sitemap"].append("/")
