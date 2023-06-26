import os
from pathlib import Path

import pandas as pd
from selenium.common.exceptions import NoSuchElementException

from src.base_scraper import BaseScraper


class Eloquii(BaseScraper):
    @property
    def output_directory(self):
        return Path('data/output/eloquii')

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
        self.close_splash()
        self._browser.maximize_window()
        self.navigate_to_required_clothing_sections()
        self.delete_cookies()

    def close_splash(self):
        button = self._browser.find_element_by_xpath("//button[@data-click='close']")
        button.click()

    def navigate_to_required_clothing_sections(self):
        print('Finding link elements')
        links = self._browser.find_elements_by_xpath("//div[@class='sub-nav-style']/p/a")
        print('{} links found...'.format(len(links)))

        link_texts = [link.get_attribute('innerHTML') for link in links]
        link_urls = [link.get_attribute('href') for link in links]

        for link_url, link_text in zip(link_urls, link_texts):
            filename: Path = self.output_directory / self.filename_generator(link_text)
            if filename.exists():
                print('Filename {} already exists, skipping...'.format(filename))
                pass
            else:
                # navigate to each sub-clothing link
                print('Navigating to {} : {}'.format(link_text, link_url))
                self._browser.get(link_url)

                # return the list of items on all pages
                items = self.get_empty_dataframe()
                more_pages = True
                counter = 1
                while more_pages:
                    print('Getting page {}...'.format(counter))
                    items = items.append(self.get_current_page_items(self.clean_string(link_text)))
                    more_pages = False
                self.save_data(items, filename)

    def get_current_page_items(self, category):
        outermost_xpath = "//div[contains(@id,'product_wrapper')]"
        product_id_string = "rel"
        product_name_xpath = "./h3[1]/a"
        product_price_xpath = "./h3[contains(@id,'prices')]"
        product_no_sale_price_xpath = "./span[@class='standardprice']"
        product_regular_price_xpath = "./s"
        product_sale_price_xpath = "./span"
        product_promo_xpath = "./h3[3]"

        product_web_elements = self._browser.find_elements_by_xpath(outermost_xpath)
        print('Finding {} element details'.format(len(product_web_elements)))

        page_items = []
        for element in product_web_elements:
            # print('Selecting the elements of {}'.format(element))
            try:
                product_name_element = element.find_element_by_xpath(product_name_xpath)
                product_id = product_name_element.get_attribute(product_id_string)
                product_name = self.clean_string(product_name_element.get_attribute('innerHTML'))
                product_price_element = element.find_element_by_xpath(product_price_xpath)
                try:

                    product_reg_price = self.clean_string(
                        product_price_element.find_element_by_xpath(product_regular_price_xpath).text)
                    product_sale_price = self.clean_string(
                        product_price_element.find_element_by_xpath(product_sale_price_xpath).text)

                except NoSuchElementException:
                    print('no sale price found...')
                    product_reg_price = self.clean_string(
                        product_price_element.find_element_by_xpath(product_no_sale_price_xpath).text)
                    product_sale_price = None

                try:
                    product_promo = self.clean_string(element.find_element_by_xpath(product_promo_xpath).text)
                except:
                    product_promo = None

                page_items.append(
                    (category, product_id, product_name, product_reg_price, product_sale_price, product_promo))
            except:
                print('No h3 element found')

        column_names = self.get_empty_dataframe().columns
        return pd.DataFrame(page_items, columns=column_names)

    def save_data(self, items, output_path):
        print('Saving data to {}...'.format(output_path))
        items.to_csv(output_path, index=False, header=True)
