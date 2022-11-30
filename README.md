# Open Lyrics Database website generator

Suite capable of building static HTML website out of [Open Lyrics Database](https://github.com/Lyrics/lyrics).


## How to run in development mode (requires [Docker](https://www.docker.com) or [Podman](https://podman.io)):

```shell
make all
```


## How to run in production mode:

```shell
sudo apt-get install python3-setuptools sassc
make INSTALL_DEPENDENCIES
make BUILD
make SERVE
```


## Checklist

#### General
 - [x] all pages should render and be accessible without JavaScript (Unobtrusive JS)
 - [ ] should be possible to switch between light and dark color schemes using a global color mode toggle switch that retains state between pages
 - [x] 404 page should redirect to search with a query constructed out of the requested URL's path
 - [x] there should be extra margin at the bottom of each page to let the user center the content without having to move their eyes down when fully scrolled
 - [x] the website should contain no remote assets (such as web fonts or script files)
 - [x] web browser reader mode should correctly work on all pages
 - [x] pages with breadcrumbs should use breadcrumb schema
 - [ ] every page passes W3M HTML5 test
 - [ ] every page passes W3M CSS3 test
 - [x] website should never have full-page horizontal scroll

#### Accessibility
 - [x] light and dark color modes should be available and support `prefers-color-scheme` CSS media query
 - [ ] AAA contrasts
 - [ ] should be possible to navigate through the website using only keyboard
 - [x] should be possible to fully use the website via text-based browsers (e.g. w3m, lynx)

#### Mobile
 - [x] it should be possible to navigate the website and read lyrics using tablet or smartphone
 - [ ] while on mobile, all clickable items should be at least 40px wide/tall

#### Lyrics page
 - [x] lyrics sheet should preserve newline characters, but wrap onto the next line if wider than the viewport (to avoid having a horizontal scroll bar)
 - [x] lyrics sheet should have visible but very light full-width horizontal separators between lines (to make lyrics readable when wrapped)
 - [x] when copied, lyrics text should retain the same amount newlines when pasted into a plaintext environment as seen in the browser

#### Search
 - [x] search should return list of recordings found using GitHub search API

#### SEO
 - [x] must have a valid sitemap.xml file that contains all website URLs


## Credits

Favicon design by [@defanor](https://github.com/defanor)
