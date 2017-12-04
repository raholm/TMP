import json
from collections import defaultdict

import os
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess

from src.util.env import get_env_variable


class FunnyShortJokesJokeScraper(scrapy.Spider):
	name = "funnyshortjokes_bot"

	allowed_domains = ["funnyshortjokes.com"]

	custom_settings = {
		"ROBOTSTXT_OBEY": True
	}

	def __init__(self):
		super().__init__()

		self.jokes = defaultdict(dict)
		self.joke_ids = defaultdict(int)

		self.base_url = "https://www.funnyshortjokes.com"
		self.categories = ["Animal Jokes", "Dirty Jokes", "Disabled Jokes",
						   "Hilarious Jokes", "Pick Up Lines", "Political Jokes",
						   "Racist Jokes", "Relationship Jokes", "Religious Jokes",
						   "Sports Jokes", "Sports Jokes", "Surreal Jokes", "Yo Mama Jokes"]

	@classmethod
	def from_crawler(cls, crawler, *args, **kwargs):
		spider = super(FunnyShortJokesJokeScraper, cls).from_crawler(crawler, *args, **kwargs)
		crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
		return spider

	def start_requests(self):
		data_directory = get_env_variable("TMP_DATA_PATH") + "/funnyshortjokes_raw"
		parsed_categories = {category.split(".")[0].replace("_", " ")
							 for category in os.listdir(data_directory)}

		urls = [self.base_url + "/c/" + category.lower().replace(" ", "-")
				for category in self.categories if category not in parsed_categories]

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def spider_closed(self, reason):
		filename_template = get_env_variable("TMP_DATA_PATH") + "/funnyshortjokes_raw/%s.json"

		for category, jokes in self.jokes.items():
			filename = filename_template % category.replace(" ", "_")

			with open(filename, "w", encoding="utf-8") as outfile:
				json.dump(jokes, outfile, indent=4, sort_keys=True)

	def parse(self, response):
		print("Parsing %s..." % (response.url,))

		category = self._get_category(response)

		for post in response.xpath("//div[contains(@class, 'post-big')]"):
			id = self._get_id(post)
			premise = self._get_premise(post)
			punchline = self._get_punchline(post)

			self.joke_ids[category] += 1
			joke_id = self.joke_ids[category]

			self.jokes[category][joke_id] = {"id": id,
											 "premise": premise,
											 "punchline": punchline,
											 "category": category}

		if self._has_more_pages(response):
			url = self._get_next_page(response)
			if url is not None:
				yield scrapy.Request(url=url, callback=self.parse)

	def _get_id(self, post):
		try:
			return post.xpath("./@id").extract()[0]
		except IndexError:
			return None

	def _get_premise(self, post):
		try:
			return " ".join(post.xpath(".//div[@class='post-title-inner']/h3/text()").extract())
		except IndexError:
			return None

	def _get_punchline(self, post):
		try:
			return " ".join(post.xpath(".//div[@class='post-text']/p/text()").extract())
		except IndexError:
			return None

	def _get_category(self, response):
		url = response.url

		for category in self.categories:
			mod_category = "/c/" + category.lower().replace(" ", "-")
			if mod_category in url:
				return category

		return None

	def _has_more_pages(self, response):
		try:
			response.xpath("//span[@class='navigation-next']").extract()
			return True
		except Exception:
			return False

	def _get_next_page(self, response):
		try:
			return response.xpath("//span[@class='navigation-next']/a/@href").extract()[0]
		except IndexError:
			return None


def main():
	process = CrawlerProcess()
	process.crawl(FunnyShortJokesJokeScraper)
	process.start()


if __name__ == "__main__":
	main()
