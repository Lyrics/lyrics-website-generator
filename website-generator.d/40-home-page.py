## Responsible for creating homepage HTML file

import pystache

import utils

def main(data):
    homePathWebPageLink = utils.getWebPageLink("/", "Home")

    ## Render HTML
    pageLinks = []
    link = utils.getWebPageLink("db" + "/", "Database")
    pageLinks.append(link)
    link = utils.getWebPageLink("tr" + "/", "Translations")
    pageLinks.append(link)
    listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
    html = pystache.render(data["templates"]["page"], {
        "title":       data["config"]["Site"]["Name"],
        "description": "Web interface for Open Lyrics Database",
        "navigation":  data["definitions"]["abc"],
        "search":      data["definitions"]["filenames"]["search"],
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink),
        "name":        "home",
        "content":     listHtml + pystache.render(data["templates"]["home-page-contents"], {
            "db": data["config"]["Site"]["DbPath"],
            "tr": data["config"]["Site"]["TranslationsPath"],
        }),
    })
    homepageFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["index"]
    )
    homepageFile.write(html)
    homepageFile.close()
    ## Add home page relative path to sitemap
    data["sitemap"].append("/")
