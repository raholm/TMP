import json
import time
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from src.util.env import get_env_variable


class KickassHumorJokeScraper(object):
	def __init__(self):
		self.jokes = {}
		self.joke_id = 1

		self.click_limit = 5
		self.category = None

	def scrape(self, start_url):
		driver = webdriver.Firefox()
		driver.get(start_url)

		driver.find_element_by_xpath("//a[@title='Best Jokes of All Time']").click()

		self.category = self._get_category(driver)

		while self._is_more_jokes(driver):
			self._load_more_jokes(driver)

		self._get_jokes(driver)
		self._write_jokes_to_file()

		driver.close()

		return self.jokes

	def _get_jokes(self, driver):
		for joke in driver.find_elements_by_xpath("//div[@class='joke cfix expand']"):
			self._load_more_text(joke, self.click_limit)

			id = self._get_id(joke)
			punchline = self._get_punchline(joke)

			self.jokes[self.joke_id] = {"id": id,
										"punchline": punchline,
										"category": self.category}
			self.joke_id += 1

	def _is_more_jokes(self, driver):
		try:
			driver.find_element_by_xpath(
				"//div[@id='jokes']/p").get_attribute("text")
			return False
		except NoSuchElementException:
			return True

	def _load_more_jokes(self, driver):
		driver.find_element_by_xpath("//div[@class='loadMore']/a").click()

	def _load_more_text(self, joke, limit):
		try:
			joke.find_element_by_xpath(".//span[@class='read-more']/a").click()
			time.sleep(0.15)
			if joke.find_element_by_xpath(".//span[@class='read-more']").is_displayed():
				self._load_more_text(joke, limit - 1)
		except NoSuchElementException:
			pass

	def _get_id(self, joke):
		return joke.get_attribute("data-jokeid")

	def _get_punchline(self, joke):
		return joke.find_element_by_xpath("./p/a").get_attribute("text")

	def _get_category(self, driver):
		return driver.current_url.split("/")[-1]

	def _write_jokes_to_file(self):
		file = get_env_variable("TMP_DATA_PATH") + "/kickasshumor_raw/%s.json" % self.category.replace("-", "_")

		with open(file, "w", encoding="utf-8") as outfile:
			json.dump(self.jokes, outfile, indent=4, sort_keys=True)


def main():
	id_to_category = {1: "funny_chuck_norris_jokes",
					  2: "funny_yo_momma_jokes",
					  3: "funny_blonde_jokes",
					  4: "funny_one_liner_jokes",
					  5: "funny_short_jokes",
					  6: "funny_long_jokes",
					  7: "funny_redneck_jokes",
					  9: "funny_dirty_jokes",
					  10: "funny_racial_jokes",
					  12: "funny_comebacks",
					  14: "funny_pick_up_lines",
					  15: "funny_celebrity_jokes",
					  16: "funny_anti_humor_jokes",
					  17: "funny_animal_jokes",
					  18: "funny_puns"}

	scraped_categories = {category.split(".")[0]
						  for category in os.listdir(get_env_variable("TMP_DATA_PATH") + "/kickasshumor_raw")}

	category_ids = [id for id, category in id_to_category.items()
					if category not in scraped_categories]

	base_url = "https://www.kickasshumor.com/c/%i"
	urls = [base_url % id for id in category_ids]

	for url in urls:
		scraper = KickassHumorJokeScraper()
		jokes = scraper.scrape(url)
		print(len(jokes))


if __name__ == "__main__":
	main()
