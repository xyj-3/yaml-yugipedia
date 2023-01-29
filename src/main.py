# SPDX-FileCopyrightText: © 2022 Kevin Lu
# SPDX-Licence-Identifier: LGPL-3.0-or-later
from platform import python_version
import random
import sys
from time import sleep

import httpx
from ruamel.yaml import YAML

from utils import download


# User agents containing the substring "python" in any casing are forbidden after 2023-01-28
user_agent = f"https://github.com/DawnbrandBots/yaml-yugipedia httpx/{httpx.__version__} py/{python_version()}"


def main():
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <category>\ne.g. Duel_Monsters_cards, Skill_Cards, Rush_Duel_cards, Yu-Gi-Oh!_Duel_Links_Skills")
    category = sys.argv[1]
    with httpx.Client(http2=True, headers={"User-Agent": user_agent}) as client:
        yaml = YAML()
        url = "https://yugipedia.com/api.php?action=query&redirects=true&generator=categorymembers&prop=revisions&rvprop=content&format=json&formatversion=2&gcmlimit=50"
        url += f"&gcmtitle=Category:{category}"
        if len(sys.argv) > 2:
            gcmcontinue = sys.argv[2]
        else:
            gcmcontinue = download(client, yaml, "gcmcontinue", url)
        while gcmcontinue is not None:
            print(f"gcmcontinue = {gcmcontinue}", flush=True)
            sleep(random.uniform(1, 2))
            gcmurl = f"{url}&gcmcontinue={gcmcontinue}"
            gcmcontinue = download(client, yaml, "gcmcontinue", gcmurl)


if __name__ == "__main__":
    main()
