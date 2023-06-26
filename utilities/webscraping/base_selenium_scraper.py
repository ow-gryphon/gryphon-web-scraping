import abc
import time
from random import randint

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path



class BaseScraper(abc.ABC):
    """
    Class to wrap Selenium and to scrape websites.
    """

    @property
    def output_directory(self):
        return Path('data/output')

    def __init__(self, headless_mode=True):
        options = webdriver.ChromeOptions()
        options.add_argument('incognito')
        if headless_mode:
            options.add_argument('headless')
        self._browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def clean_string(self, dirty_string):
        """

        :param dirty_string:
        :return: String with all whitespace (trailing and interior) and double quotes removed
        """
        return dirty_string.strip().replace('"', "").replace(" ", "").replace("#","")

    def get_page_source(self, url):
        """
        Method to obtain the source HTML of a page. There are re-tries as sometimes we observed weird non-deterministic
        behaviours.

        :param url: target URL
        :return: page HTML
        """
        print('opening: %s' % (url,))
        self._browser.get(url)

        # Put counter to make sure we get the same page each time - there were case of non-deterministic page loads.
        # Global counter is to avoid infinite re-loading
        prev_page_source = None
        equals_counter = 0
        global_counter = 0
        while True:
            page_source = self._browser.page_source
            global_counter += 1
            if page_source == prev_page_source:
                equals_counter += 1
            else:
                equals_counter = 0
            if equals_counter == 5:
                break
            prev_page_source = page_source
            time.sleep(0.1)
            if global_counter > 100:
                break
        return page_source
        

    def wind_down_browser(self):
        """
        Function to shut down browser when finished scraping

        :return:
        """
        try:
            self._browser.quit()
        except Exception:
            # Browser may already be closed down if a crash has happened
            pass

    def select_value_dropdown_id(self, id, value_to_select):
        """
        Function to select a value from a dropdown menu.

        :param id:
        :param value_to_select:
        :return:
        """
        select_reg_year = Select(self._browser.find_element_by_id(id))
        select_reg_year.select_by_value(value_to_select)

    def click_javascript_element(self, id):
        """
        Some elements are not directly clickable on the page as they appear and are controlled through JavaScript.
        So must use the Javascript engine to render them.

        :param id:
        :return:
        """
        element = self._browser.find_element_by_id(id)
        self._browser.execute_script("arguments[0].click();", element)

    def delete_cookies(self):
        """
        Function to clear all cookies.

        :return:
        """
        self._browser.delete_all_cookies()

    def randomly_select_dropdown_id(self, id, start_index=0):
        """
        Function to randomly select an item from the dropdown menu.

        :param id: HTML ID of the dropdown
        :param start_index: where to start the random selection from
        :return: None - selects value
        """
        ddwn_menu = Select(self._browser.find_element_by_id(id))
        ddwn_menu.select_by_index(randint(start_index, len(ddwn_menu.options) - 1))


class MyScraper(BaseScraper):

    def website_specific_actions(self, params):
        # Implement the website-specific actions here
        pass
        
    def scrape_website(self, url, params):
        """
        Full flow to scrape the website.

        :return:
        """
        self.get_page_source(url)
        self.website_specific_actions(params)