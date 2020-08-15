#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import pystache
from urllib.parse import quote

## Config
siteName          = 'Lyrics'
siteURL           = 'https://lyrics.github.io'
destDatabaseDir   = 'db'
sourceDatabaseDir = os.path.join('..', '..', 'lyrics.git', 'database')
templatesPath     = os.path.join('..', 'src', 'templates')

## File names
indexFileName    = 'index.html'
notFoundFileName = '404.html'
searchFileName   = 'search.html'
sitemapFileName  = 'sitemap.xml'

## Function for optimizing templates' code
def shrinkwrapTemplate(code):
    return re.sub(r'\n\s*', '', code)

## Function for reading and optimizing templates' code
def getTemplateContents(templateFileName):
    return shrinkwrapTemplate(open(os.path.join(templatesPath, templateFileName), 'r').read())

## Read and store template files
templates = {}
templatesFileNames = next(os.walk(templatesPath))[2]
for templateFileName in templatesFileNames:
    (templateName, _) = os.path.splitext(templateFileName)
    templates[templateName] = getTemplateContents(templateFileName)

## Dictionary of letters (used for navigating the website)
abc = []
for letter in list(map(chr, range(ord('A'), ord('Z')+1))):
    abc.append({ 'path': '/' + destDatabaseDir + '/' + letter, 'label': letter })

## List of URLs to be added to the sitemap file
sitemapURLs = []

def getSafePath(input):
    return input

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def mkfile(where='', filename=indexFileName):
    return open(os.path.join(where, filename), 'w')

def getLink(target, text, depth):
    return { 'link': '/' + quote(target) + '/', 'label': text, 'type': depth }

def getSitemapURL(target=''):
    URL = siteURL + '/' + quote(target)
    if target:
        URL += '/'
    return URL

def getBreadcrumbs(*links):
    items = []
    depth = 0
    for link in links:
        items.append(link)
        depth += 1
        if depth < len(links):
            items.append(None)
    return pystache.render(templates['breadcrumbs'], {
        'breadcrumbs': items,
    })

def splitLyricsIntoTextAndMetadata(lyricsFileContents):
    return re.split('_+', lyricsFileContents)

def getText(lyricsFileContents):
    partials = splitLyricsIntoTextAndMetadata(lyricsFileContents)
    lyricsText = ""
    if len(partials) > 1:
        lyricsText = partials[0]
    else:
        lyricsText = lyricsFileContents
    ## Trim text
    lyricsText = lyricsText.strip()
    ## Add newline at end of text (unless it's empty)
    if lyricsText != "":
        lyricsText += "\n"
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
    return ', '.join(items[:24])

def getDescriptionText(text):
    text = re.sub('\n+', ' / ', text)
    text = re.sub(' +', ' ', text)
    text = text[:220]
    return text.strip()

def parseMetadata(metadata):
    datalines = []
    for line in metadata.splitlines():
      line = line.rstrip() ## Discard trailing whitespaces
      if line[0] == ' ':
        if len(datalines) == 0:
          print('LMML parsing error: keys cannot begin with a space')
        else:
          ## The value is split between multiple lines,
          ## append this line to the previous one
          datalines[-1] += line
      else:
        datalines.append(line)
    dictionary = {}
    for dataline in datalines:
      partials = re.split('\s{2,}', dataline)
      key = partials[0]
      rawvalue = dataline[len(key):].strip()
      valuepartials = re.split(',\s{2,}', rawvalue)
      dictionary[key] = valuepartials
    return dictionary

def formatLyricsAndMetadata(lyricsText, lyricsMetadata):
    ## Separate text into paragraphs
    lyricsText = re.sub('\n\n+', '<span><br/></span><span class="g"><br/></span>', lyricsText)
    ## Convert newline characters into linebreaks
    lyricsText = re.sub('\n', '<span><br/></span>', lyricsText)
    html = ''
    ## Add margin for cli browsers
    html += '<br/>'
    ## Construct HTML
    html += '<div id="lyrics">'
    html += lyricsText
    html += '<br/><br/>'
    if lyricsMetadata:
        lyricsMetadata = re.sub('\n', '<br/>', lyricsMetadata)
        html += '<hr/>'
        html += '<p>' + lyricsMetadata + '</p>'
    html += '</div>'
    return html

