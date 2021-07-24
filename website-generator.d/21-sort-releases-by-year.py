import utils

def main(data):
    for groupKey in data["database"]:
        group = data["database"][groupKey]
        for artistKey in group:
            artist = data["database"][groupKey][artistKey]
            artist["releases"].sort(key=utils.sortReleasesByYear123)
