import scrapy
import json
import sys
sys.path.insert(0, 'C:/Users/stepanchenko_em/Desktop/telegram-bot/telegram-bot-04/scraping_info/scraping_info')
from items import ScrapingInfoItem

from twisted.internet import reactor
from twisted.internet.task import deferLater
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

class AfishaSpider(scrapy.Spider):
	name = "afisha"
	start_urls = [
		'https://www.culture.ru/afisha/tomsk',
		#'https://www.culture.ru/afisha/moskva-i-podmoskove',
	]
	
	# Счётчик страниц. Первая следующая страница
	page_counter = 2
	i = 0
	
	# Словарь для хранения всех остальных словарей
	__json_dict = {}
	
	PAGES = './/nav[@class="pagination"]/a[@class="pagination_item"]/text()'
	INFO_CARD = '//div[@class="entity-cards_item col"]'
	JSON_SCRIPT = './/script[@type="application/ld+json"]/text()'
	NEXT_PAGE_SELECTOR = './/nav[@class="pagination"]/a[@class="pagination_item"]/@href'
	
	def parse(self, response):	
		items = ScrapingInfoItem()
			
		# Получаем всю информацию о карточке события
		item_cards = response.xpath(self.INFO_CARD)
		
		# Перебераем все карточки с информацией на одной странице сайта
		for card in item_cards:
			self.i += 1
			
			# Получаем скрипт-строку с JSON с сайта
			item = card.xpath(self.JSON_SCRIPT).extract()
			
			# Преобразуем скрипт-строку в словарь
			j = json.loads(item[0])
			
			# Добавляем словарь с JSON в словарь
			self.__json_dict[self.i] = j
			
			# Добавляем элементы JSON в Items
			items['title'] = self.__json_dict[self.i]["name"]
			items['description'] = self.__json_dict[self.i]["description"]
			items['location'] = self.__json_dict[self.i]["location"]["address"]
			items['url'] =  self.__json_dict[self.i]["url"]
			yield items
							
		try:
			# Получаем список страниц и определяем положение текущей страницы в нём
			list_of_pages = response.xpath(self.PAGES).extract()
			link_position = list_of_pages.index(str(self.page_counter))
				
			# Вытягиваем все ссылки на следующие страницы	
			next_page = response.xpath(self.NEXT_PAGE_SELECTOR)[link_position].extract()
			if next_page:
				self.page_counter += 1
				yield scrapy.Request(
						response.urljoin(next_page),
						callback = self.parse
				)

		except ValueError:
			print("All infos scraped.")
			

def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)
    
def crash(failure):
    print('oops, spider crashed')
    print(failure.getTraceback())
	
process = CrawlerProcess(get_project_settings())

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting 10 seconds before restart...'))
    deferred.addErrback(crash)  				# <-- add errback here
    deferred.addCallback(sleep, seconds=10)
    deferred.addCallback(_crawl, spider)
    return deferred

_crawl(None, AfishaSpider)
process.start()