## Sorting function for album and song lists
def sortListItems123(link):
    if 'id' in link:
        ## Sort albums by year, songs by number
        return int(link['id'])
    else:
        return 3000 ## Push albums without year or songs without number to the bottom

## Alphabetical sorting function for song lists (LPs, cassettes)
def sortListItemsABC(link):
    if 'id' in link:
        ## Sort songs by letter
        return link['id']
    else:
        return 'Z' ## Push songs without letter to the bottom

def formatAlbumYear(a):
    if 'id' in a:
        a['id'] = '(' + str(a['id']) + ')'
    return a

def formatSongNumber(s):
    if 'id' in s:
        s['id'] = '' + str(s['id']) + '.'
    return s

###################################
#                                 #
#  The build process starts here  #
#                                 #
###################################

## 0. Create the root index file
html = pystache.render(templates['layout'], {
    'title': siteName,
    'description': "Web interface to the lyrics database hosted on GitHub",
    'navigation': abc,
    'content': pystache.render(templates['home'])
})
homepageFile = mkfile()
homepageFile.write(html)
homepageFile.close()

## Create the 404 page
html = pystache.render(templates['layout'], {
    'title': "Page not found" + " | " + siteName,
    'description': "Error 404: page not found",
    'navigation': abc,
    'content': pystache.render(templates['404'])
})
notFoundFile = mkfile('', notFoundFileName)
notFoundFile.write(html)
notFoundFile.close()

## Create the search page
html = pystache.render(templates['layout'], {
    'title': "Search" + " | " + siteName,
    'description': "Find lyrics using GitHub's code search engine",
    'navigation': abc,
    'content': pystache.render(templates['search'])
})
searchFile = mkfile('', searchFileName)
searchFile.write(html)
searchFile.close()

## Add root URL to the list of sitemap links
sitemapURLs.append(getSitemapURL())

