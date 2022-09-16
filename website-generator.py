#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import importlib.util
import os
import re

import utils

definitions = {
    "runtime": {
        "cwd": os.path.dirname(os.path.realpath(__file__)),
    },
    "filenames": {
        "index":    "index.html",
        "notfound": "404.html",
        "search":   "s.htm",
        "css":      "g.css",
        "sitemap":  "sitemap.xml",
    },
    "link_types": {
        "group": 1,
        "artist": 2,
        "release": 3,
        "recording": 4,
        "language": 5,
    },
}

## Config
config = configparser.ConfigParser()
configFile = os.path.join(definitions["runtime"]["cwd"], "config.ini")
if os.path.isfile(configFile):
    config.read(configFile)
else:
    print("Error: config.ini does not exist")
    exit()

## Function for optimizing templates’ code
def shrinkwrapTemplate(markup):
    return re.sub(r"\n\s*", "", markup)

## Function for reading and optimizing templates’ code
def getTemplateContents(templateFileName):
    if templateFileName == "sitemap.mustache":
        return open(os.path.join(templatesPath, templateFileName), "r").read()
    else:
        return shrinkwrapTemplate(open(os.path.join(templatesPath, templateFileName), "r").read())

## Read and store template files
templates = {}
templatesPath = os.path.join(definitions["runtime"]["cwd"], "src", "templates")
templatesFileNames = next(os.walk(templatesPath))[2]
for templateFileName in templatesFileNames:
    (templateName, _) = os.path.splitext(templateFileName)
    templates[templateName] = getTemplateContents(templateFileName)

## Schema
##
## data:
##     "database": {
##         LetterGroup {
##             Artist {
##                 "name": String,
##                 "printable_name": String,
##                 "releases": [
##                     {
##                         "name": String,
##                         "printable_name": String,
##                         "recordings": [
##                             [
##                                 {
##                                     "name": String,
##                                     "printable_name": String,
##                                     "text": String,
##                                     "metadata": {},
##                                     "disc_no": Int,
##                                     "track_no": Int,
##                                     "postfix": String,
##                                 }
##                             ]
##                         ],
##                         "year": Int
##                     }
##                 ]
##             }
##         }
##     }
##     "translations": {
##         Language {
##             LetterGroup {
##                 Artist {
##                     "name": String,
##                     "printable_name": String,
##                     "releases": [
##                         {
##                             "name": String,
##                             "printable_name": String,
##                             "recordings": [
##                                 [
##                                     {
##                                         "name": String,
##                                         "printable_name": String,
##                                         "text": String,
##                                         "metadata": {},
##                                     }
##                                 ]
##                             ]
##                         }
##                     ]
##                 }
##             }
##         }
##     }
data = {
    "definitions": definitions,
    "config": config,
    "templates": templates,
    "database": {},
    "translations": {},
    "videos": {},
}
if data["config"].getboolean("Site", "CreateSitemap", fallback=False):
    data["sitemap"] = []

buildStagesDirectory = os.path.join(definitions["runtime"]["cwd"], os.path.splitext(os.path.basename(__file__))[0] + ".d")
for buildStageFilename in sorted(os.listdir(buildStagesDirectory), key=str.lower):
    if buildStageFilename.endswith(".py"):
        spec = importlib.util.spec_from_file_location(buildStageFilename, os.path.join(buildStagesDirectory, buildStageFilename))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        buildStageMainFn = getattr(module, "main")
        buildStageMainFn(data)
