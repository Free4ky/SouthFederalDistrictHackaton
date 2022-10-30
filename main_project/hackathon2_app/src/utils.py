import numpy as np
from bs4 import BeautifulSoup
import requests


def get_unique_values(a):
    indexes = np.unique(a, return_index=True)[1]
    return a[sorted(indexes)]

def get_reverse_rank(a, val):
    try:
        rank = np.where(a == val)[0][0]
        return 1 - rank / a.shape[0]
    except IndexError:
        return 0

def get_text_from_website(url: str) -> str:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    paragraphs = []
    for paragraph in soup.find_all('p'):
        paragraphs.append(paragraph.getText())
    return '. '.join(paragraphs)

