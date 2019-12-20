#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import pystache
from urllib.parse import quote

# Config
siteURL = 'https://lyrics.github.io'
siteName = 'Lyrics'
srcDir = '../../lyrics.git/database'
dbDir = 'db'
# File names
indexFileName = 'index.html'
notFoundFileName = '404.html'
searchFileName = 'search.html'
sitemapFileName = 'sitemap.xml'

# Templates
t404 = open('../src/templates/404.mustache', 'r').read()
tHome = open('../src/templates/home.mustache', 'r').read()
tLayout = open('../src/templates/layout.mustache', 'r').read()
tList = open('../src/templates/list.mustache', 'r').read()
tSearch = open('../src/templates/search.mustache', 'r').read()
tSitemap = open('../src/templates/sitemap.mustache', 'r').read()

# Dictionary of letters (used for global navigation)
abc = []
for letter in list(map(chr, range(ord('A'), ord('Z')+1))):
    abc.append({ 'path': '/' + dbDir + '/' + letter, 'label': letter })

# List of URLs to be added to the sitemap file
sitemapURLs = []

def getSafePath(input):
    return input

def mkfile(where='', filename=indexFileName):
    return open(os.path.join(where, filename), 'w')

def getLink(target, text, depth):
    return { 'link': '/' + quote(target) + '/', 'label': text, 'type': depth }

def getSitemapURL(target=''):
    URL = siteURL + '/' + quote(target)
    if target:
        URL += '/'
    return URL

def getBreadcrumbs(*items):
    output = []
    depth = 0
    base = dbDir
    for item in items:
        base = os.path.join(base, getSafePath(item))
        output.append(getLink(base, item, depth))
        depth += 1
        if depth < len(items):
            output.append(None)
    return output

def getLyrics(text):
    regex = re.compile(r'(.*)\n+_+\n(.*)$', re.DOTALL)
    # Extract the song text
    lyricsText = regex.sub(r'\1', text)
    # Separate text into paragraphs
    lyricsText = re.sub('\n\n+', '<span><br/></span><span class="g"><br/></span>', lyricsText)
    # Convert newline characters into linebreaks
    lyricsText = re.sub('\n', '<span><br/></span>', lyricsText)
    # Take care of the metadata
    metaData = regex.sub(r'\2', text)
    metaData = re.sub('\n', '<br/>', metaData)
    return '<blockquote id="lyrics">' + lyricsText + '<br/><br/><br/><hr/><p>' + metaData + '</p></blockquote>'

def getDescriptionList(items):
    return ', '.join(items[:24])

def getDescriptionText(text):
    text = re.sub('\n+', ' / ', text)
    text = re.sub(' +', ' ', text)
    text = text[:220]
    return text.strip()

def mkdir(path):
    os.makedirs(path, exist_ok=True)

# 0. Create the root index file
html = pystache.render(tLayout, {
    'title': siteName,
    'description': "Web interface to the lyrics database hosted on GitHub",
    'navigation': abc,
    'content': pystache.render(tHome)
})
homepageFile = mkfile()
homepageFile.write(html)
homepageFile.close()

# Create the 404 page
html = pystache.render(tLayout, {
    'title': "Page not found" + " | " + siteName,
    'description': "Error 404: page not found",
    'navigation': abc,
    'content': pystache.render(t404)
})
notFoundFile = mkfile('', notFoundFileName)
notFoundFile.write(html)
notFoundFile.close()

# Create the search page
html = pystache.render(tLayout, {
    'title': "Search" + " | " + siteName,
    'description': "Find lyrics using GitHub's code search engine",
    'navigation': abc,
    'content': pystache.render(tSearch)
})
searchFile = mkfile('', searchFileName)
searchFile.write(html)
searchFile.close()

# Add root URL to the list of sitemap links
sitemapURLs.append(getSitemapURL())

