import json
import time

from joblib import Parallel, delayed
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class JokeExtractor(object):
	def __init__(self, valid_domains, num_pages):
		if isinstance(valid_domains, (list, tuple)):
			self.valid_domains = valid_domains
		else:
			self.valid_domains = [valid_domains]

		self.num_pages = num_pages

	def extract(self, start_url):
		driver = webdriver.Firefox()
		driver.get(start_url)

		self._click_age_button_if_exists(driver)

		jokes = []
		pages_accessed = 0

		start = time.time()

		while pages_accessed < self.num_pages:
			for (premise, punchline), domain in self._get_jokes(driver):
				if premise is None or punchline is None:
					continue

				jokes.append((premise, punchline, domain))

			next_page = self._get_next_page(driver)
			pages_accessed += 1

			if next_page is None:
				continue

			driver.get(next_page)

		end = time.time()

		driver.close()

		print("Total time in seconds:", end - start)

		if pages_accessed > 0:
			print("Average time per page in seconds:", (end - start) / pages_accessed)

		return jokes

	def _get_jokes(self, driver):
		for entry in driver.find_elements_by_xpath("//div[@class='entry unvoted']"):
			domain = self._get_domain(entry)

			if not self._is_valid_domain(domain):
				continue

			button = self._get_button(entry)

			if button is None:
				continue

			yield self._get_joke(entry, button, 3), domain

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


def run_extraction():
	base_url = "https://www.reddit.com/r/"
	subreddits = ["Jokes", "DirtyJokes", "cleanjokes", "AntiJokes", "Antihumor",
				  "darkjokes", "MeanJokes", "AntiAntiJokes", "dadjokes", "ProgrammerHumor",
				  "MathJokes", "MommaJokes", "3amjokes", "ShortCleanFunny", "badjokes",
				  "deadbabyjokes", "DarkHumor", "Punny", "pun", "ScienceJokes", "chemistryjokes",
				  "science_jokes", "intellectualdadjokes", "ProgrammerDadJokes", "nsfwdadjokes",
				  "dadjokesinhistory", "Hearthstonedadjokes", "dadsouls", "warcraftdadjokes",
				  "dota2dadjokes", "DestinyDadJokes", "FFXIVDadjokes", "Falloutdadjokes", "DMDadJokes",
				  "skyrimdadjokes", "OverwatchDadjokes", "DarkDadJokes", "CivDadJokes", "TrahearneJokes",
				  "StarWarsDadJokes", "eu4dadjokes", "shubreddit", "momjokes"]
	start_urls = [base_url + subreddit for subreddit in subreddits]

	extractor = JokeExtractor(subreddits, 1)

	jokes = Parallel(n_jobs=-1)(delayed(extractor.extract)(start_url) for start_url in start_urls[-1:])

	formatted_jokes = {}
	joke_id = 1

	for subreddit_jokes in jokes:
		for premise, punchline, subreddit in subreddit_jokes:
			formatted_jokes[joke_id] = {"premise": premise.strip(),
										"punchline": punchline.strip(),
										"subreddit": subreddit}
			joke_id += 1

	with open("../data/jokes.json", "w", encoding="utf-8") as outfile:
		json.dump(formatted_jokes, outfile, indent=4, sort_keys=True)


def main():
	run_extraction()


# with open("../data/jokes.json", "r") as infile:
# 	jokes = json.load(infile)
#
# print(len(jokes))


if __name__ == "__main__":
	main()
