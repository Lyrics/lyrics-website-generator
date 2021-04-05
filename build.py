#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import configparser
import pystache
from itertools import chain
from urllib.parse import quote

scriptPath = os.path.dirname(os.path.realpath(__file__))
configFile = os.path.join(scriptPath, "config.ini")
templatesPath = os.path.join(scriptPath, "src", "templates")

## Config
config = configparser.ConfigParser()
if os.path.isfile(configFile):
    config.read(configFile)
else:
    print("Error: config.ini does not exist")
    exit()
config["Filesystem"]["SourcePath"] = os.path.join(scriptPath, config["Filesystem"]["SourcePath"])

## File names
indexFileName    = "index.html"
notFoundFileName = "404.html"
searchFileName   = "s.htm"
sitemapFileName  = "sitemap.xml"

## Breadcrumb and list item link types
TYPE_LETTER    = 1
TYPE_ARTIST    = 2
TYPE_ALBUM     = 3
TYPE_RECORDING = 4

## Function for optimizing templates" code
def shrinkwrapTemplate(markup):
    return re.sub(r"\n\s*", "", markup)

## Function for reading and optimizing templates" code
def getTemplateContents(templateFileName):
    return shrinkwrapTemplate(open(os.path.join(templatesPath, templateFileName), "r").read())

def getSafePath(input):
    return input

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def mkfile(where="", filename=indexFileName):
    return open(os.path.join(where, filename), "w")

def getLink(target, label, type=0):
    return { "href": quote(target), "label": label, "type": type }

def getSitemapURL(target=""):
    URL = config["Site"]["URL"] + "/" + quote(target)
    if target:
        URL += "/"
    return URL

def getBreadcrumbs(*links):
    items = []
    depth = 0
    for link in links:
        depth += 1
        items.append({ "href": link["href"], "label": link["label"], "type": depth })
        # Change relative paths to dot-paths based on their level
        if depth == len(links):
            items[-1]["href"] = "."
        else:
            items[-1]["href"] = "/".join([".."] * (len(links) - depth))
            # Put empty items between links (for arrows)
            items.append(None)
    return pystache.render(templates["breadcrumbs"], {
        "breadcrumbs": items,
    })

def splitLyricsIntoTextAndMetadata(lyricsFileContents):
    return re.split("_+", lyricsFileContents)

def getText(lyricsFileContents):
    partials = splitLyricsIntoTextAndMetadata(lyricsFileContents)
    lyricsText = ""
    if len(partials) > 1:
        lyricsText = partials[0]
    else:
        lyricsText = lyricsFileContents
    ## Trim text
    lyricsText = lyricsText.strip()
    ## Add newlines at end of text (unless it’s empty)
    if lyricsText != "":
        lyricsText += "\n\n"
    return lyricsText

def getMetadata(lyricsFileContents):
    partials = splitLyricsIntoTextAndMetadata(lyricsFileContents)
    lyricsMetadata = ""
    if len(partials) > 1:
        lyricsMetadata = partials[1]
        ## Trim metadata
        lyricsMetadata = lyricsMetadata.strip()
    return lyricsMetadata

def getDescriptionList(items):
    return ", ".join(items[:24])

def getDescriptionText(text):
    text = re.sub("\n+", " / ", text)
    text = re.sub(" +", " ", text)
    text = text[:220]
    return text.strip()

def parseMetadata(metadata):
    datalines = []
    for line in metadata.splitlines():
      line = line.rstrip() ## Discard trailing whitespaces
      if line[0] == " ":
        if len(datalines) == 0:
          print("Warning: metadata keys cannot begin with a space")
        else:
          ## The value is split between multiple lines,
          ## append this line to the previous one
          datalines[-1] += line
      else:
        datalines.append(line)
    dictionary = {}
    for dataline in datalines:
        partials = re.split("\s{2,}", dataline)
        key = partials[0]
        rawvalue = dataline[len(key):].strip()
        valuepartials = re.split(",\s{2,}", rawvalue)
        dictionary[key] = valuepartials
    return dictionary

