# -*- coding: utf-8 -*-
import sys, os
sys.dont_write_bytecode = True

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import ItemLoader
from soccer.items import ResultsItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request

from flask import session, request, url_for, flash
import re, json, time, urllib2, requests
from soccer import models
from soccer.settings import session, logger_present, logger_absent



spider_path = os.path.abspath(__name__).split('spiders')[0][:-1]
links = open(spider_path + '/spiders/links.txt').readlines()


class Missing_games_crawler(CrawlSpider):

    name            = "soccer_missings"
    allowed_domains = ["oddsportal.com"]
    start_urls      = links

    def parse(self, response):

        hxs    = HtmlXPathSelector(response)
        years  = hxs.select("//div[@class='main-menu2 main-menu-gray']/ul//a").extract()
        league = hxs.select("//div[@id='breadcrumb']/a/text()").extract()[2]
        group  = hxs.select("//div[@id='breadcrumb']/a/text()").extract()[3]

        for year in years:
        
            year_url = re.findall(re.compile('\"(.+?)\"'),  year)[0]
            year_num = re.findall(re.compile('>(.+?)</a>'), year)[0]
            new_url  = urljoin_rfc(get_base_url(response),  year_url)

            yield Request((new_url), meta = {'year':   year_num,
                                             'group':  group,
                                             'league': league}, callback=self.parse_year)

    def parse_year(self, response):

        hxs = HtmlXPathSelector(response)
        pages = list(set(hxs.select("//div[@id='pagination']/a/@href").extract()))
        pages_to_parse = [urljoin_rfc(get_base_url(response), page) for page in pages if 'page' in page]
        pages_to_parse.append(response.url + 'page/1')

        for page in pages_to_parse:
            yield Request(page, meta = {'year':   response.meta['year'],
                                        'group':  response.meta['group'],
                                        'league': response.meta['league']}, callback=self.parse_category)

    def parse_category(self, response):

        hxs = HtmlXPathSelector(response)
        tournament_links = hxs.select("//table[@id='tournamentTable']//a[not(@class)]/@href").extract()  
        
        for i, link in enumerate(tournament_links[1:]):
            new_url = urljoin_rfc(get_base_url(response), link)

            logger_present.info(new_url)