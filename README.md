# lyrics-website

Lyrics website generator

The build script links against `lyrics.git`'s `database` directory
and outputs website files into `./www/`. The contents of that directory
then can be uploaded to a server.


## Requirements

    pip3 install pystache simple-http-server


## Build

    make clean all


## Run local web server

    make serve


## Checklist

General
 - [x] all pages should render and be accessible without JavaScript
 - [ ] light and dark color modes should be available and support both `prefers-color-scheme` CSS selector and a toggle switch on the page
 - [ ] it should be possible to navigate through the website using only keyboard
 - [ ] 404 pages should redirect to search with a query constructed out of the requested URL's path
 - [ ] it should be possible to fully use the website via text-based browsers (e.g. w3m, lynx)
 - [ ] there should be extra margin at the bottom of each page to let the user center the content without having to move their eyes down when fully scrolled
 - [ ] the website should contain no 3rd-party assets (such as web fonts or script files)
 - [ ] reader mode should correctly work on all pages
 - [ ] pages with breadcrumbs should use breadcrumb schema
Mobile
 - [x] it should be possible to navigate the website and read lyrics using tablet or smartphone
 - [ ] while on mobile, all navigation items should be at least 40px wide/tall
Lyrics page
 - [x] lyrics sheet should preserve newline characters, but wrap onto the next line if wider than the viewport (to avoid having a horizontal scroll bar)
 - [x] lyrics sheet should have visible but very light full-width horizontal separators between lines
 - [ ] when copied, lyrics text should retain the same newlines when pasted into a plaintext environment as seen in the browser
Search
 - [x] search should return the list of songs found using the search API
