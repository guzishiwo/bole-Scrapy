# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader, XPathItemLoader
from datetime import datetime

from scrapy.loader.processors import TakeFirst, Join

from ArticleSpider.items import BoleArticleItem, ArticleItemLoader



class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """ 1. 获取文章的页面的url并交给scrapy不下载后解析 2.
        :param response:
        :return:
        """
        # 获取下载
        post_nodes = response.xpath('//div[@class="post floated-thumb"]')

        for post_node in post_nodes:
            post_url = post_node.xpath('.//div/a/@href').extract_first()
            image_url = post_node.xpath('.//div/img/@src').extract_first()
            # yield 自动下载
            yield Request(url=post_url,
                          meta={
                              "main_image_url": image_url,
                          },
                          callback=self.extract_post_field)

        next_url = (response
                    .xpath('//a[@class="next page-numbers"]/@href')
                    .extract_first(''))
        if next_url:
            yield Request(url=next_url, callback=self.parse)

        # 提取下一页进行下载

    def extract_post_field(self, response):
        # # scrapy shell url 来调试获取路径

        item_loader = ArticleItemLoader(item=BoleArticleItem(),  response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('created_date', '//*[@class="entry-meta-hide-on-mobile"]/text()')
        # item_loader.add_value('main_image_url',
        #                       response.meta.get('main_image_url') or '')
        item_loader.add_xpath('vote_num',
                              '//span[contains(@class, "vote-post-up")]/h10/text()')
        item_loader.add_xpath('bookmark_num',
                              '//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')
        item_loader.add_xpath('tags', '//*[@class="entry-meta-hide-on-mobile"]/a/text()')

        article_loader = item_loader.load_item()

        yield article_loader
