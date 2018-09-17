# -*- coding: utf-8 -*-
import scrapy

class LonelyplanetSpider(scrapy.Spider):
    ''' scrape text descriptions from travel pages '''

    name = 'lonelyplanet'
    allowed_domains = ['lonelyplanet.com', 'www.lonelyplanet.com']
    start_urls = ['https://www.lonelyplanet.com/places']

    def parse(self, response):
        ''' pull countries out of the lowest level places page '''
        # open country pages
        countries = response.xpath(
            '//div[@class="place-list__section context--content"]//a/@href')
        for country in countries:
            # go to the list of cities
            country = country.get() + '/places'
            country_page = response.urljoin(country)
            yield scrapy.Request(country_page, callback=self.parse_country)


    def parse_country(self, response):
        ''' from a country page, open individual cities '''
        cities = response.xpath(
            '//div[@class="card__mask"]//a/@href')
        for city in cities:
            city = city.get()
            city_page = response.urljoin(city)
            yield scrapy.Request(city_page, callback=self.parse_place)


    def parse_place(self, response):
        ''' from a city/place page, open restaurants '''
        restaurants = response.xpath(
            '//li[@class="food-and-drink__item"]//a/@href')
        for restaurant in restaurants:
            restaurant = restaurant.get()
            restaurant_page = response.urljoin(restaurant)
            yield scrapy.Request(
                restaurant_page,
                callback=self.parse_restaurant)


    def parse_restaurant(self, response):
        ''' finally, we have a restauarant review '''
        name = response.xpath(
            '//h1[@class="styles__heading___mD4_3"]/text()').get()
        review_pieces = response.xpath(
            '//div[@class="styles__textArticle___OqHJQ ' \
            'styles__reviewBodyText___2rexg"]//*/text()')
        review = ' '.join(l.get() for l in review_pieces)
        placename = response.xpath(
            '//a[@itemtype="http://schema.org/Place"]//span/text()')
        placename = ', '.join(p.get() for p in placename)
        yield {
            'name': name,
            'review': review,
            'location': placename,
            'url': response.url,
        }

