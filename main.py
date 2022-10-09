import json

import grequests
import requests
from lxml.html import fromstring
import httplib2
from httplib2 import RedirectLimit
import typer
import csv
from bs4 import BeautifulSoup, SoupStrainer
import urllib.parse


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

        # all links array
        self.all_links = []
        self.all_titles = []
        visited_sites = set()

        links_to_visit = []
        links_to_visit.append(self.url)
        visited_sites.add(self.url)

        lista_list_linkow = []

        rs = (grequests.get(link) for link in links_to_visit)
        rs_to_process = grequests.map(rs)

        links = {

        }

        while len(rs_to_process) > 0:
            content = rs_to_process[0]
            rs_to_process.pop(0)
            url = links_to_visit.pop(0)

            if url not in links:
                links[url] = ("",0,0,0)

            if content is None:
                continue

            try:
                link_data = list(links[url])
                for title in BeautifulSoup(content.text, 'html.parser', parseOnlyThese=SoupStrainer('title')):
                    self.all_titles.append(title.text)
                    link_data[0] = title.text

                internals, externals = self.extract_links(response=content.text)
                for inter in internals:
                    if inter not in links:
                        links[url] = ("", 0, 0, 1)
                    else:
                        inter_link_data = list(links[inter])
                        inter_link_data[-1] += 1
                        links[inter] = tuple(inter_link_data)

                internals_not_visited = []

                for inter in internals:
                    if inter not in visited_sites:
                        internals_not_visited.append(inter)
                        visited_sites.add(inter)

                rs = (grequests.get(link) for link in internals_not_visited)
                rs_to_process = rs_to_process + (grequests.map(rs))
                links_to_visit = links_to_visit+internals_not_visited

                link_data[1] = len(internals)
                link_data[2] = len(externals)
                print(link_data)

            except (RedirectLimit, httplib2.ServerNotFoundError, UnicodeError, httplib2.RelativeURIError, TypeError):
                print('redirection limit on', content)

        print(links)

    def is_external_link(self, link: str) -> bool:
        return link.startswith('https') or link.startswith('http')

    def save_to_file(self):
        # save to CSV/JSON file with link, title, len(self.all_link), self.count_external, len(self.all_links) - self.count_external
        pass

    def extract_links(self, response: str):
        all_links = []
        for link in BeautifulSoup(response, 'html.parser', parseOnlyThese=SoupStrainer('a')):
            if link.has_attr('href'):
                all_links.append(link['href'])

        external_links = []
        internal_links = []
        for link in all_links:
            if self.is_external_link(link=link):
                external_links.append(link)
            else:
                internal_links.append(urllib.parse.urljoin(self.url, link))

        return internal_links, external_links


if __name__ == "__main__":
    typer.run(ToCrawl)
