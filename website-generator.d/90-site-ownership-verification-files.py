import utils

def main(data):
    ## Create Google website verification file
    if data["config"].get("ThirdParty", "GoogleSiteVerificationKey", fallback=False):
        contents = "google-site-verification: google" + data["config"].get("ThirdParty", "GoogleSiteVerificationKey") + ".html\n"
        fileHandle = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"].get("Filesystem", "DestinationDirPath"),
            "google" + data["config"].get("ThirdParty", "GoogleSiteVerificationKey") + ".html",
        )
        fileHandle.write(contents)
        fileHandle.close()

    ## Create Yandex website verification file
    if data["config"].get("ThirdParty", "YandexSiteVerificationKey", fallback=False):
        contents = '<html>\n\
    <head>\n\
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
    </head>\n\
    <body>\n\
        Verification: ' + data["config"].get("ThirdParty", "YandexSiteVerificationKey") + '\n\
    </body>\n\
</html>\n'
        fileHandle = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"].get("Filesystem", "DestinationDirPath"),
            "yandex_" + data["config"].get("ThirdParty", "YandexSiteVerificationKey") + ".html",
        )
        fileHandle.write(contents)
        fileHandle.close()
