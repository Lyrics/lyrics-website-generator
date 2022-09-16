import os
import sys

import pystache

import utils

def main(data):
    homePathWebPageLink = utils.getWebPageLink("/", "Home")
    indexFileName = data["definitions"]["filenames"]["index"]

    ## Output progress status
    print(utils.indent("Website database HTML files"), file=sys.stderr)
    sys.stderr.flush()
    ## Generate link
    dbPathWebPageLink = utils.getWebPageLink(data["config"]["Site"]["DbPath"] + "/", "Database")
    ## Create containing directory
    utils.mkdir(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["config"]["Site"]["DbPath"],
    )
    ## Render HTML
    databaseLinkList = []
    for groupKey in data["database"]:
        link = pystache.render(data["templates"]["link"], {
            "href": groupKey + "/",
            "content": groupKey,
        })
        databaseLinkList.append(link)
    html = pystache.render(data["templates"]["page"], {
        "title":       "Main database index page",
        "description": "List of database artist groups",
        "logo":        pystache.render(data["templates"]["link"], {
            "href": ".." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
            "content": "Lyrics",
        }),
        "navigation":  utils.generateTopBarNavigation(),
        "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 1),
        "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 1),
        "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, dbPathWebPageLink),
        "name":        "db",
        "content":     pystache.render(data["templates"]["db-page-contents"], {
            "links": databaseLinkList,
        }),
    })
    ## Create index HTML file
    htmlFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["config"]["Site"]["DbPath"],
        indexFileName,
    )
    ## Write rendered HTML into index HTML file
    htmlFile.write(html)
    htmlFile.close()
    ## Add relative path to list of sitemap items
    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
        data["sitemap"].append(data["config"]["Site"]["DbPath"] + "/")

    ## Loop through letter groups
    for groupKey in data["database"]:
        ## Output progress status
        print(utils.indent(groupKey, 1), file=sys.stderr)
        sys.stderr.flush()
        ## Assign variables
        group = data["database"][groupKey]
        ## Resolve paths
        groupPathSource = os.path.join(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["SourcePath"],
            groupKey,
        )
        groupPathDestination = os.path.join(
            data["config"]["Site"]["DbPath"],
            groupKey,
        )
        ## Generate link
        groupPathWebPageLink = utils.getWebPageLink(groupKey + "/", groupKey)
        ## Create containing directory
        utils.mkdir(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            groupPathDestination,
        )
        ## Render HTML
        pageLinks = []
        for artistKey in group:
            link = utils.getWebPageLink(artistKey + "/", group[artistKey]["printable_name"], data["definitions"]["link_types"]["artist"])
            pageLinks.append(link)
        listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
        html = pystache.render(data["templates"]["page"], {
            "title":       "Artists starting with “" + groupKey + "”",
            "description": utils.getDescriptionList(list(group.keys())),
            "logo":        pystache.render(data["templates"]["link"], {
                "href": "../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                "content": "Lyrics",
            }),
            "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth("", 1) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
            "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 2),
            "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 2),
            "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, dbPathWebPageLink, groupPathWebPageLink),
            "name":        "group",
            "content":     listHtml,
        })
        ## Create index HTML file
        htmlFile = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            groupPathDestination,
            indexFileName,
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
            print(utils.indent(artistKey, 2), file=sys.stderr)
            sys.stderr.flush()
            ## Assign variables
            artist = group[artistKey]
            ## Resolve paths
            groupArtistPathSource = os.path.join(
                groupPathSource,
                artistKey,
            )
            groupArtistPathDestination = os.path.join(
                groupPathDestination,
                artistKey,
            )
            ## Generate link
            groupArtistPathWebPageLink = utils.getWebPageLink(artistKey + "/", artist["printable_name"], data["definitions"]["link_types"]["artist"])
            ## Create containing directory
            utils.mkdir(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["DestinationDirPath"],
                groupArtistPathDestination,
            )
            ## Render items list HTML
            pageLinks = []
            for release in artist["releases"]:
                link = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
                if "year" in release:
                    link["postfix"] = "(" + str(release["year"]) + ")"
                pageLinks.append(link)
            listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
            ## Render page HTML
            html = pystache.render(data["templates"]["page"], {
                "title":       "Albums by " + artist["printable_name"],
                "description": utils.getDescriptionList(list(map(lambda link: link["label"], pageLinks))),
                "logo":        pystache.render(data["templates"]["link"], {
                    "href": "../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                    "content": "Lyrics",
                }),
                "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth("", 2) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 3),
                "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 3),
                "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, dbPathWebPageLink, groupPathWebPageLink, groupArtistPathWebPageLink),
                "name":        "artist",
                "content":     listHtml,
            })
            ## Create index HTML file
            htmlFile = utils.mkfile(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["DestinationDirPath"],
                groupArtistPathDestination,
                indexFileName,
            )
            ## Write rendered HTML into the index HTML file
            htmlFile.write(html)
            htmlFile.close()
            ## Add relative path to list of sitemap items
            if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                data["sitemap"].append(groupArtistPathDestination + "/")

            ## Loop through releases
            for release in artist["releases"]:
                ## Output progress status
                print(utils.indent(release["name"], 3), file=sys.stderr)
                sys.stderr.flush()
                ## Resolve paths
                groupArtistReleasePathSource = os.path.join(
                    groupArtistPathSource,
                    release["name"],
                )
                groupArtistReleasePathDestination = os.path.join(
                    groupArtistPathDestination,
                    release["name"],
                )
                ## Generate link
                groupArtistReleasePathWebPageLink = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
                ## Create containing directory
                utils.mkdir(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["DestinationDirPath"],
                    groupArtistReleasePathDestination,
                )
                ## Render items list HTML
                listHtml = ""
                metaDescriptionLinks = []
                for recordingGroup in release["recordings"]:
                    recordingGroupLinks = []
                    for recording in recordingGroup:
                        link = utils.getWebPageLink(
                            recording["name"] + "/" if len(recording["name"]) > 0 else "",
                            recording["printable_name"],
                            data["definitions"]["link_types"]["recording"]
                        )
                        if "prefix" in recording:
                            link["prefix"] = recording["prefix"]
                        if "postfix" in recording:
                            link["postfix"] = recording["postfix"]
                        recordingGroupLinks.append(link)
                        metaDescriptionLinks.append(link)
                    listHtml += pystache.render(data["templates"]["list"], { "links": recordingGroupLinks })
                ## Render page HTML
                html = pystache.render(data["templates"]["page"], {
                    "title":       "Release “" + release["printable_name"] + "” by " + artist["printable_name"],
                    "description": utils.getDescriptionList(list(map(lambda link: link["label"], metaDescriptionLinks))),
                    "logo":        pystache.render(data["templates"]["link"], {
                        "href": "../../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                        "content": "Lyrics",
                    }),
                    "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth("", 3) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                    "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 4),
                    "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 4),
                    "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, dbPathWebPageLink, groupPathWebPageLink, groupArtistPathWebPageLink, groupArtistReleasePathWebPageLink),
                    "name":        "release",
                    "content":     listHtml,
                })
                ## Create index HTML file
                htmlFile = utils.mkfile(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["DestinationDirPath"],
                    groupArtistReleasePathDestination,
                    indexFileName,
                )
                ## Write rendered HTML into the index HTML file
                htmlFile.write(html)
                htmlFile.close()
                ## Add relative path to list of sitemap items
                if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                    data["sitemap"].append(groupArtistReleasePathDestination + "/")

                ## Loop through recordings
                for recordingGroup in release["recordings"]:
                    for recording in recordingGroup:
                        ## Skip empty (gap) items
                        if len(recording["name"]) == 0: continue
                        ## Output progress status
                        print(utils.indent(recording["name"], 4), file=sys.stderr)
                        sys.stderr.flush()
                        ## Resolve paths
                        groupArtistReleaseRecordingPathSource = os.path.join(
                            groupArtistReleasePathSource,
                            recording["name"],
                        )
                        groupArtistReleaseRecordingPathDestination = os.path.join(
                            groupArtistReleasePathDestination,
                            recording["name"],
                        )
                        ## Generate link
                        groupArtistReleaseRecordingPathWebPageLink = utils.getWebPageLink(recording["name"] + "/", recording["printable_name"], data["definitions"]["link_types"]["recording"])
                        ## Create containing directory
                        utils.mkdir(
                            data["definitions"]["runtime"]["cwd"],
                            data["config"]["Filesystem"]["DestinationDirPath"],
                            groupArtistReleaseRecordingPathDestination,
                        )
                        ## Add action buttons
                        lyricsActionsList = []
                        if data["config"].getboolean("Site", "HasEditTextButton"):
                            actionButton1 = pystache.render(data["templates"]["link"], {
                                "href": data["config"]["Source"]["Repository"]  + "/edit/" + \
                                        data["config"]["Source"]["DefaultBranch"]  + "/database/" + \
                                        groupKey + "/" + artistKey + "/" + release["name"] + "/" + recording["name"],
                                "content": "Suggest improvements for this text",
                            })
                            lyricsActionsList.append(actionButton1)
                        ## Render HTML
                        html = pystache.render(data["templates"]["page"], {
                            "title":       "Text of “" + recording["printable_name"] + "” by " + artist["printable_name"],
                            "description": utils.getDescriptionText(recording["text"]),
                            "logo":        pystache.render(data["templates"]["link"], {
                                "href": "../../../../.." if data["config"].getboolean("Site", "UseRelativePaths", fallback=False) else "/",
                                "content": "Lyrics",
                            }),
                            "navigation":  utils.generateTopBarNavigation(utils.giveLinkDepth("", 4) if data["config"].getboolean("Site", "UseRelativePaths") else "/" + data["config"]["Site"]["DbPath"] + "/"),
                            "css":         utils.giveLinkDepth(data["definitions"]["filenames"]["css"], 5),
                            "search":      utils.giveLinkDepth(data["definitions"]["filenames"]["search"], 5),
                            "breadcrumbs": utils.getBreadcrumbs(data["templates"], homePathWebPageLink, dbPathWebPageLink, groupPathWebPageLink, groupArtistPathWebPageLink, groupArtistReleasePathWebPageLink, groupArtistReleaseRecordingPathWebPageLink),
                            "name":        "recording",
                            "content":     utils.formatLyricsAndMetadata(data["templates"], recording["text"], recording["metadata"], lyricsActionsList),
                        })
                        ## Create index HTML file
                        htmlFile = utils.mkfile(
                            data["definitions"]["runtime"]["cwd"],
                            data["config"]["Filesystem"]["DestinationDirPath"],
                            groupArtistReleaseRecordingPathDestination,
                            indexFileName,
                        )
                        ## Write rendered HTML into the index HTML file
                        htmlFile.write(html)
                        htmlFile.close()
                        ## Add relative path to list of sitemap items
                        if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
                            data["sitemap"].append(groupArtistReleaseRecordingPathDestination + "/")
