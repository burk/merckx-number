# -*- coding: utf-8 -*-
import scrapy
from pcs_scraper.items import YearItem, TeamItem, RiderItem
import re

class PCSSpider(scrapy.Spider):
    name = 'pcs'

    allowed_domains = ['procyclingstats.com']

    start_urls = [
            'http://www.procyclingstats.com/teams.php?c=1&season=2016'
            ]

    def parse(self, response):
        yield scrapy.Request(response.url,
                callback=self.parse_year_continue)

    def parse_year_continue(self, response):
        year = re.findall(r"\d\d\d\d", response.url)[0]
        y = YearItem()
        y['year'] = year
        y['teams'] = []
        team_hrefs = response.xpath(
                '//a[@class="black"][contains(@href, "team")]/@href')
        for href in team_hrefs:
            url = response.urljoin(href.extract())
            team = href.extract()
            team = team.replace("team/", "").strip()
            y['teams'].append(team)
            yield scrapy.Request(url, callback=self.parse_team)

        if len(y['teams']) == 0: # or int(year) < 2013:
            yield
        else:
            yield y
            next_url = response.url
            next_url = next_url.replace(year, str(int(year) - 1))
            
            yield scrapy.Request(next_url,
                    callback=self.parse_year_continue)


    def parse_team(self, response):
        name = response.xpath('//h1/text()')[0].extract()[10:]
        year = response.xpath('//h1/text()')[0].re(r'\d\d\d\d')[0]
        name.replace(u"\xc2\xa0", "")
        #name.replace(u" (WT)", "")
        #name.replace(u" (PCT)", "")
        #name.replace(u" (UCI)", "")
        #name.strip()
        rider_hrefs = response.xpath('//div[contains(@class, "name")]//a[contains(@class, "rider")][contains(@href, "rider")]/@href')
        team = re.findall(r"team/(.*)", response.url)[0].strip()

        if name.strip() == "":
            print "YER:", year
            print "teamname", name
            print "teamslug", team
            print "HREFS", rider_hrefs

        t = TeamItem()
        t['name'] = name
        t['team'] = team
        t['riders'] = []
        t['year'] = year.strip()

        for href in rider_hrefs:
            url = response.urljoin(href.extract())
            rider = href.extract()
            rider = rider.replace("rider/", "").strip()
            t['riders'].append(rider)
            print "PARSING RIDER: ", url
            yield scrapy.Request(url, callback=self.parse_rider)

        if len(t['riders']) == 0:
            yield

        yield t

    def parse_rider(self, response):
        name = response.xpath('//h1/text()')[0].extract()
        name = name.replace(u"»", "")
        name = name.replace(u'\xa0', u' ')
        name = name.replace("  ", " ").strip()

        rider = response.xpath('//a[@class="cur"]/@href')[0].extract()
        rider = rider.replace("rider/", "")
        #print "riderslug:", rider
        r = RiderItem()
        r['name'] = name
        r['rider'] = rider.strip()

        yield r

