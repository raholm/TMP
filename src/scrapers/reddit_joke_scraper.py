import json
import time

import os
from joblib import Parallel, delayed
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from src.util.env import get_env_variable


class RedditJokeScraper(object):
	def __init__(self, valid_domains, num_pages=2, expand_attempts=5,
				 age_restriction=False):
		if isinstance(valid_domains, (list, tuple)):
			self.valid_domains = valid_domains
		else:
			self.valid_domains = [valid_domains]

		self.num_pages = num_pages
		self.expand_attempts = expand_attempts
		self.age_restriction = age_restriction

	def scrape(self, start_url):
		driver = webdriver.Firefox()
		driver.get(start_url)

		jokes = []
		pages_accessed = 0

		if not self.age_restriction:
			self._click_age_button_if_exists(driver)
		elif self._is_age_restricted(driver):
			driver.close()
			return jokes

		start = time.time()

		while pages_accessed < self.num_pages:
			for id, (premise, punchline), domain in self._get_jokes(driver):
				if premise is None and punchline is None:
					continue

				jokes.append((id, premise, punchline, domain))

			next_page = self._get_next_page(driver)

			if next_page is None:
				break

			pages_accessed += 1

			driver.get(next_page)

		end = time.time()

		driver.close()

		print(start_url)
		print("Total number of pages:", pages_accessed + 1)
		print("Total time in seconds:", end - start)

		if pages_accessed > 0:
			print("Average time per page in seconds:", (end - start) / pages_accessed)

		filename = start_url.split("/")[-1] + ".json"
		self._write_jokes_to_file(jokes, filename)

		return jokes

	def _get_jokes(self, driver):
		for entry in driver.find_elements_by_xpath("//div[@class='entry unvoted']"):
			domain = self._get_domain(entry)

			if not self._is_valid_domain(domain):
				continue

			button = self._get_button(entry)

			if button is None:
				continue

			yield self._get_id(entry), self._get_joke(entry, button, self.expand_attempts), domain

	def _get_joke(self, entry, button, attempts_left):
		if attempts_left == 0:
			return None, None

		try:
			premise = entry.find_element_by_xpath(".//a").text
			punchline = entry.find_element_by_xpath(".//div[@class='md']/p").text
			return premise, punchline
		except NoSuchElementException:
			button.click()
			time.sleep(0.15)
			return self._get_joke(entry, button, attempts_left - 1)

	def _get_domain(self, entry):
		try:
			return entry.find_element_by_xpath(".//span[@class='domain']/a").get_attribute("href")
		except NoSuchElementException:
			return None

	def _get_id(self, entry):
		try:
			return entry.find_element_by_xpath("./div/p/a").get_attribute("href").split("/")[-3]
		except NoSuchElementException:
			return None

	def _is_valid_domain(self, domain):
		if domain is None:
			return False

		return any(valid_domain in domain for valid_domain in self.valid_domains)

	def _get_next_page(self, driver):
		try:
			return driver.find_element_by_xpath("//span[@class='next-button']/a").get_attribute("href")
		except NoSuchElementException:
			return None

	def _get_button(self, entry):
		try:
			return entry.find_element_by_xpath(".//div[contains(@class, 'expando-button')]")
		except NoSuchElementException:
			return None

	def _click_age_button_if_exists(self, driver):
		try:
			driver.find_element_by_xpath("//button[@name='over18'][@value='yes']").click()
		except NoSuchElementException:
			pass

	def _is_age_restricted(self, driver):
		try:
			driver.find_element_by_xpath("//button[@name='over18'][@value='yes']")
			return True
		except NoSuchElementException:
			return False

	def _write_jokes_to_file(self, jokes, filename):
		joke_id = 1
		jokes_dict = {}

		for id, premise, punchline, subreddit in jokes:
			jokes_dict[joke_id] = {"id": id,
								   "premise": premise,
								   "punchline": punchline,
								   "subreddit": subreddit}
			joke_id += 1

		file = get_env_variable("TMP_DATA_PATH") + "/reddit_raw/%s" % filename
		with open(file, "w", encoding="utf-8") as outfile:
			json.dump(jokes_dict, outfile, indent=4, sort_keys=True)


def run_joke_scraper():
	base_url = "https://www.reddit.com/r/"
	subreddits = ["Jokes", "DirtyJokes", "cleanjokes", "AntiJokes", "Antihumor",
				  "darkjokes", "MeanJokes", "AntiAntiJokes", "dadjokes", "ProgrammerHumor",
				  "MathJokes", "MommaJokes", "3amjokes", "ShortCleanFunny", "badjokes",
				  "deadbabyjokes", "DarkHumor", "Punny", "pun", "ScienceJokes", "chemistryjokes",
				  "intellectualdadjokes", "ProgrammerDadJokes", "nsfwdadjokes",
				  "dadjokesinhistory", "Hearthstonedadjokes", "dadsouls", "warcraftdadjokes",
				  "dota2dadjokes", "DestinyDadJokes", "FFXIVDadjokes", "Falloutdadjokes", "DMDadJokes",
				  "skyrimdadjokes", "OverwatchDadjokes", "DarkDadJokes", "CivDadJokes", "TrahearneJokes",
				  "StarWarsDadJokes", "eu4dadjokes", "shubreddit", "momjokes"]

	subreddits_scraped = {filename.split(".")[0] for filename in os.listdir("../data/reddit_raw")}

	start_urls = [base_url + subreddit for subreddit in subreddits if subreddit not in subreddits_scraped]

	scraper = RedditJokeScraper(subreddits, 1000)
	jokes = Parallel(n_jobs=1)(delayed(scraper.scrape)(start_url) for start_url in start_urls)


# formatted_jokes = {}
# joke_id = 1
#
# for subreddit_jokes in jokes:
# 	for id, premise, punchline, subreddit in subreddit_jokes:
# 		formatted_jokes[joke_id] = {"id": id,
# 									"premise": premise,
# 									"punchline": punchline,
# 									"subreddit": subreddit}
# 		joke_id += 1
#
# with open("../data/jokes.json", "w", encoding="utf-8") as outfile:
# 	json.dump(formatted_jokes, outfile, indent=4, sort_keys=True)

def get_reddit_joke_files():
	directory = get_env_variable("TMP_DATA_PATH") + "/reddit_raw"
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".json"):
				yield os.path.join(root, file)


def get_all_reddit_jokes():
	jokes = {}

	for file in get_reddit_joke_files():
		with open(file, "r") as infile:
			data = json.load(infile)

		for key, value in data.items():
			id = value["id"]
			premise = value["premise"]
			punchline = value["punchline"]
			subreddit = value["subreddit"]

			jokes[id] = {"premise": premise,
						 "punchline": punchline,
						 "subreddit": subreddit}

	print(len(jokes))

	return jokes


def main():
	# run_joke_scraper()
	get_all_reddit_jokes()


# with open("../data/jokes.json", "r") as infile:
# 	jokes = json.load(infile)
#
# print(len(jokes))


if __name__ == "__main__":
	main()