def formatLyricsAndMetadata(lyricsText, lyricsMetadataDict, lyricsActionsList):
    ## Separate text into paragraphs
    lyricsHtml = re.sub("\n\n+", "<br/><span></span><br/><span></span>", lyricsText)
    ## Convert newline characters into linebreaks
    lyricsHtml = re.sub("\n", "\n<br/><span></span>", lyricsHtml)

    ## Proccess metadata keys and values
    metadataHtml = None
    if len(lyricsMetadataDict) > 0:
        items = []
        for key, value in lyricsMetadataDict.items():
            items.append({
                "key":   key,
                "value": ",  ".join(value)
            })
            ## Post-process metadata keys and values
            if key == "Name":
                items[-1]["key"] = "Song name"
            if key == "Track no":
                items[-1]["key"] = "Track number"
            if key == "MusicBrainz ID":
                items[-1]["value"] = pystache.render(templates["link"], {
                    "href":    "https://musicbrainz.org/recording/" + value[0],
                    "content": value[0],
                })
        metadataHtml = pystache.render(templates["lyrics-metadata"], items)

    ## Process action buttons
    actionsHtml = None
    if len(lyricsActionsList) > 0:
        actionsHtml = "<br />".join(lyricsActionsList)

    html = pystache.render(templates["lyrics-container"], {
        "lyrics":   lyricsHtml,
        "metadata": metadataHtml,
        "actions":  actionsHtml,
    })
    return html

## Sorting function for album lists
def sortAlbumsYear123(link, key="year"):
    if key in link:
        ## Sort albums by year
        return int(link[key])
    else:
        return 3000 ## Push albums without year to the bottom

## Sorting function for lists of recordings
def sortRecordingsByTrackNumber(link, key="track_no"):
    if key in link:
        ## Sort recordings by number
        return int(link[key])
    else:
        return 1000 ## Push recordings without number to the bottom

## Alphabetical sorting function for lists of recordings (LPs, cassettes)
def sortRecordingsByTrackLetter(link, key="track_no"):
    if key in link:
        ## Sort recordings by letter
        return link[key]
    else:
        return "Z" ## Push recordings without letter to the bottom

def formatAlbumYear(a):
    if "year" in a:
        a["postfix"] = "(" + str(a["year"]) + ")"
    return a

def formatRecordingNumber(recording):
    if "track_no" in recording:
        # Add padding to make record numbers appear aligned within text browsers
        leftPadding = ""
        trackNoAsStr = str(recording["track_no"])
        if len(trackNoAsStr) < 2:
            leftPadding = "&nbsp;"
        recording["prefix"] = leftPadding + trackNoAsStr + "."
    return recording

def fillTheGaps(recordings):
    existingTrackNumbers = []
    for recording in recordings:
        if "track_no" in recording: existingTrackNumbers.append(recording["track_no"])
    for recording in recordings:
        if "track_no" in recording:
            if recording["track_no"].isdecimal():
                sideLetter = ""
                trackNo = int(recording["track_no"])
            else:
                sideLetter = recording["track_no"][0]
                if len(recording["track_no"]) > 1:
                    trackNo = int(recording["track_no"][1:])
                else:
                    trackNo = 0
            def missingFilter(r):
                if trackNo == 0:
                    return False
                prevTrackNo = trackNo - 1
                return prevTrackNo > 0 and not sideLetter + str(prevTrackNo) in existingTrackNumbers
            while len(list(filter(missingFilter, recordings))) > 0:
                prevTrackNoStr = sideLetter + str(trackNo - 1)
                recordings.append(getLink("", "", TYPE_RECORDING))
                recordings[-1]["track_no"] = prevTrackNoStr
                existingTrackNumbers.append(prevTrackNoStr)
    return recordings

# Builds list of recording names out of 2D array of discs
def flattenRecordingsLists(recordingsLists):
    flattened = chain.from_iterable(recordingsLists)
    filtered = list(filter(lambda link: len(link["label"]) > 0, flattened))
    namesOnly = list(map(lambda link: link["label"], filtered))
    return namesOnly

