# -*- coding: utf-8 -*-
import scrapy


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/114285']

    def parse(self, response):
        # text() 获取文本
        x_selector = response.xpath('//*[@id="post-114285"]/div[1]/h1/text()')
        # scrapy shell url 来调试获取路径
        created_at = (
            response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()')
                    .extract()[0].strip()[:10]
        )

        pass
