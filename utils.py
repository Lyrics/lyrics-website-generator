import os
import re
import sys
from urllib.parse import quote
from urllib.parse import urljoin

import pystache

def fillTheGaps(definitions, recordings):
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
                recordings.append(getWebPageLink("", "", definitions["link_types"]["recording"]))
                recordings[-1]["track_no"] = prevTrackNoStr
                recordings[-1]["name"] = ""
                recordings[-1]["printable_name"] = ""
                existingTrackNumbers.append(prevTrackNoStr)

def formatLyricsAndMetadata(templates, lyricsText, lyricsMetadataDict, lyricsActionsList):
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

def formatRecordingNumber(recording):
    if "track_no" in recording:
        # Add padding to make record numbers appear aligned within text browsers
        leftPadding = ""
        trackNoAsStr = str(recording["track_no"])
        if len(trackNoAsStr) < 2:
            leftPadding = "&nbsp;"
        recording["prefix"] = leftPadding + trackNoAsStr + "."

def getBreadcrumbs(templates, *links):
    items = []
    depth = 0
    for link in links:
        depth += 1
        items.append({ "href": link["href"], "label": link["label"], "type": link["type"] })
        ## Change relative paths to dot-paths based on their level
        if link["href"].endswith("/"):
            if depth == len(links):
                items[-1]["href"] = "."
            else:
                items[-1]["href"] = "/".join([".."] * (len(links) - depth))
                ## Put empty items between links (for arrows)
                items.append(None)
    return pystache.render(templates["breadcrumbs"], {
        "breadcrumbs": items,
    })

def getDescriptionList(items):
    return ", ".join(list(filter(lambda item: len(item) > 0, items))[:24])

def getDescriptionText(text):
    text = re.sub("\n+", " / ", text)
    text = re.sub(" +", " ", text)
    text = text[:220]
    return text.strip()

def getMetadata(lyricsFileContents):
    partials = splitLyricsIntoTextAndMetadata(lyricsFileContents)
    lyricsMetadata = ""
    if len(partials) > 1:
        lyricsMetadata = partials[1]
        ## Trim metadata
        lyricsMetadata = lyricsMetadata.strip()
    return lyricsMetadata

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

def getWebPageLink(target, label, type=0):
    return {
        "href": quote(target),
        "label": label,
        "type": type,
    }

def indent(what="", amount=0):
    indentation = ""
    if amount > 0:
        indentation = "│ " * (amount - 1)
        indentation += "├─" # └
    return indentation + what

def mkdir(*paths):
    os.makedirs(os.path.join(*paths), exist_ok=True)

def mkfile(*paths):
    return open(os.path.join(*paths), "w")

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

def resolveURL(base, url):
    return urljoin(base, quote(url), allow_fragments=False)

## Sorting function for lists of recordings
def sortRecordingsByTrackNumber(link, key="track_no"):
    if key in link:
        ## Sort recordings by number
        return int(link[key])
    else:
        return sys.maxsize ## Push recordings without number to the bottom

## Alphabetical sorting function for lists of recordings (LPs, cassettes)
def sortRecordingsByTrackLetter(link, key="track_no"):
    if key in link:
        ## Sort recordings by letter
        return link[key]
    else:
        return "Z" ## Push recordings without letter to the bottom

## Sorting function for release lists
def sortReleasesByYear123(link, key="year"):
    if key in link:
        ## Sort releases by year
        return int(link[key])
    else:
        ## Push releases without year to the bottom
        return sys.maxsize

def splitLyricsIntoTextAndMetadata(lyricsFileContents):
    return re.split("_+", lyricsFileContents)
