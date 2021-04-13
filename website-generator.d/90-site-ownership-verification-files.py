import utils

def main(data):
    ## Create Google website verification file
    if data["config"]["ThirdParty"]["GoogleSiteVerificationKey"]:
        contents = "google-site-verification: google" + data["config"]["ThirdParty"]["GoogleSiteVerificationKey"] + ".html\n"
        fileHandle = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            "google" + data["config"]["ThirdParty"]["GoogleSiteVerificationKey"] + ".html",
        )
        fileHandle.write(contents)
        fileHandle.close()

    ## Create Yandex website verification file
    if data["config"]["ThirdParty"]["YandexSiteVerificationKey"]:
        contents = '<html>\n\
    <head>\n\
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n\
    </head>\n\
    <body>\n\
        Verification: ' + data["config"]["ThirdParty"]["YandexSiteVerificationKey"] + '\n\
    </body>\n\
</html>\n'
        fileHandle = utils.mkfile(
            data["definitions"]["runtime"]["cwd"],
            data["config"]["Filesystem"]["DestinationDirPath"],
            "yandex_" + data["config"]["ThirdParty"]["YandexSiteVerificationKey"] + ".html",
        )
        fileHandle.write(contents)
        fileHandle.close()
