from urllib.parse import urlparse

import utils

def main(data):
    url = urlparse(data["config"]["Site"]["Url"])
    contents = "Host: " + url.netloc + "\n"
    if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
        contents += "Sitemap: " + utils.resolveURL(url.geturl(), data["definitions"]["filenames"]["sitemap"]) + "\n"
    fileHandle = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        "robots.txt",
    )
    fileHandle.write(contents)
    fileHandle.close()
