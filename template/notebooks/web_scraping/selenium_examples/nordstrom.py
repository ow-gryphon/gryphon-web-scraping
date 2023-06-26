import os
from pathlib import Path

import pandas as pd
from selenium.common.exceptions import NoSuchElementException

from src.base_scraper import BaseScraper

import time


class Nordstrom(BaseScraper):
    @property
    def output_directory(self):
        return Path('data/output/nordstrom')

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

        more_pages=True
        counter=1
        # scrape the current page
        link_text = 'page{}'.format(counter)
        items = self.get_empty_dataframe()
        filename: Path = self.output_directory / self.filename_generator(link_text)
        if filename.exists():
            print('Filename {} already exists, skipping...'.format(filename))
            pass
        else:
            items = items.append(self.get_current_page_items(self.clean_string(link_text)))
            self.save_data(items, filename)

        while more_pages:
            try:
                next_link = self._browser.find_element_by_xpath("//a[@data-element='page-arrow-page-next-link']")
                next_href = next_link.get_attribute("href")
                if next_href == "" or next_href is None:
                    more_pages = False
                else:
                    counter += 1
                    print('Getting page {}...'.format(counter))
                    self.get_page_source(next_href)
                    link_text = 'page{}'.format(counter)
                    items = self.get_empty_dataframe()
                    filename: Path = self.output_directory / self.filename_generator(link_text)
                    if filename.exists():
                        print('Filename {} already exists, skipping...'.format(filename))
                        pass
                    else:
                        items = items.append(self.get_current_page_items(self.clean_string(link_text)))
                        self.save_data(items, filename)
            except:
                more_pages = False



    def get_current_page_items(self, category):
        outermost_xpath = "//article[@data-element='product-results-product-module-desktop']"
        product_id_string = "href"
        product_name_xpath = ".//h3/a/span/span"
        product_price_original_xpath = ".//div[contains(@data-element,'product-module-price-line-original')]"
        product_price_sales_price_xpath = ".//div[contains(@data-element,'product-module-price-line-sale')]"
        product_sub_price_xpath = "//span[@data-element='product-module-price-line-price']"

        product_promo_xpath = "//span[@data-element='product-module-price-line-percent']"

        product_web_elements = self._browser.find_elements_by_xpath(outermost_xpath)
        print('Finding {} element details'.format(len(product_web_elements)))

        page_items = []
        for element in product_web_elements:
            # print('Selecting the elements of {}'.format(element))

            product_name_element = element.find_element_by_xpath(product_name_xpath)
            product_name = self.clean_string(product_name_element.text)
            product_id = None

            product_orig_price_element = element.find_element_by_xpath(product_price_original_xpath + product_sub_price_xpath)
            product_reg_price = self.clean_string(product_orig_price_element.text)
            try:
                product_sales_price_element = element.find_element_by_xpath(product_price_sales_price_xpath + product_sub_price_xpath)
                product_sales_price = product_sales_price_element.text
            except:
                product_sales_price = None

            product_promo = None

            page_items.append(
                (category, product_id, product_name, product_reg_price, product_sales_price, product_promo))

        column_names = self.get_empty_dataframe().columns
        return pd.DataFrame(page_items, columns=column_names)

    def save_data(self, items, output_path):
        print('Saving data to {}...'.format(output_path))
        items.to_csv(output_path, index=False, header=True)
