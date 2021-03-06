# -*- coding: utf-8 -*-
import scrapy

from scrapy_charlie_chaplin.items import ScrapyCharlieChaplinItem


# spider_with_thumbnail
# extends scrapy.Spider
# 
# Given multiple start_urls, 1 default parse() function, 
# and 1 customized parse_item() function
# The crawler will first use parse() function to process the 
# Item List, then use callback parse_item() function to 
# process the Item Page. 
#
# parse() is auto invoked by the crawler, and parse_item() 
# is always invoked from inside parse() function. 
# 
# Most important is the use of request.meta, which passes in 
# thumbnail to the request from Item List Page, to the 
# parse_item() function
#
# i.e. this code: request.meta['item'] = item

class SpiderWithThumbnail(scrapy.Spider):
    name = "spider_with_thumbnail"
    allowed_domains = ["archive.org"]
    start_urls = (
        'https://archive.org/search.php?query=subject%3A%22Charlie+Chaplin%22&and%5B%5D=mediatype%3A%22movies%22',
        'https://archive.org/search.php?query=subject%3A%22Charlie+Chaplin%22&and%5B%5D=mediatype%3A%22movies%22&page=2',
        'https://archive.org/search.php?query=subject%3A%22Charlie+Chaplin%22&and%5B%5D=mediatype%3A%22movies%22&page=3',
    )
    
    # I could also have done it smarter: in parse(), add:
    # yield scrapy.Request(url, callback=self.parse)
    # But I've been too lazy to do so. Thus I put multiple urls in start_urls
    # http://doc.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.closed
    
    def parse(self, response):
        results = response.xpath('//div[@class="results"]/div/div[@class="C234"]/div[@class="item-ttl C C2"]/a')
        
        for result in results:
            item = ScrapyCharlieChaplinItem()
            thumbnail = result.xpath('div[@class="tile-img"]/img/@source').extract()
            
            item_link = result.xpath('@href').extract()
            if (item_link and len(item_link) is not 0 and 
                thumbnail and len(thumbnail) is not 0):
                request = scrapy.Request('https://archive.org' + item_link[0],
                                         callback=self.parse_item)
                item['thumbnail'] = thumbnail[0]
                request.meta['item'] = item
                yield request

    def parse_item(self, response):
        # get the item from response, passed throw from parse()
        # the thumbnail is contained in this 
        item = response.meta['item']
        
        item['title'] = response.xpath('//div[@class="relative-row row"]/div/h1/text()').extract()
        # if title does not exist, return no item
        if (not item['title']):
          return
        else:
          self.logger.info('now crawling item page: %s', response.url)

        item['description'] = response.xpath('//div[@class="relative-row row"]/div/div[@id="descript"]/text()').extract()
        if (not item['description']):
          item['description'] = response.xpath('//div[@class="relative-row row"]/div/div[@id="descript"]/p/text()').extract()

        item['date'] = response.xpath('//div[@class="relative-row row"]/div/div[@class="boxy"]/div[@class="boxy-ttl"]/text()').extract()
        item['video_url'] = response.xpath('//div[@class="relative-row row"]/div/div[@class="boxy quick-down"]/div[@class="format-group"]/a[@class="format-summary download-pill"]/@href').extract()
        if (not item['video_url']):
          return

        return item
