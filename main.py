import json

import httplib2
import typer
import csv
from bs4 import BeautifulSoup, SoupStrainer


# we have to crawl: link, title, number of internal links, number of times url was referenced by other pages
# crawl --page <URL> --format <csv/json> --output <path_to_file>

# done link
# done title
# counting internal and external links is done

class ToCrawl:
    def __init__(self, url: str):
        # input url
        self.external = None
        self.url = url
        self.http = httplib2.Http()

        # get request form URL
        self.status, self.response = self.http.request(self.url)
        self.count_external = 0

        # all links array
        self.all_links = []
        self.all_titles = []

        # get title from URL
        for link in BeautifulSoup(self.response, 'html.parser', parseOnlyThese=SoupStrainer('title')):
            self.all_titles.append(link.text)
            print(self.all_titles)


        for link in BeautifulSoup(self.response, 'html.parser', parseOnlyThese=SoupStrainer('a')):
            if link.has_attr('href'):
                self.all_links.append(link['href'])

        self.counter = 0
        for link in self.all_links:
            if self.is_external_link(link=link):
                self.count_external +=1
            if link is not self.is_external_link(link=link):
                if link.startswith('/'):
                    print(link)

        print(f'There is: {len(self.all_links)}, links')
        print(f'There is: {self.count_external} external links')
        print(f'There is: {len(self.all_links) - self.count_external} linternal links')

        self.save_to_file()

    def is_external_link(self, link: str) -> bool:
        return link.startswith('https') or link.startswith('http')

    def save_to_file(self):
        # save to CSV/JSON file with link, title, len(self.all_link), self.count_external, len(self.all_links) - self.count_external
        self.file = open('datas.json', 'w')
        json.dump(self.all_links, self.file)
        self.file.close()

if __name__ == "__main__":
    typer.run(ToCrawl)
