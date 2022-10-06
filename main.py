import typer
import requests
from requests_html import HTMLSession
import lxml
import json
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import csv

# we have to crawl: link, title, number of internal links, number of times url was referenced by other pages
# crawl --page <URL> --format <csv/json> --output <path_to_file>

# done link
# done title

class ToCrawl:
    def __init__(self, url: str):
        # input url
        self.url = url
        self.http = httplib2.Http()
        self.status, self.response = self.http.request(self.url)
        self.count_external = 0
        self.all_links = []


        for link in BeautifulSoup(self.response, 'html.parser', parseOnlyThese=SoupStrainer('a')):
            if link.has_attr('href'):
                self.all_links.append(link['href'])

        for self.external in self.all_links:
            if self.external.startswith('https') or self.external.startswith('http'):
                self.count_external += 1

        print('There is: ', len(self.all_links), " links")
        print('There is: ', self.count_external, " external links")
        print('There is: ', len(self.all_links) - self.count_external," internal links")

if __name__ == "__main__":
    typer.run(ToCrawl)
