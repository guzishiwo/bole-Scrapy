# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeLine(object):
    def __init__(self):
        self.connection = pymysql.connect("127.0.0.1", "root", "",
                                          database="spider",
                                          charset='utf8mb4')
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into bole_article 
            (title, created_date, main_image_url, vote_num, bookmark_num, content, tags) 
            values  (%s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item['title'], item['created_date'],
                             item['main_image_url'],
                             item['vote_num'], item['bookmark_num'],
                             item['content'],
                             item['tags']))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()


class MysqlTwistedPipeLine(object):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        config = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DB_NAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASS'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool("pymysql", **config)
        return cls(db_pool)

    def process_item(self, item, spider):
        # 使用twisted变成异步执行
        query = self.db_pool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
            insert into bole_article 
            (title, created_date, main_image_url, vote_num, bookmark_num, content, tags) 
            values  (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql,
                       (item['title'], item['created_date'],
                        item['main_image_url'],
                        item['vote_num'], item['bookmark_num'],
                        item['content'],
                        item['tags']))

    def close_spider(self, spider):
        self.db_pool.close()
