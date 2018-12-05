# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import XPathItemLoader, ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def load_created_date(created_at):
    created_at = created_at.strip()[:10]
    if created_at and '/' in created_at:
        created_date = datetime.strptime(created_at, '%Y/%m/%d').date()
    else:
        created_date = datetime.now().date()
    return created_date


idg_re = re.compile(r'.*(\d+).*')


def extract_digit(s):
    match_str = idg_re.match(s or '')
    num = 0
    if match_str:
        num = int(match_str.group(1))
    return num


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class BoleArticleItem(scrapy.Item):
    title = scrapy.Field(
    )
    created_date = scrapy.Field(
        input_processor=MapCompose(load_created_date)
    )
    url = scrapy.Field()
    # main_image_url = scrapy.Field()
    vote_num = scrapy.Field(
        input_processor=MapCompose(extract_digit)
    )
    bookmark_num = scrapy.Field(
        input_processor=MapCompose(extract_digit)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(lambda x: "" if '评论' in x else x.replace(',', '')),
        output_processor=Join(',')
    )
    content = scrapy.Field()
