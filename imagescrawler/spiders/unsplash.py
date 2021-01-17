from scrapy import Spider, Request
import json


class UnsplashSpider(Spider):
    name = 'unsplash'
    allowed_domains = ['unsplash.com']
    start_urls = ['http://unsplash.com/']
    topics = [
        'wallpapers',
        'nature',
        'people',
        'architecture',
        'current-events',
        'experimental',
        'fashion',
        'film',
        'health',
        'interiors',
        'street-photography',
        'technology',
        'travel',
        'textures-patterns',
        'business-work',
        'animals',
        'food-drink',
        'athletics',
        'spirituality',
        'arts-culture',
        'history',
    ]
    page_max = 1000
    index_url_pattern = 'https://unsplash.com/napi/topics/{topic}/photos?page={page}&per_page={per_page}'
    detail_url_pattern = 'https://unsplash.com/napi/photos/{id}'
    related_url_pattern = 'https://unsplash.com/napi/photos/{id}/related'
    custom_settings = {
        'MONGODB_DATABASE_NAME': 'images',
        'MONGODB_COLLECTION_NAME_DEFAULT': 'unsplash',
        'IMAGES_STORE': 'images/unsplash'
    }
    
    def start_requests(self):
        for topic in self.topics:
            for page in range(1, self.page_max):
                index_url = self.index_url_pattern.format(
                    topic=topic,
                    page=page,
                    per_page=10
                )
                yield Request(index_url, callback=self.parse_index)
    
    def parse_index(self, response):
        items = json.loads(response.text)
        for item in items:
            id = item.get('id')
            detail_url = self.detail_url_pattern.format(id=id)
            self.logger.debug('detail url %s', detail_url)
            yield Request(detail_url, callback=self.parse_detail, priority=10)
            related_url = self.related_url_pattern.format(id=id)
            yield Request(related_url, callback=self.parse_related, priority=12)
    
    def parse_related(self, response):
        items = json.loads(response.text)
        for item in items.get('results'):
            id = item.get('id')
            detail_url = self.detail_url_pattern.format(id=id)
            self.logger.debug('related detail url %s', detail_url)
            yield Request(detail_url, callback=self.parse_detail, priority=10)
    
    def parse_detail(self, response):
        data = json.loads(response.text)
        yield data
