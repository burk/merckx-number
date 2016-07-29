# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class YearItem(scrapy.Item):
    year = scrapy.Field()
    url = scrapy.Field()
    teams = scrapy.Field()

class TeamItem(scrapy.Item):
    year = scrapy.Field()
    name = scrapy.Field()
    team = scrapy.Field()
    riders = scrapy.Field()

class RiderItem(scrapy.Item):
    rider = scrapy.Field()
    name = scrapy.Field()

