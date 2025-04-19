import sys
from common import *
import requests
import shelve
import json

url = "https://ssd-api.jpl.nasa.gov/sbdb.api"

class SmallBodiesDatabase:
    http_responses = None

    def __init__(self, savefile):
        try:
            savefile = ROOT + "/save/" + savefile
            self.http_responses = shelve.open(savefile + "_http_responses", writeback=True)
        except Exception as e:
            print(e)
            sys.exit()

    def close(self):
        self.http_responses.close()

    def jpl_lookup(self, text):
        print(f"jpl_lookup '{text}':", end=" ")
        http_response = self.do_request(url + "?sstr=" + text)
        if http_response is None:
            print("jpl_lookup: http_response is None")
            return None
        try:
            reponse_json = json.loads(http_response.text)
        except Exception as e:
            print("Failed to convert http response to json object: ", http_response)
            print("Exception:", e)
            return None
        if "message" in reponse_json:
            print(reponse_json["message"])
        if "list" in reponse_json:
            print(f"{len(reponse_json['list'])} objects")
            print(", ".join(sorted([y['name'] for y in reponse_json['list']])))
            out = []
            for y in reponse_json['list']:
                words = y['name'].split(" ")
                for word in words:
                    word = word.strip()
                    if word.isalpha():
                        out.append(word)
            out.sort()
            print(", ".join(out))
            return
        if "object" in reponse_json:
            print(f"'{reponse_json['object']['shortname']}'", end=", ")
            print("orbit:", reponse_json['orbit'])
            return reponse_json
        return response_json

    def do_request(self, url):
        if url in self.http_responses:
            response = self.http_responses[url]
            # print("Found in cache:", url)
            return response
        print("Doing request", url, " ... Sometimes it takes a little while, so please wait and dont press Ctrl-C.")
        try:
            response = requests.get(url)
            self.http_responses[url] = response
            print("Response: ", response.text[:50] + "...")
            return response
        except Exception as e:
            print("Request failed:", request)
            print("Error", e)
            return None

    def get_cached_bodies(self, search_string):
        return [(key, value) for (key, value) in self.small_bodies.items() if search_string.lower() in key.lower()]

# Cache queries
# Mapping from key to dict (from json)
# indices

# ==========================================================

def test_all():
    sb = SmallBodiesDatabase("small_bodies")
    print("cached http_requests:", list(sb.http_responses.keys()))
    response_json = sb.jpl_lookup("Eros")
    response_json = sb.jpl_lookup("Ceres")
    print("---")
    response_json = sb.jpl_lookup("C*")
    sys.exit()
    print(response)
    print(response.text)
    j = json.loads(response.text)
    print(j)
    for (key, value) in j.items():
        print(key, value)
    sys.exit()
    xs = j['list']
    for x in xs:
        print(x)

    # print(sb.get_cached_bodies("er"))
    sys.exit()


    eros = sb.small_bodies["Eros"]
    #print(eros)
    print(eros["object"]["shortname"])
    orbit = eros["orbit"]
    #print(orbit)
    #print(orbit["elements"])
    for elem in orbit["elements"]:
        title = elem['title']
        if ";" in title:
            title = title.split(";")[0]
        title += " (" + elem["name"] + "/" + elem['label'] + ")"
        value = elem['value']
        units = elem['units']
        value += (" " + units) if units is not None else ""
        print(f"{title:<45}   {value:<15}   (sigma: {elem['sigma']})")

    sys.exit()

    foo = sb.jpl_lookup("Eros")
    sb.close()

    print(foo)
    bar = json.loads(foo)
    print(bar)

if __name__ == "__main__":
    test_all()


