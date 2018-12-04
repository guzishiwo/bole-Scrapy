# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse
from datetime import datetime
from ArticleSpider.items import BoleArticleItem

idg_re = re.compile(r'.*(\d+).*')


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章的页面的url并交给scrapy不下载后解析
        2.
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
        article_item = BoleArticleItem()
        title = (
            response.xpath('//div[@class="entry-header"]/h1/text()')
                    .extract_first('')
        )
        # scrapy shell url 来调试获取路径
        created_at = (
            response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()')
                    .extract()[0].strip()[:10]
        )
        if created_at:
            created_date = datetime.strptime(created_at, '%Y/%m/%d').date()
        else:
            created_date = datetime.now().date()
        vote_num = int(response
                       .xpath('//span[contains(@class, "vote-post-up")]/h10/text()')
                       .extract_first('0'))
        book_mark_string = (
            response.xpath('//span[contains(@class, "bookmark-btn")]/text()')
                    .extract_first('')
        )
        bookmark_m = idg_re.match(book_mark_string)
        bookmark_num = 0
        if bookmark_m:
            # group(0)匹配所有字符串，对吧，good
            bookmark_num = bookmark_m.group(1)

        content = response.xpath('//div[@class="entry"]').extract()[0]
        content_tag_lst = response.xpath(
            '//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        content_tag = ''.join(
            [i for i in content_tag_lst if not ('评论' in i)])

        article_item['title'] = title
        article_item['url'] = response.url
        article_item['created_date'] = created_date
        article_item['main_image_url'] = response.meta.get('main_image_url','')
        article_item['vote_num'] = vote_num
        article_item['bookmark_num'] = bookmark_num
        article_item['content'] = content
        article_item['tags'] = content_tag

        # 会传递到pipeline
        yield article_item
