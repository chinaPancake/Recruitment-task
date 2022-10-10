import json
import asyncio
from urllib.parse import urljoin, urlparse

import httpx
from httpx import Response
import itertools
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.opened_connections = 0

    async def crawl_site(self):
        urls_to_gather = [self.base_url]
        urls_visited = set(urls_to_gather)
        links = { }
        async with httpx.AsyncClient() as client:
            while len(urls_to_gather) > 0:
                gathered = await asyncio.gather(
                    *map(self.fetch_link, urls_to_gather, itertools.repeat(client), )
                )
                urls_to_gather.clear()
                for wholeLink in gathered:
                    for link in wholeLink.internal:
                        if link not in urls_visited:
                            urls_visited.add(link)
                            urls_to_gather.append(link)
                    if wholeLink.url not in links:
                        links[wholeLink.url] = wholeLink
                    else:
                        print('that shouldnt be there')
        for link in links:
            current = links[link]
            for internal in current.internal:
                links[internal].references_from += [link]

        return links

    async def fetch_link(self, url: str, client: httpx.AsyncClient):
        self.opened_connections += 1

        print(f'Fetching {url}. Opened connections: {self.opened_connections}')
        try:
            content = await client.get(url)
        except:
            content = None
        finally:
            self.opened_connections -= 1

        print(f'Finished fetching {url}. Opened connections: {self.opened_connections}')

        return Link(self.base_url, url, content)


class Link:
    def __init__(self, base_url: str, url: str, content: Response):
        self.url = url
        self.content = content
        self.title = self.get_title()
        self.internal = self.get_internal_links(base_url)
        self.external = self.get_external_links()
        self.references_from = []

    def get_title(self):
        if self.content is None:
            return ''
        soup = BeautifulSoup(self.content.text, 'html.parser')
        for title in soup.find_all('title'):
            return title.text
        return ''

    def get_external_links(self):
        if self.content is None:
            return set()

        links = set()
        soup = BeautifulSoup(self.content.text, 'html.parser')
        for link in soup.find_all('a'):
            if self.is_external(link.get('href')):
                links.add(link.get('href'))
        return links

    def get_internal_links(self, base_url: str):
        if self.content is None:
            return set()

        links = set()
        soup = BeautifulSoup(self.content.text, 'html.parser')
        for link in soup.find_all('a'):
            if not self.is_external(link.get('href')):
                url = urljoin(base_url, link.get('href'))
                links.add(url)
        return links

    def is_external(self, url: str):
        return url.startswith('http') if url is not None else False


class LinksPrinter:
    def __init__(self, links):
        self.links = links

    def print_as_csv(self, delimiter: str):
        retVal = f'Url{delimiter}title{delimiter}External links{delimiter}{delimiter}Internal links{delimiter}References'
        for linkStr in self.links:
            link = self.links[linkStr]
            retVal += f'{link.url}{delimiter}{link.title}{delimiter}{len(link.external)}{delimiter}{len(link.internal)}{delimiter}{len(link.references_from)}\n'
        return retVal

    def print_as_json(self):
        links = []
        for linkStr in self.links:
            link = self.links[linkStr]
            links += [{'url': link.url, 'title': link.title, 'external': len(link.external), 'internal': len(
                link.internal), 'references': len(link.references_from)}]
        return str(links)

    def print_as_struct(self, base: str, depth: int, stack: set[str]):
        link = self.links[base]
        inner = set(stack)
        inner.add(link.url)
        ret_val = ''
        for each in link.internal:
            ret_val += ' ' * depth + each + '\n'
            if each not in inner:
                ret_val += self.print_as_struct(each, depth + 1, inner)
        return ret_val

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    crawler = Crawler('https://crawler-test.com/')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(crawler.crawl_site())
    printer = LinksPrinter(result)
    csv = open('crawler.csv', 'w', encoding="utf-8")
    json = open('crawler.json', 'w',encoding="utf-8")
    structure = open('crawler.txt', 'w', encoding="utf-8")
    csv.write(printer.print_as_csv(delimiter=','))
    csv.close()
    json.write(printer.print_as_json())
    json.close()
    structure.write(printer.print_as_struct('https://crawler-test.com/', 0, set()))
    structure.close()
