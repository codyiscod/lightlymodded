# this is broken, idk, i can't be bothered troubleshooting it rn


import requests
import json
from pathlib import Path
from sys import exit
from dataclasses import dataclass

@dataclass
class Mod:
    name: str
    id: str
    url: str
    game_versions: list[str]
    loaders: list[str]
    supported: bool | None = None



SCRIPT_DIR = Path(__file__).parent
VERSION_DIR = SCRIPT_DIR / "versions"
MODRINTH_API = (SCRIPT_DIR / "modrinth_api.txt").read_text(encoding="utf-8").strip()
HEADERS = {
    "Authorization": MODRINTH_API
}

    # get original version file
# print("Original version file:")
# old_version = input("| Minecraft version > ")
# old_loader = input("| Loader > ")
old_version = "26.3"
old_loader = "fabric"
old_file = VERSION_DIR / f"{old_version}-{old_loader}.json"

# check to see if its a valid file
if old_file.is_file():
    print("Found version file!\n")
else:
    input("No version file found! Press Enter to exit... ")
    exit()


    # ask for converted file stuff
# print("Converted version:")
# version = input("| Minecraft version > ")
# loader = input("| Loader > ")
version = "1.21.11"
loader = "fabric"
file = f"{version}-{loader}.json"





# modrinth api web request stuff
def get_project(mod_id: str):
    """
    Get `https://api.modrinth.com/v2/project/{mod.id}`
    """
    try:
        res = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}", headers=HEADERS)
        return json.loads(res.text)
    except:
        return None

def get_versions(mod_id: str):
    """
    Get `https://api.modrinth.com/v2/project/{mod.id}/version`
    """
    try:
        res = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}/version", headers=HEADERS)
        return json.loads(res.text)
    except:
        return None
    




def check_mod(mod: object):
    """
    Check if the mod is compatible with the new version and loader
    Calls `replace_id` if not supported. Loops until no replacement given or supported mod found
    """
    if version in mod.game_versions and loader in mod.loaders:
        print(f"✅ {mod.name}")
        mod.supported = True
        return mod
    else:
        print(f"❌ {mod.name} - Incompatible")
        replace_mod(mod)


def replace_mod(mod: object):
    """Replace an mod 

    Returns:
        _type_: _description_
    """
    print(f"  Please input an ID to replace \"{mod.name}\", or press Enter to skip")
    new_id = input("  New ID > ")
    
    if new_id.strip() == "":
        mod.supported = False
        return mod
    else:
        new_mod_project = get_project(new_id)
        if new_mod_project:
            check_mod(Mod(
                name = mod.name,
                id = new_id,
                url = f"https://modrinth.com/mod/{new_id}",
                game_versions = new_mod_project["game_versions"],
                loaders = new_mod_project["loaders"],
                supported = None
            ))
        else:
            replace_mod(mod)




# get mod ids from old version file
mods = []
with open(old_file, "r", encoding="utf-8") as file:
    for mod in json.load(file):
        mod_id = mod["url"].removeprefix("https://modrinth.com/mod/")
        mods.append(Mod(
            name          = mod["name"],
            id            = mod_id,
            url           = mod["url"],
            game_versions = get_project(mod_id)["game_versions"],
            loaders       = get_project(mod_id)["loaders"],
            supported     = None
        ))

total_ids = len(mods)
print(f"Found {total_ids} mod IDs\n")

for mod in mods:
    mod = check_mod(mod)