## 1. Loop through letters in the database
## for letter in sorted(os.listdir(sourceDatabaseDir)):
for letter in sorted(next(os.walk(sourceDatabaseDir))[1]):
    ## Output progress status
    print(letter, end=" ", file=sys.stderr)
    sys.stderr.flush()

    letterPath = os.path.join(sourceDatabaseDir, letter)
    safeLetterPath = getSafePath(os.path.join(destDatabaseDir, letter))
    letterLink = getLink(safeLetterPath, letter, 0)
    sitemapURLs.append(getSitemapURL(safeLetterPath))
    ## Create db/x/
    mkdir(safeLetterPath)
    ## Create db/x/index.html
    letterPathFile = mkfile(safeLetterPath)
    artists = sorted(next(os.walk(letterPath))[1], key=str.lower)
    artistList = []

    ## 2. Loop through artists starting with letter x
    for artist in artists:
        artistPath = os.path.join(letterPath, artist)
        safeArtistPath = getSafePath(os.path.join(destDatabaseDir, letter, artist))
        sitemapURLs.append(getSitemapURL(safeArtistPath))
        ## Create db/x/artist/
        mkdir(safeArtistPath)
        ## Create db/x/artist/index.html
        artistPathFile = mkfile(safeArtistPath)
        ## Append artist link to db/x/index.html
        artistList.append(getLink(safeArtistPath, artist, 1))
        albums = sorted(next(os.walk(artistPath))[1], key=str.lower)
        albumList = []

        ## 3. Loop through artist's albums
        for album in albums:
            albumPath = os.path.join(artistPath, album)
            safeAlbumPath = getSafePath(os.path.join(destDatabaseDir, letter, artist, album))
            sitemapURLs.append(getSitemapURL(safeAlbumPath))
            ## Create db/x/artist/album/
            mkdir(safeAlbumPath)
            ## Create db/x/artist/album/index.html
            albumPathFile = mkfile(safeAlbumPath)
            ## Append album link to db/x/artist/index.html
            albumList.append(getLink(safeAlbumPath, album, 2))
            songs = sorted(next(os.walk(albumPath))[2], key=str.lower)
            songList = []

            ## 4. Loop through songs
            for song in songs:
                songPath = os.path.join(albumPath, song)
                if not os.path.isfile(songPath):
                    print(songPath + " is not a file! 0x04")
                else:
                    safeSongPath = getSafePath(os.path.join(destDatabaseDir, letter, artist, album, song))
                    sitemapURLs.append(getSitemapURL(safeSongPath))
                    ## Create db/x/artist/album/song/
                    mkdir(safeSongPath)
                    ## Create db/x/artist/album/song/index.html
                    songPathFile = mkfile(safeSongPath)
                    ## Append song link to db/x/artist/album/index.html
                    songList.append(getLink(safeSongPath, song, 3))
                    ## Read the lyrics file
                    lyricsFileContents = open(songPath, 'r').read().strip()
                    lyricsText = getText(lyricsFileContents)
                    lyricsMetadata = getMetadata(lyricsFileContents)
                    lyricsMetadataDictionary = parseMetadata(lyricsMetadata)
                    ## Make use of any available metadata values
                    if 'Name' in lyricsMetadataDictionary:
                        songList[-1]['label'] = lyricsMetadataDictionary['Name'][0]
                    if 'Artist' in lyricsMetadataDictionary:
                        artistList[-1]['label'] = lyricsMetadataDictionary['Artist'][0]
                    if 'Album' in lyricsMetadataDictionary:
                        albumList[-1]['label'] = lyricsMetadataDictionary['Album'][0]
                    if 'Track no' in lyricsMetadataDictionary:
                        songList[-1]['id'] = lyricsMetadataDictionary['Track no'][0]
                    if 'Year' in lyricsMetadataDictionary:
                        albumList[-1]['id'] = lyricsMetadataDictionary['Year'][0]
                    ## Render and write song page contents
                    html = pystache.render(templates['layout'], {
                        'title': artistList[-1]['label'] + ' – ' + songList[-1]['label'] + ' | ' + siteName,
                        'description': getDescriptionText(lyricsText),
                        'navigation': abc,
                        'breadcrumbs': getBreadcrumbs(letterLink, artistList[-1], albumList[-1], songList[-1]),
                        'content': formatLyricsAndMetadata(lyricsText, lyricsMetadata),
                    })
                    songPathFile.write(html)
                    songPathFile.close()

            ## Sort song list within the album by track number/letter
            if len(songList) > 0:
                # Determine if tracks bear alphabetic or decimal enumeration
                isOrderDecimal = False
                for song in songList:
                    if 'id' in song and song['id'].isdecimal():
                        isOrderDecimal = True
                        break
                if isOrderDecimal:
                    # By number (CDs, WEB releases)
                    songList.sort(key=sortListItems123)
                else:
                    # By letter (or letter + number, e.g. A, B1, B2) (LPs, cassette tapes)
                    songList.sort(key=sortListItemsABC)
            ## Format song number/letter labels
            songList = list(map(formatSongNumber, songList))
            ## Render and write album page contents
            html = pystache.render(templates['layout'], {
                'title': 'Album "' + albumList[-1]['label'] + '" by ' + artistList[-1]['label'] + ' | ' + siteName,
                'description': getDescriptionList(songs),
                'navigation': abc,
                'breadcrumbs': getBreadcrumbs(letterLink, artistList[-1], albumList[-1]),
                'content': pystache.render(templates['list'], {'links': songList}),
            })
            albumPathFile.write(html)
            albumPathFile.close()

        ## Sort albums by year
        albumList.sort(key=sortListItems123)
        ## Wrap album years in parens
        albumList = list(map(formatAlbumYear, albumList))
        ## Render and write artist page contents
        html = pystache.render(templates['layout'], {
            'title': artistList[-1]['label'] + ' | ' + siteName,
            'description': getDescriptionList(albums),
            'navigation': abc,
            'breadcrumbs': getBreadcrumbs(letterLink, artistList[-1]),
            'content': pystache.render(templates['list'], {'links': albumList}),
        })
        artistPathFile.write(html)
        artistPathFile.close()

    ## Render and write letter page contents
    html = pystache.render(templates['layout'], {
        'title': 'Artists starting with ' + letter + ' | ' + siteName,
        'description': getDescriptionList(artists),
        'navigation': abc,
        'breadcrumbs': getBreadcrumbs(letterLink),
        'content': pystache.render(templates['list'], {'links': artistList}),
    })
    letterPathFile.write(html)
    letterPathFile.close()

## Write the sitemap file
sitemapFile = mkfile('', sitemapFileName)
xml = pystache.render(templates['sitemap'], {'links': sitemapURLs})
sitemapFile.write(xml)
sitemapFile.close()

#################################
#                               #
#  The build process ends here  #
#                               #
#################################

## Print newline
print(file=sys.stderr)
