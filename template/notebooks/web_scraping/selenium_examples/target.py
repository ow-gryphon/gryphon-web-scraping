import os
from pathlib import Path

import pandas as pd
from selenium.common.exceptions import NoSuchElementException

from src.base_scraper import BaseScraper

import time


class Target(BaseScraper):
    @property
    def output_directory(self):
        return Path('data/output/target')

    def filename_generator(self, name: str):
        return '{}.csv'.format(self.clean_string(name))

    def get_empty_dataframe(self):
        return pd.DataFrame([], columns=['category',
                                         'item_number',
                                         'item_name',
                                         'regular_price',
                                         'sale_price',
                                         'promo'])

    def website_specific_actions(self, params=None):
        """
        Function to do all the set of actions (clicks, form filling etc.) required for a website. To be overridden
        by child website-specific classes.

        :return:
        """
        # self.close_splash()
        self._browser.maximize_window()
        self.navigate_to_required_clothing_sections()
        self.delete_cookies()

    # def close_splash(self):
    #     button = self._browser.find_element_by_xpath("//button[@data-click='close']")
    #     button.click()

    def navigate_to_required_clothing_sections(self):
        print('Finding link elements')
        links = self._browser.find_elements_by_xpath("//a[contains(@data-lnk,'Plus Size')]")
        print('{} links found...'.format(len(links)))

        link_texts = [link.text for link in links]
        link_urls = [link.get_attribute('href') for link in links]

        for link_url, link_text in zip(link_urls, link_texts):
            filename: Path = self.output_directory / self.filename_generator(link_text)
            if filename.exists():
                print('Filename {} already exists, skipping...'.format(filename))
                pass
            else:
                # navigate to each sub-clothing link
                print('Navigating to {} : {}'.format(link_text, link_url))
                # return the list of items on all pages
                items = self.get_empty_dataframe()
                more_pages = True
                counter = 1
                next_href = link_url
                while more_pages:
                    print('Getting page {}...'.format(counter))
                    self.get_page_source(next_href)
                    items = items.append(self.get_current_page_items(self.clean_string(link_text)))
                    try:
                        next_link = self._browser.find_element_by_xpath("//a[@data-test='next']")
                        next_href = next_link.get_attribute("href")
                        if next_href == "" or next_href is None:
                            more_pages = False
                        else:
                            counter += 1
                    except:
                        more_pages = False
                self.save_data(items, filename)

    def get_current_page_items(self, category):
        outermost_xpath = "//div[@data-test='product-details']"
        product_id_string = "href"
        product_name_xpath = ".//a[@data-test='product-title']"
        product_price_xpath = ".//span[@data-test='product-price']"
        product_no_sale_price_xpath = "./span[@class='standardprice']"
        product_regular_price_xpath = "./s"
        product_sale_price_xpath = "./span"
        product_promo_xpath = "./h3[3]"

        product_web_elements = self._browser.find_elements_by_xpath(outermost_xpath)
        print('Finding {} element details'.format(len(product_web_elements)))

        page_items = []
        for element in product_web_elements:
            # print('Selecting the elements of {}'.format(element))

            product_name_element = element.find_element_by_xpath(product_name_xpath)
            product_id = product_name_element.get_attribute(product_id_string)
            product_name = self.clean_string(product_name_element.get_attribute('innerHTML'))
            product_price_element = element.find_element_by_xpath(product_price_xpath)
            product_reg_price = self.clean_string(product_price_element.get_attribute('innerHTML'))
            product_sale_price = None
            product_promo = None

            page_items.append(
                (category, product_id, product_name, product_reg_price, product_sale_price, product_promo))

        column_names = self.get_empty_dataframe().columns
        return pd.DataFrame(page_items, columns=column_names)

    def save_data(self, items, output_path):
        print('Saving data to {}...'.format(output_path))
        items.to_csv(output_path, index=False, header=True)
