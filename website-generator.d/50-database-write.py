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
    ## Generate breadcrumbs link to this page
    dbPathWebPageLink = utils.getWebPageLink(data["config"]["Site"]["DbPath"] + "/", "Database")
    ## Render HTML
    groups = [
        ## Numbers
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ## Latin
        ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        ## Japanese (Hiragana)
        ["あ", "け", "す", "た", "ぶ", "も"],  ## TODO: complete this to include all of Hiragana syllabary
        ## Punjabi (Gurmukhi)
        ["ੳ", "ਅ", "ੲ", "ਸ", "ਹ", "ਕ", "ਖ", "ਗ", "ਘ", "ਙ", "ਚ", "ਛ", "ਜ", "ਝ", "ਞ", "ਟ", "ਠ", "ਡ", "ਢ", "ਣ", "ਤ", "ਥ", "ਦ", "ਧ", "ਨ", "ਪ", "ਫ", "ਬ", "ਭ", "ਮ", "ਯ", "ਰ", "ਲ", "ਵ", "ੜ", "ਸ਼", "ਖ਼", "ਗ਼", "ਜ਼", "ਫ਼", "ਲ਼"],
        ## Everything else (misfits)
        [],
    ]
    databaseLinkList = list(map(lambda x: [], groups))
    for letterGroupKey in data["database"]:
        link = utils.getWebPageLink(letterGroupKey + "/", letterGroupKey, data["definitions"]["link_types"]["group"])
        for i, group in enumerate(groups):
            if letterGroupKey in group:
                databaseLinkList[i].append(link)
                break
        else:
            databaseLinkList[-1].append(link)
    for i in databaseLinkList[:]:
        if len(i) < 1:
            databaseLinkList.remove(i)
    content = map(lambda groupedDatabaseLinkList: pystache.render(data["templates"]["list"], {
        "class": "g",
        "links": groupedDatabaseLinkList,
    }), databaseLinkList)
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
        "content":     "".join(filter(lambda subset: len(subset) > 0, content)),
    })
    ## Create containing directory
    utils.mkdir(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["config"]["Site"]["DbPath"],
    )
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

    ## Loop through letter groups (e.g. "X")
    for letterGroupKey in data["database"]:
        ## Output progress status
        print(utils.indent(letterGroupKey, 1), file=sys.stderr)
        sys.stderr.flush()
        ## Assign variables
        group = data["database"][letterGroupKey]
        ## Resolve paths
        groupPathSource = os.path.join(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["SourcePath"],
            letterGroupKey,
        )
        groupPathDestination = os.path.join(
            data["config"]["Site"]["DbPath"],
            letterGroupKey,
        )
        ## Generate breadcrumbs link to this page
        groupPathWebPageLink = utils.getWebPageLink(letterGroupKey + "/", letterGroupKey)
        ## Render HTML
        pageLinks = []
        for artistKey in group:
            link = utils.getWebPageLink(artistKey + "/", group[artistKey]["printable_name"], data["definitions"]["link_types"]["artist"])
            pageLinks.append(link)
        listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
        html = pystache.render(data["templates"]["page"], {
            "title":       "Artists starting with “" + letterGroupKey + "”",
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
        ## Create containing directory
        utils.mkdir(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            groupPathDestination,
        )
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

        ## Loop through artists that are part of the letter group "X"
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
            ## Generate breadcrumbs link to this page
            groupArtistPathWebPageLink = utils.getWebPageLink(artistKey + "/", artist["printable_name"], data["definitions"]["link_types"]["artist"])
            ## Render items list HTML
            pageLinks = []
            for release in artist["releases"]:
                link = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
                if "year" in release:
                    link["postfix"] = "(" + str(release["year"]) + ")"
                pageLinks.append(link)
            listHtml = pystache.render(data["templates"]["list"], { "links": pageLinks })
            ## Render HTML
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
            ## Create containing directory
            utils.mkdir(
                data["definitions"]["runtime"]["cwd"],
                data["config"]["Filesystem"]["DestinationDirPath"],
                groupArtistPathDestination,
            )
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
                ## Generate breadcrumbs link to this page
                groupArtistReleasePathWebPageLink = utils.getWebPageLink(release["name"] + "/", release["printable_name"], data["definitions"]["link_types"]["release"])
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
                ## Render HTML
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
                ## Create containing directory
                utils.mkdir(
                    data["definitions"]["runtime"]["cwd"],
                    data["config"]["Filesystem"]["DestinationDirPath"],
                    groupArtistReleasePathDestination,
                )
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
                        ## Generate breadcrumbs link to this page
                        groupArtistReleaseRecordingPathWebPageLink = utils.getWebPageLink(recording["name"] + "/", recording["printable_name"], data["definitions"]["link_types"]["recording"])
                        ## Add action buttons
                        lyricsActionsList = []
                        if data["config"].getboolean("Site", "HasEditTextButton"):
                            actionButton1 = pystache.render(data["templates"]["link"], {
                                "href": data["config"]["Source"]["Repository"]  + "/edit/" + \
                                        data["config"]["Source"]["DefaultBranch"]  + "/database/" + \
                                        letterGroupKey + "/" + artistKey + "/" + release["name"] + "/" + recording["name"],
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
                        ## Create containing directory
                        utils.mkdir(
                            data["definitions"]["runtime"]["cwd"],
                            data["config"]["Filesystem"]["DestinationDirPath"],
                            groupArtistReleaseRecordingPathDestination,
                        )
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
