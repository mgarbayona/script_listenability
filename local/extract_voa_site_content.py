import re

from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve




def main():
    url = "https://learningenglish.voanews.com/a/omicron-vs-delta-battle-of-the-variants/6343393.html"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # to get audio file
    for a in soup.findAll('a',href=re.compile('http.*\.mp3')):
        print ("URL:", a['href'])

    links = [a['href'] for a in soup.find_all('a',href=re.compile('http.*_hq\.mp3'))]

if __name__ == "__main__":
    main()
