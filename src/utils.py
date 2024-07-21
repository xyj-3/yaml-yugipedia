# SPDX-FileCopyrightText: © 2022–2023 Kevin Lu
# SPDX-Licence-Identifier: LGPL-3.0-or-later
from logging import getLogger
import random
from time import sleep
from typing import Optional
from urllib.parse import quote

import httpx
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

import re


logger = getLogger(__name__)


def get_retry(client: httpx.Client, url: str) -> httpx.Response:
    for retry in range(5):
        try:
            return client.get(url, follow_redirects=True)
        except httpx.RequestError as e:
            logger.warning(f"TRY {retry}\t{e}\t{url}")
            sleep(random.uniform(1 + retry, 2 + retry))


def download(
    client: httpx.Client, yaml: YAML, continue_key: str, url: str, skip_condition=None
) -> Optional[str]:
    # logger.info(url)
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    result = response.json()
    logger.debug(f"{url} | {result}")
    # print(len(result["query"]["pages"]))  # TESTING
    if not result.get("batchcomplete"):
        logger.warning(f"batchcomplete != true | {url}")
    warnings = result.get("warnings")
    if warnings:
        logger.warning(f"{warnings} | {url}")
    continue_value = (
        result["continue"][continue_key] if result.get("continue") else None
    )
    print("continue_value", continue_value)
    if "query" not in result:
        logger.warning(f"No results! | {url}")
        return
    for page in result["query"]["pages"]:
        pageid = page["pageid"]
        if skip_condition is not None and skip_condition(page):
            logger.debug(f"Skipping {pageid} | {url}")
            continue
        n_revisions = len(page["revisions"])
        contentformat = page["revisions"][0]["contentformat"]
        contentmodel = page["revisions"][0]["contentmodel"]
        if n_revisions != 1:
            logger.warning(f"{n_revisions} revisions | {pageid} | {url}")
        if contentformat != "text/x-wiki":
            logger.warning(f"contentformat = {contentformat} | {pageid} | {url}")
        if contentmodel != "wikitext":
            logger.warning(f"contentmodel = {contentmodel} | {pageid} | {url}")
        with open(f"{pageid}.yaml", mode="w", encoding="utf-8") as out:
            title = page["title"]
            # logger.info(f"Writing out {pageid}.yaml [{title}] | {url}")
            yaml.dump(
                {
                    "title": title,
                    "wikitext": LiteralScalarString(page["revisions"][0]["content"]),
                },
                out,
            )
            if page["ns"] == 14:  # is Category page
                title_ = title.replace(" ", "_")
                subcat_url = re.sub(r"Category:[a-zA-Z0-9_!-]+", f'{title_}', url)
                print(title_)
                # print(subcat_url)
                # download(client, yaml, continue_key, subcat_url)

                gcmcontinue =  download(client, yaml, continue_key, subcat_url)
                while gcmcontinue is not None:
                    sleep(random.uniform(1, 2))
                    gcmurl = f"{subcat_url}&gcmcontinue={quote(gcmcontinue)}"
                    gcmcontinue = download(client, yaml, continue_key, gcmurl)

    return continue_value