## Read and store template files
templates = {}
templatesFileNames = next(os.walk(templatesPath))[2]
for templateFileName in templatesFileNames:
    (templateName, _) = os.path.splitext(templateFileName)
    templates[templateName] = getTemplateContents(templateFileName)

###################################
#  The build process starts here  #
###################################

## Create directories to accommodate website database path
mkdir(config["Site"]["DbPath"])

## A-Z letter lihks for top navigation
abc = []
for letter in list(map(chr, range(ord("A"), ord("Z")+1))):
    abc.append(getLink("/" + config["Site"]["DbPath"] + "/" + letter, letter))

## List of URLs to be added to the sitemap file
sitemapURLs = []

## List of top-level directory names
dbLetters = []

## 1. Loop through letters in the database
for letter in sorted(next(os.walk(config["Filesystem"]["SourcePath"]))[1]):
    ## Output progress status
    print(letter, end=" ", file=sys.stderr)
    sys.stderr.flush()

    dbLetters.append(letter)

    letterPath = os.path.join(config["Filesystem"]["SourcePath"], letter)
    safeLetterPath = getSafePath(os.path.join(config["Site"]["DbPath"], letter))
    letterLink = getLink(getSafePath(letter), letter)
    sitemapURLs.append(getSitemapURL(safeLetterPath))
    ## Create db/x/
    mkdir(safeLetterPath)
    ## Create db/x/index.html
    letterHtmlFile = mkfile(safeLetterPath)
    artists = sorted(next(os.walk(letterPath))[1], key=str.lower)
    artistList = []

    ## 2. Loop through artists starting with letter x
    for artist in artists:
        artistPath = os.path.join(letterPath, artist)
        safeArtistPath = getSafePath(os.path.join(config["Site"]["DbPath"], letter, artist))
        sitemapURLs.append(getSitemapURL(safeArtistPath))
        ## Create db/x/artist/
        mkdir(safeArtistPath)
        ## Create db/x/artist/index.html
        artistHtmlFile = mkfile(safeArtistPath)
        ## Append artist link to db/x/index.html
        artistList.append(getLink(getSafePath(artist), artist, TYPE_ARTIST))
        albums = sorted(next(os.walk(artistPath))[1], key=str.lower)
        albumList = []

        ## 3. Loop through artist’s albums
        for album in albums:
            albumPath = os.path.join(artistPath, album)
            safeAlbumPath = getSafePath(os.path.join(config["Site"]["DbPath"], letter, artist, album))
            sitemapURLs.append(getSitemapURL(safeAlbumPath))
            ## Create db/x/artist/album/
            mkdir(safeAlbumPath)
            ## Create db/x/artist/album/index.html
            albumHtmlFile = mkfile(safeAlbumPath)
            ## Append album link to db/x/artist/index.html
            albumList.append(getLink(getSafePath(album), album, TYPE_ALBUM))
            recordings = sorted(next(os.walk(albumPath))[2], key=str.lower)
            recordingsLists = [[]] # One list per disc

            ## 4. Loop through songs
            for recording in recordings:
                recordingPath = os.path.join(albumPath, recording)
                if not os.path.isfile(recordingPath):
                    print("Warning: " + recordingPath + " is not a file!")
                else:
                    safeRecordingPath = getSafePath(os.path.join(config["Site"]["DbPath"], letter, artist, album, recording))
                    sitemapURLs.append(getSitemapURL(safeRecordingPath))
                    ## Create db/x/artist/album/song/
                    mkdir(safeRecordingPath)
                    ## Create db/x/artist/album/song/index.html
                    recordingHtmlFile = mkfile(safeRecordingPath)
                    ## Read lyrics file
                    lyricsFileContents = open(recordingPath, "r").read().strip()
                    lyricsText = getText(lyricsFileContents)
                    lyricsMetadata = getMetadata(lyricsFileContents)
                    lyricsMetadataDictionary = parseMetadata(lyricsMetadata)
                    ## Determine disc number
                    discNo = int(lyricsMetadataDictionary["Disc no"][0]) if "Disc no" in lyricsMetadataDictionary else 0
                    ## Make sure there’s an array for this disc
                    while len(recordingsLists) <= discNo:
                        recordingsLists.append([])
                    ## Append recording link to db/x/artist/album/index.html
                    recordingsLists[discNo].append(getLink(getSafePath(recording), recording, TYPE_RECORDING))
                    ## Make use of any available metadata values
                    if "Name" in lyricsMetadataDictionary:
                        recordingsLists[discNo][-1]["label"] = lyricsMetadataDictionary["Name"][0]
                    if "Artist" in lyricsMetadataDictionary:
                        artistList[-1]["label"] = lyricsMetadataDictionary["Artist"][0]
                    if "Album" in lyricsMetadataDictionary:
                        albumList[-1]["label"] = lyricsMetadataDictionary["Album"][0]
                    if "Track no" in lyricsMetadataDictionary:
                        recordingsLists[discNo][-1]["track_no"] = lyricsMetadataDictionary["Track no"][0]
                    if "Disc no" in lyricsMetadataDictionary:
                        recordingsLists[discNo][-1]["disc_no"] = lyricsMetadataDictionary["Disc no"][0]
                    if "Year" in lyricsMetadataDictionary:
                        albumList[-1]["year"] = lyricsMetadataDictionary["Year"][0]
                    ## Add action buttons
                    lyricsActionsList = []
                    if config["Site"]["HasEditTextButton"]:
                        actionButton1 = pystache.render(templates["link"], {
                            "href": config["Source"]["Repository"]  + "/edit/" + \
                                    config["Source"]["DefaultBranch"]  + "/database/" + \
                                    letter + "/" + artist + "/" + album + "/" + recording,
                            "content": "Suggest improvements for this text",
                        })
                        lyricsActionsList.append(actionButton1)
                    ## Mark instrumental texts within parent page’s (album) list
                    if len(lyricsText) == 0:
                        recordingsLists[discNo][-1]["postfix"] = config["Site"]["InstrumentalLabel"]
                    ## Render and write song page contents
                    html = pystache.render(templates["page"], {
                        "title":       artistList[-1]["label"] + " – " + recordingsLists[discNo][-1]["label"],
                        "description": getDescriptionText(lyricsText),
                        "navigation":  abc,
                        "breadcrumbs": getBreadcrumbs(letterLink, artistList[-1], albumList[-1], recordingsLists[discNo][-1]),
                        "name":        "recording",
                        "content":     formatLyricsAndMetadata(lyricsText, lyricsMetadataDictionary, lyricsActionsList),
                        "search":      searchFileName,
                    })
                    recordingHtmlFile.write(html)
                    recordingHtmlFile.close()

            ## Make disc-less items appear after discs (on the bottom)
            if len(recordingsLists) > 1:
                recordingsLists.append(recordingsLists.pop(0))
            ## Render lists of recordings
            recordingsListHtml = ""
            for recordingsList in recordingsLists:
                ## Skip if empty
                if len(recordingsList) < 1: continue
                ## Fill missing tracks with empty gaps
                recordingsList = fillTheGaps(recordingsList)
                # Determine if tracks bear alphabetic or decimal enumeration
                isOrderDecimal = False
                for recording in recordingsList:
                    if "track_no" in recording and recording["track_no"].isdecimal():
                        isOrderDecimal = True
                        break
                ## Sort recording list within the album by track number/letter
                if isOrderDecimal:
                    # By number, for CDs and WEB releases
                    recordingsList.sort(key=sortRecordingsByTrackNumber)
                else:
                    # By letter (or letter + number, e.g. A, B1, B2), for LPs and cassette tapes
                    recordingsList.sort(key=sortRecordingsByTrackLetter)
                ## Format song number/letter labels
                recordingsList = list(map(formatRecordingNumber, recordingsList))
                # Render list of recordings
                recordingsListHtml += pystache.render(templates["list"], {"links": recordingsList})
            ## Render and write album page contents
            html = pystache.render(templates["page"], {
                "title":       "Album “" + albumList[-1]["label"] + "” by " + artistList[-1]["label"],
                "description": getDescriptionList(flattenRecordingsLists(recordingsLists)),
                "navigation":  abc,
                "breadcrumbs": getBreadcrumbs(letterLink, artistList[-1], albumList[-1]),
                "name":        "album",
                "content":     recordingsListHtml,
                "search":      searchFileName,
            })
            albumHtmlFile.write(html)
            albumHtmlFile.close()

        ## Sort albums by year
        albumList.sort(key=sortAlbumsYear123)
        ## Wrap album years in parens
        albumList = list(map(formatAlbumYear, albumList))
        ## Render list of albums
        albumsListHtml = pystache.render(templates["list"], {"links": albumList})
        ## Render and write artist page contents
        html = pystache.render(templates["page"], {
            "title":       "Albums by " + artistList[-1]["label"],
            "description": getDescriptionList(list(map(lambda link: link["label"], albumList))),
            "navigation":  abc,
            "breadcrumbs": getBreadcrumbs(letterLink, artistList[-1]),
            "name":        "artist",
            "content":     albumsListHtml,
            "search":      searchFileName,
        })
        artistHtmlFile.write(html)
        artistHtmlFile.close()

    ## Render list of artist
    artistsListHtml = pystache.render(templates["list"], {"links": artistList})
    ## Render and write letter page contents
    html = pystache.render(templates["page"], {
        "title":       "Artists starting with " + letter,
        "description": getDescriptionList(artists),
        "navigation":  abc,
        "breadcrumbs": getBreadcrumbs(letterLink),
        "name":        "letter",
        "content":     artistsListHtml,
        "search":      searchFileName,
    })
    letterHtmlFile.write(html)
    letterHtmlFile.close()