# 1. Loop through letters in the database
# for letter in sorted(os.listdir(srcDir)):
for letter in sorted(next(os.walk(srcDir))[1]):
    # Output progress status
    print(letter, end=" ", file=sys.stderr)
    sys.stderr.flush()

    letterPath = os.path.join(srcDir, letter)
    safeLetterPath = getSafePath(os.path.join(dbDir, letter))
    sitemapURLs.append(getSitemapURL(safeLetterPath))
    # Create db/x/
    mkdir(safeLetterPath)
    # Create db/x/index.html
    letterPathFile = mkfile(safeLetterPath)
    letters = sorted(next(os.walk(letterPath))[1], key=str.lower)
    artistList = []

    # 2. Loop through artists starting with letter x
    for artist in letters:
        artistPath = os.path.join(letterPath, artist)
        safeArtistPath = getSafePath(os.path.join(dbDir, letter, artist))
        sitemapURLs.append(getSitemapURL(safeArtistPath))
        # Create db/x/artist/
        mkdir(safeArtistPath)
        # Create db/x/artist/index.html
        artistPathFile = mkfile(safeArtistPath)
        # Append artist link to db/x/index.html
        artistList.append(getLink(safeArtistPath, artist, 1))
        albums = sorted(next(os.walk(artistPath))[1], key=str.lower)
        albumList = []

        # 3. Loop through artist's albums
        for album in albums:
            albumPath = os.path.join(artistPath, album)
            safeAlbumPath = getSafePath(os.path.join(dbDir, letter, artist, album))
            sitemapURLs.append(getSitemapURL(safeAlbumPath))
            # Create db/x/artist/album/
            mkdir(safeAlbumPath)
            # Create db/x/artist/album/index.html
            albumPathFile = mkfile(safeAlbumPath)
            # Append album link to db/x/artist/index.html
            albumList.append(getLink(safeAlbumPath, album, 2))
            songs = sorted(next(os.walk(albumPath))[2], key=str.lower)
            songList = []

            # 4. Loop through songs
            for song in songs:
                songPath = os.path.join(albumPath, song)
                if not os.path.isfile(songPath):
                    print(songPath + " is not a file! 0x04")
                else:
                    safeSongPath = getSafePath(os.path.join(dbDir, letter, artist, album, song))
                    sitemapURLs.append(getSitemapURL(safeSongPath))
                    # Create db/x/artist/album/song/
                    mkdir(safeSongPath)
                    # Create db/x/artist/album/song/index.html
                    songPathFile = mkfile(safeSongPath)
                    # Append song link to db/x/artist/album/index.html
                    songList.append(getLink(safeSongPath, song, 3))
                    # Read the lyrics file
                    lyrics = open(songPath, 'r').read().strip()
                    html = pystache.render(tLayout, {
                        'title': artist + ' – ' + song + ' | ' + siteName,
                        'description': getDescriptionText(lyrics),
                        'navigation': abc,
                        'breadcrumbs': getBreadcrumbs(letter, artist, album, song),
                        'content': getLyrics(lyrics),
                    })
                    songPathFile.write(html)
                    songPathFile.close()

            html = pystache.render(tLayout, {
                'title': 'Album "' + album + '" by ' + artist + ' | ' + siteName,
                'description': getDescriptionList(songs),
                'navigation': abc,
                'breadcrumbs': getBreadcrumbs(letter, artist, album),
                'content': pystache.render(tList, {'links': songList}),
            })
            albumPathFile.write(html)
            albumPathFile.close()

        html = pystache.render(tLayout, {
            'title': artist + ' | ' + siteName,
            'description': getDescriptionList(albums),
            'navigation': abc,
            'breadcrumbs': getBreadcrumbs(letter, artist),
            'content': pystache.render(tList, {'links': albumList}),
        })
        artistPathFile.write(html)
        artistPathFile.close()

    html = pystache.render(tLayout, {
        'title': 'Artists starting with ' + letter + ' | ' + siteName,
        'description': getDescriptionList(letters),
        'navigation': abc,
        'breadcrumbs': getBreadcrumbs(letter),
        'content': pystache.render(tList, {'links': artistList}),
    })
    letterPathFile.write(html)
    letterPathFile.close()

# Write the sitemap file
sitemapFile = mkfile('', sitemapFileName)
xml = pystache.render(tSitemap, {'links': sitemapURLs})
sitemapFile.write(xml)
sitemapFile.close()

print(file=sys.stderr)
