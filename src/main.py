# SPDX-FileCopyrightText: © 2022–2023 Kevin Lu
# SPDX-Licence-Identifier: LGPL-3.0-or-later
import logging
from platform import python_version
import random
import sys
from time import sleep
from urllib.parse import quote

import httpx
from ruamel.yaml import YAML

from utils import download, get_pageid


# User agents containing the substring "python" in any casing are forbidden after 2023-01-28
user_agent = f"https://github.com/DawnbrandBots/yaml-yugipedia httpx/{httpx.__version__} py/{python_version()}"


def main():
    if len(sys.argv) < 2:
        sys.exit(
            f"Usage: {sys.argv[0]} <category>\ne.g. Duel_Monsters_cards, Skill_Cards, Rush_Duel_cards, Yu-Gi-Oh!_Duel_Links_Skills"
        )
    logging.basicConfig(level=logging.INFO)
    category = sys.argv[1]
    with httpx.Client(http2=True, headers={"User-Agent": user_agent}) as client:
        yaml = YAML()
        url = "https://yugipedia.com/api.php?action=query&redirects=true&generator=categorymembers&prop=revisions&rvprop=content&format=json&formatversion=2&gcmlimit=50"
        url += f"&gcmtitle=Category:{category}"
        pageid = get_pageid(client, category)
        if pageid:
            seen = set()
            seen.add(pageid)
        else:
            seen = set()
        if len(sys.argv) > 2:
            gcmcontinue = sys.argv[2]
        else:
            gcmcontinue, seen = download(client, yaml, "gcmcontinue", url, seen)
        while gcmcontinue is not None:
            logging.info(f"gcmcontinue = {gcmcontinue}")
            sleep(random.uniform(1, 2))
            # URL encode first to prevent httpx from doing so and double-encoding earlier parts of the URL
            gcmurl = f"{url}&gcmcontinue={quote(gcmcontinue)}"
            gcmcontinue, _ = download(client, yaml, "gcmcontinue", gcmurl, seen)


if __name__ == "__main__":
    main()
