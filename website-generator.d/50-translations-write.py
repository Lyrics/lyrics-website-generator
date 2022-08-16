import os
import sys

import pystache

import utils

def main(data):
    homePathWebPageLink = utils.getWebPageLink("/", "Home")

    ## Output progress status
    print("Website translation HTML files", file=sys.stderr)
    sys.stderr.flush()
    ## Generate link
    trPathWebPageLink = utils.getWebPageLink(data["config"]["Site"]["TranslationsPath"] + "/", "Translations")
    ## Create containing directory
    utils.mkdir(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["config"]["Site"]["TranslationsPath"],
    )
    ## Create root index file for translations directory
    translationsLinkList = []
    for groupKey in data["translations"]:
        link = pystache.render(data["templates"]["link"], {
            "href": groupKey + "/",
            "content": groupKey,
        })
        translationsLinkList.append(link)
    html = pystache.render(data["templates"]["page"], {
        "title":       "List of available translations languages",
        "description": utils.getDescriptionList(list(data["translations"].keys())),
        "logo":        pystache.render(data["templates"]["link"], {
            "href": ".." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
            "content": "Lyrics",
        }),
        "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 1) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
        "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 1),
        "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 1),
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink),
        "name":        "translations",
        "content":     pystache.render(data["templates"]["db-page-contents"], {
            "links": translationsLinkList,
        }),
    })
    translationsFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["config"]["Site"]["TranslationsPath"],
        data["definitions"]["filenames"]["index"],
    )
    translationsFile.write(html)
    translationsFile.close()
    ## Add relative path to list of sitemap items
    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
        data["sitemap"].append(data["config"]["Site"]["TranslationsPath"] + "/")

    ## Loop through languages
    for languageKey in data["translations"]:
        ## Output progress status
        print(utils.indent(languageKey, 1), file=sys.stderr)
        sys.stderr.flush()
        ## Assign variables
        language = data["translations"][languageKey]
        ## Resolve paths
        languagePathSource = os.path.join(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["SourcePathTranslations"],
            languageKey,
        )
        languagePathDestination = os.path.join(
            data["config"]["Site"]["TranslationsPath"],
            languageKey,
        )
        ## Generate link
        languagePathWebPageLink = utils.getWebPageLink(languageKey + "/", languageKey, data["definitions"]["link_types"]["language"])
        ## Create containing directory
        utils.mkdir(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            languagePathDestination,
        )
        ## Render HTML
        pageLinks = []
        for groupKey in language:
            link = utils.getWebPageLink(groupKey + "/", groupKey, data["definitions"]["link_types"]["group"])
            pageLinks.append(link)
        listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
        html = pystache.render(data["templates"]["page"], {
            "title":       "Groups of artists containing " + languageKey + " translations",
            "description": utils.getDescriptionList(list(language.keys())),
            "logo":        pystache.render(data["templates"]["link"], {
                "href": "../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                "content": "Lyrics",
            }),
            "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 2) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
            "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 2),
            "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 2),
            "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink, languagePathWebPageLink),
            "name":        "language",
            "content":     listHtml,
        })
        ## Create index HTML file
        htmlFile = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            languagePathDestination,
            data["definitions"]["filenames"]["index"],
        )
        ## Write rendered HTML into the index HTML file
        htmlFile.write(html)
        htmlFile.close()
        ## Add relative path to list of sitemap items
        if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
            data["sitemap"].append(languagePathDestination + "/")

        ## Loop through groups
        for groupKey in language:
            ## Output progress status
            print(utils.indent(groupKey, 2), file=sys.stderr)
            sys.stderr.flush()
            ## Assign variables
            group = data["translations"][languageKey][groupKey]
            ## Resolve paths
            groupPathSource = os.path.join(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["SourcePathTranslations"],
                languageKey,
                groupKey,
            )
            groupPathDestination = os.path.join(
                data["config"]["Site"]["TranslationsPath"],
                languageKey,
                groupKey,
            )
            ## Generate link
            groupPathWebPageLink = utils.getWebPageLink(groupKey + "/", groupKey, data["definitions"]["link_types"]["group"])
            ## Create containing directory
            utils.mkdir(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["DestinationDirPath"],
                groupPathDestination,
            )
            ## Render HTML
            pageLinks = []
            for artistKey in group:
                link = utils.getWebPageLink(artistKey + "/", artistKey, data["definitions"]["link_types"]["artist"])
                pageLinks.append(link)
            listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
            html = pystache.render(data["templates"]["page"], {
                "title":       "Artist group “" + groupKey + "” of " + languageKey + " translations",
                "description": utils.getDescriptionList(list(group.keys())),
                "logo":        pystache.render(data["templates"]["link"], {
                    "href": "../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                    "content": "Lyrics",
                }),
                "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 3) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 3),
                "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 3),
                "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink, languagePathWebPageLink, groupPathWebPageLink),
                "name":        "group",
                "content":     listHtml,
            })
            ## Create index HTML file
            htmlFile = utils.mkfile(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["DestinationDirPath"],
                groupPathDestination,
                data["definitions"]["filenames"]["index"],
            )
            ## Write rendered HTML into the index HTML file
            htmlFile.write(html)
            htmlFile.close()
            ## Add relative path to list of sitemap items
            if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                data["sitemap"].append(groupPathDestination + "/")

            ## Loop through artists
            for artistKey in group:
                ## Output progress status
                print(utils.indent(artistKey, 3), file=sys.stderr)
                sys.stderr.flush()
                ## Assign variables
                artist = group[artistKey]
                ## Resolve paths
                artistPathSource = os.path.join(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["SourcePathTranslations"],
                    languageKey,
                    groupKey,
                    artistKey,
                )
                artistPathDestination = os.path.join(
                    data["config"]["Site"]["TranslationsPath"],
                    languageKey,
                    groupKey,
                    artistKey,
                )
                ## Generate link
                artistPathWebPageLink = utils.getWebPageLink(artistKey + "/", artistKey, data["definitions"]["link_types"]["artist"])
                ## Create containing directory
                utils.mkdir(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["DestinationDirPath"],
                    artistPathDestination,
                )
                ## Render HTML
                pageLinks = []
                for release in artist["releases"]:
                    link = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
                    pageLinks.append(link)
                listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
                html = pystache.render(data["templates"]["page"], {
                    "title":       "Releases by " + artist["printable_name"] + " containing " + languageKey + " translations",
                    "description": utils.getDescriptionList(list(map(lambda link: link["label"], pageLinks))),
                    "logo":        pystache.render(data["templates"]["link"], {
                        "href": "../../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                        "content": "Lyrics",
                    }),
                    "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 4) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                    "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 4),
                    "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 4),
                    "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink, languagePathWebPageLink, groupPathWebPageLink, artistPathWebPageLink),
                    "name":        "artist",
                    "content":     listHtml,
                })
                ## Create index HTML file
                htmlFile = utils.mkfile(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["DestinationDirPath"],
                    artistPathDestination,
                    data["definitions"]["filenames"]["index"],
                )
                ## Write rendered HTML into the index HTML file
                htmlFile.write(html)
                htmlFile.close()
                ## Add relative path to list of sitemap items
                if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                    data["sitemap"].append(artistPathDestination + "/")

                ## Loop through releases
                for release in artist["releases"]:
                    ## Output progress status
                    print(utils.indent(release["name"], 4), file=sys.stderr)
                    sys.stderr.flush()
                    ## Resolve paths
                    releasePathSource = os.path.join(
                        data["definitions"]["runtime"]["cwd"],
                        data["config"]["Filesystem"]["SourcePathTranslations"],
                        languageKey,
                        groupKey,
                        artistKey,
                        release["name"],
                    )
                    releasePathDestination = os.path.join(
                        data["config"]["Site"]["TranslationsPath"],
                        languageKey,
                        groupKey,
                        artistKey,
                        release["name"],
                    )
                    ## Generate link
                    releasePathWebPageLink = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
                    ## Create containing directory
                    utils.mkdir(
                        data["definitions"]["runtime"]["cwd"],
                        data["config"]["Filesystem"]["DestinationDirPath"],
                        releasePathDestination,
                    )
                    ## Render HTML
                    pageLinks = []
                    for recording in release["recordings"]:
                        link = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["recording"])
                        pageLinks.append(link)
                    listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
                    html = pystache.render(data["templates"]["page"], {
                        "title":       artist["printable_name"] + " " + languageKey + " translations from “" + release["printable_name"] + "”",
                        "description": utils.getDescriptionList(list(map(lambda link: link["label"], pageLinks))),
                        "logo":        pystache.render(data["templates"]["link"], {
                            "href": "../../../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                            "content": "Lyrics",
                        }),
                        "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 5) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                        "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 5),
                        "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 5),
                        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink, languagePathWebPageLink, groupPathWebPageLink, artistPathWebPageLink, releasePathWebPageLink),
                        "name":        "release",
                        "content":     listHtml,
                    })
                    ## Create index HTML file
                    htmlFile = utils.mkfile(
                        data["definitions"]["runtime"]["cwd"],
                        data["config"]["Filesystem"]["DestinationDirPath"],
                        releasePathDestination,
                        data["definitions"]["filenames"]["index"],
                    )
                    ## Write rendered HTML into the index HTML file
                    htmlFile.write(html)
                    htmlFile.close()
                    ## Add relative path to list of sitemap items
                    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                        data["sitemap"].append(releasePathDestination + "/")

                    ## Loop through recordings
                    for recordingGroup in release["recordings"]:
                        for recording in recordingGroup:
                            ## Output progress status
                            print(utils.indent(recording["name"], 5), file=sys.stderr)
                            sys.stderr.flush()
                            ## Resolve paths
                            recordingPathSource = os.path.join(
                                data["definitions"]["runtime"]["cwd"],
                                data["config"]["Filesystem"]["SourcePathTranslations"],
                                languageKey,
                                groupKey,
                                artistKey,
                                release["name"],
                                recording["name"],
                            )
                            recordingPathDestination = os.path.join(
                                data["config"]["Site"]["TranslationsPath"],
                                languageKey,
                                groupKey,
                                artistKey,
                                release["name"],
                                recording["name"],
                            )
                            ## Generate link
                            recordingPathWebPageLink = utils.getWebPageLink(recording["name"] + "/", recording["printable_name"], data["definitions"]["link_types"]["recording"])
                            ## Create containing directory
                            utils.mkdir(
                                data["definitions"]["runtime"]["cwd"],
                                data["config"]["Filesystem"]["DestinationDirPath"],
                                recordingPathDestination,
                            )
                            ## Add action buttons
                            lyricsActionsList = []
                            if data["config"].getboolean("Site", "HasEditTextButton"):
                                actionButton1 = pystache.render(data["templates"]["link"], {
                                    "href": data["config"]["Source"]["Repository"]  + "/edit/" + \
                                            data["config"]["Source"]["DefaultBranch"]  + "/translations/" + \
                                            languageKey + "/" + groupKey + "/" + artistKey + "/" + release["name"] + "/" + recording["name"],
                                    "content": "Suggest improvements for this translation",
                                })
                                lyricsActionsList.append(actionButton1)
                            ## Render HTML
                            html = pystache.render(data["templates"]["page"], {
                                "title":       languageKey + " translation of “" + recording["printable_name"] + "” by " + artist["printable_name"],
                                "description": utils.getDescriptionText(recording["text"]),
                                "logo":        pystache.render(data["templates"]["link"], {
                                    "href": "../../../../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                                    "content": "Lyrics",
                                }),
                                "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth(data["config"]["Site"]["DbPath"] + "/", 6) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                                "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 6),
                                "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 6),
                                "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, trPathWebPageLink, languagePathWebPageLink, groupPathWebPageLink, artistPathWebPageLink, releasePathWebPageLink, recordingPathWebPageLink),
                                "name":        "recording",
                                "content":     utils.formatTranslationPageContents(data["templates"], recording["original_text"], recording["text"], recording["map"], recording["metadata"], lyricsActionsList),
                            })
                            ## Create index HTML file
                            htmlFile = utils.mkfile(
                                data["definitions"]["runtime"]["cwd"],
                                data["config"]["Filesystem"]["DestinationDirPath"],
                                recordingPathDestination,
                                data["definitions"]["filenames"]["index"],
                            )
                            ## Write rendered HTML into the index HTML file
                            htmlFile.write(html)
                            htmlFile.close()
                            ## Add relative path to list of sitemap items
                            if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                                data["sitemap"].append(recordingPathDestination + "/")
