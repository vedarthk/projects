
'''
This script crawls the websites and keeps on adding the unique urls to the repository. It stops when the required number of urls are added in the repository or when Ctrl+c is pressed. 
On completion or on interrupt, it prints the list of urls and the summary: total number of urls visited and number of urls in repository.
The script uses set of md5 of the url to check if it already exists in the repository or not in order to make the look-up faster and md5 would save memory. 
If address of two links is different but they both redirect to the same page, they are considered unique. 
If the link in repositry (except start url) is not reachable , it is skipped by the crawler
It is assumed by the url parser (parse_url) that the url passed to it as input is not empty. Anyway there are no empty urls in the repository from which it gets the url to parse
Assumption: Memory for saving the links to the repository is not limited. 
A class and the main repository is used by the single url parser every time because it should have the sense of urls/links already present in the repository and stop adding further if the limit is crossed. 
Usage : python webcrawler <url> <max_no_of_urls_to_crawl>
'''

import os
import sys
import requests
import urlparse
import hashlib
from bs4 import BeautifulSoup

class UrlCrawler(object):

    def __init__(self,start_url,max_links):
        self.repository = [start_url]
        self.max_links = max_links
        self.url_set = set()
	self.url_set.add(hashlib.md5(start_url).hexdigest())

    # parse url and add the urls with tag = 'a' and href in the repository 
    def parse_url(self,url):
        try:
            content = requests.get(url, timeout = 5) # timeout as do not wait infinitely for server to respond
        except requests.exceptions.RequestException as e:
            print e
            return 1
        plaintext = content.text
        soup = BeautifulSoup(plaintext,"lxml")
        # Finding each href link with tag a
        for link in soup.findAll('a',href=True):
            # ignore the link to same page/null link
            if link['href'] == '' or link['href'].startswith('#') or link['href'] == '/':
                continue
            href = (link['href']).rstrip('/')
            # join root url to the links not with http / relative
            if not href.startswith("http"):
                href = urlparse.urljoin(url, href)
            # append a unique link to the repository
            if hashlib.md5(href).hexdigest() not in self.url_set:
                # check md5 in set because md5 will save memory and set will make it faster than checking in whole repository / db
                self.url_set.add(hashlib.md5(href).hexdigest()) 
                self.repository.append(href)
            if len(self.repository) >= self.max_links:
                print "Max limit achieved"
                return 0

    # a driver that gives one url to be parsed for the links,returns the repository and number of links visited in the end
    def crawler(self):
        try:
            num_visited = 0
            while len(self.repository) < self.max_links:
                try:
                    url = self.repository[num_visited]
     	            num_visited+=1
                    print(num_visited, "Visiting:", url)
                except IndexError:
                    print "Repository empty. Exiting"
		    return num_visited, self.repository
                    break
                status = self.parse_url(url)
		# Skip the url if it is not reachable / parsed or empty
                if status == 1:
                    print "ALARM : Could not parse the url : %s " % (url)
        except KeyboardInterrupt:
            print "INTERRUPT: You pressed Ctrl+c"
        finally:
            return num_visited, self.repository


if len(sys.argv) < 3:
	print "Usage : python webcrawler <url> <max_no_of_urls_to_crawl>  > repository_list.txt"
	sys.exit(1)

url = sys.argv[1]
max_links = int(sys.argv[2])
links = []
num_visited = 0
parser = UrlCrawler(url,max_links)
num_visited,links = parser.crawler()
print ('\n'.join(links))
print " %d links visited, %d links in repo: " %( num_visited, len(links))
                                 