## Create homepage index file
html = pystache.render(templates["page"], {
    "title":       config["Site"]["Name"],
    "description": "Web interface to Open Lyrics Database",
    "navigation":  abc,
    "name":        "home",
    "content":     pystache.render(templates["home-page-contents"], {
        "db": config["Site"]["DbPath"],
    }),
    "search":      searchFileName,
})
homepageFile = mkfile()
homepageFile.write(html)
homepageFile.close()

## Create DB root index file
html = pystache.render(templates["page"], {
    "title":       config["Site"]["Name"],
    "description": "Index of top-level database directories",
    "navigation":  abc,
    "name":        "db",
    "content":     pystache.render(templates["db-page-contents"], {"letters": dbLetters}),
    "search":      searchFileName,
})
homepageFile = mkfile(config["Site"]["DbPath"])
homepageFile.write(html)
homepageFile.close()

## Create 404 page
html = pystache.render(templates["page"], {
    "title":       "Page not found",
    "description": "Error 404: page not found",
    "navigation":  abc,
    "name":        "error",
    "content":     pystache.render(templates["not-found-page-contents"]),
    "search":      searchFileName,
})
notFoundFile = mkfile("", notFoundFileName)
notFoundFile.write(html)
notFoundFile.close()

## Create search page
html = pystache.render(templates["page"], {
    "title":       "Search",
    "description": "Find lyrics using GitHub’s code search engine",
    "navigation":  abc,
    "name":        "search",
    "content":     pystache.render(templates["search-page-contents"]),
    "search":      searchFileName,
})
searchFile = mkfile("", searchFileName)
searchFile.write(html)
searchFile.close()

## Add homepage URL to the sitemap
sitemapURLs.append(getSitemapURL())

## Add DB root URL to the sitemap
sitemapURLs.append(getSitemapURL(config["Site"]["DbPath"]))

## Write the sitemap file
sitemapFile = mkfile("", sitemapFileName)
xml = pystache.render(templates["sitemap"], {"links": sitemapURLs})
sitemapFile.write(xml)
sitemapFile.close()

#################################
#  The build process ends here  #
#################################

## Put newline after the A B C ... Z output
print(file=sys.stderr)
