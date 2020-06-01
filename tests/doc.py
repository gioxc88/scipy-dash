import re
from urllib.parse import urljoin

import requests
import bs4

from markdownify import markdownify as md
from bs4 import BeautifulSoup

from . import config


dist = 'norm'
def get_doc(dist):
    r = requests.get(f'{config.scipy_url}{dist}.html')
    soup = BeautifulSoup(r.content, features='lxml')
    body = soup.findAll('div', id=re.compile(r'^scipy-stats-'))[0]
    paragraphs = body.find_all('p', 'rubric')
    found = False
    to_remove = []
    for i, descendant in enumerate(body.descendants):
        if descendant is not None:
            if descendant.name == 'p' and descendant.text == 'Examples':
                found = True
                print(found)
            if found:
                to_remove.append(descendant)

    for element in to_remove:
        try:
            element.decompose()
        except AttributeError:
            pass
    html = re.sub(r'\n\s', '', str(body))
    # return body.text.strip()
    # return html
    return md(html)
