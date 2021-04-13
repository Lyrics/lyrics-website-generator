import pystache

import utils

def main(data):
    ## Write the sitemap file
    sitemapFile = utils.mkfile(
        data["definitions"]["runtime"]["cwd"],
        data["config"]["Filesystem"]["DestinationDirPath"],
        data["definitions"]["filenames"]["sitemap"],
    )
    xml = pystache.render(data["templates"]["sitemap"], {
        "links": map(lambda path: utils.resolveURL(data["config"]["Site"]["URL"], path), data["sitemap"]),
    })
    sitemapFile.write(xml)
    sitemapFile.close()
