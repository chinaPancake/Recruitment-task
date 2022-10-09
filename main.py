import json

import httplib2
from httplib2 import RedirectLimit
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
        self.url = url
        self.http = httplib2.Http()

        # get request form URL
        self.status, self.response = self.http.request(self.url)
        self.count_external = 0

        # all links array
        self.all_links = []
        self.all_titles = []
        self.internal_links = []

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
            else:
                if link.startswith('/'):
                    self.internal_links.append(self.url+link)

        try:
            for link in self.internal_links:
                self.go_to = httplib2.Http()
                self.go_to_status, self.go_to_response = self.go_to.request(link)
                for title in BeautifulSoup(self.go_to_response, 'html.parser', parseOnlyThese=SoupStrainer('title')):
                    self.all_titles.append(title.text)
        except (RedirectLimit, httplib2.ServerNotFoundError, UnicodeError, httplib2.RelativeURIError):
            print('redirection limit on', link)


        print(f'There is: {len(self.all_links)}, links')
        print(f'There is: {self.count_external} external links')
        print(f'There is: {len(self.all_links) - self.count_external} linternal links')
        print(self.internal_links)
        self.save_to_file()

    def is_external_link(self, link: str) -> bool:
        return link.startswith('https') or link.startswith('http')

    def save_to_file(self):
        # save to CSV/JSON file with link, title, len(self.all_link), self.count_external, len(self.all_links) - self.count_external
        self.file = open('datas.json', 'w')
        json.dump(self.all_titles, self.file)
        self.file.close()

if __name__ == "__main__":
    typer.run(ToCrawl)
