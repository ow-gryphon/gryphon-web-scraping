import datetime
import os
import time
from random import randint
from random import random

from selenium.common.exceptions import ElementNotVisibleException

from src.base_scraper import BaseScraper


class BSBSurveryNavigator(BaseScraper):
    def website_specific_actions(self, params):
        """
        Function containing the code specific to navigate the BSB survey.

        :param params: parameters for the navigation and selection
        :return: None - navigates website
        """
        self.get_to_survey()
        self.select_company()
        self.radio_pages()
        self.words_page(params['input_words'])
        self.check_boxes_page(params['checkboxes_threshold_p7'])
        self.dropdowns_page(params['checkboxes_threshold_p8'], params['certif_name'])
        time.sleep(3)

    def get_to_survey(self):
        """
        Function for the first page - clicking on button to go to survey.

        :return: None
        """
        # Click on start survey
        try:
            navigator._browser.find_element_by_class_name('btn-survey').click()
        except ElementNotVisibleException:
            time.sleep(10)   # sometime takes some time to load - wait and try again. Potentially replace with a more sophisticated wait
            navigator._browser.find_element_by_class_name('btn-survey').click()

    def select_company(self):
        """
        Function to select the company.

        :return: None
        """
        time.sleep(0.5)
        # Select company at random from drop-down
        self.randomly_select_dropdown_id('sq_100i', start_index=1)  # Start at 1 to avoid the item 'Choose...'

        # Select other dropdown - does not always appear or have proper values, depends on company --> try block
        time.sleep(0.5)
        try:
            # Select company at random from drop-down
            self.randomly_select_dropdown_id('sq_101i', start_index=1)  # Start at 1 to avoid the item 'Choose...'
        except Exception:
            pass

        # Go next page
        navigator._browser.find_element_by_xpath('//input[@value="Next"]').click()

    def radio_pages(self):
        """
        Function to click through the radio pages of the survey.

        :return: None
        """
        # There are 4 pages of radio buttons to click
        for page_num in range(4):
            time.sleep(0.2)
            # Retrieve all radio buttons
            radio_buttons = navigator._browser.find_elements_by_xpath('//*[starts-with(@name, "likert-core-question")]')

            # Get all unique question values
            q_vals = [q.get_attribute('name') for q in radio_buttons]
            q_uniques = set(q_vals)   # WARNING - does not preserve order

            # Get random set of questions to click on
            values = [str(randint(1, 5)) for _ in range(len(q_uniques))]
            selected_questions = []
            for question, value in zip(q_uniques, values):
                selected_questions.append(BSBSurveryNavigator.filter_questions_name_value(radio_buttons, question, value))

            # Click on them
            for q in selected_questions:
                self._browser.execute_script("arguments[0].click();", q)
                time.sleep(0.05)

            # Go to next page
            navigator._browser.find_element_by_xpath('//input[@value="Next"]').click()

    def words_page(self, input_list):
        """
        Function to input the words in the free words page.

        :param input_list: list containing the words to input in the first two input boxes
        :return: None.
        """
        input_list.append(datetime.datetime.now().strftime("%y-%m-%d %H:%M"))  # TODO: WARNING IT TAKES THE SPACE IN!!!
        input_boxes = navigator._browser.find_elements_by_id('sq_106i')
        for box, input_text in zip(input_boxes, input_list):
            box.clear()
            box.send_keys(input_text)
            time.sleep(0.2)

        # Go to next page
        navigator._browser.find_element_by_xpath('//input[@value="Next"]').click()


    @staticmethod
    def filter_questions_name_value(q_list, name, value):
        """
        Function to filter a question from a full list of questions given name and value.

        :param q_list: full list of questions
        :param name: name of the question to filter
        :param value: value of the question to filter
        :return: filtered question
        """
        for question in q_list:
            if question.get_attribute('name') == name and question.get_attribute('value') == value:
                return question

    def check_boxes_page(self, threshold):
        """
        Function to click the check-boxes on Page 7.

        :param threshold: threshold for random selection of check-boxes
        :return: None
        """
        time.sleep(0.5)
        checkbox_names = ['values-conflict', 'past-months-behavior-extended', 'raising-concerns-extended']
        for checkbox in checkbox_names:
            try:
                self.click_checkbox_series(checkbox, threshold)
            except ElementNotVisibleException as e:
                if checkbox == 'values-conflict':
                    continue   # It's ok, it's a conditional checkbox that only pops-up sometimes
                else:
                    raise e

        # Go to next page
        navigator._browser.find_element_by_xpath('//input[@value="Next"]').click()

    def click_checkbox_series(self, series_name, threshold, sleep_time=0.1, skip_checkbox_index=-1):
        """
        Function to Retrieve check-boxes given the name of the series, and click a random number of them.

        :param series_name: HTML name attribute of the series
        :param threshold: random threshold over which clicking checkboxes
        :param skip_checkbox_index: index of a checkbox to skip in the series
        :return: None - clieck checkboxes
        """
        counter = 0
        checkboxes_one = navigator._browser.find_elements_by_name(series_name)  # TODO: WARNING: CAN INSERT MUTUALLY-EXCLUSIVE OPTIONS, LIKE A VALID OPTION AND 'PRFER NOT TO SAY'
        for checkbox in checkboxes_one:
            if random() < threshold and counter != skip_checkbox_index:
                self._browser.execute_script("arguments[0].click();", checkbox)
                time.sleep(sleep_time)
            counter += 1

    def dropdowns_page(self, threshold, certif_name):
        ddwns_ids = ['sq_110i', 'sq_111i', 'sq_112i', 'sq_113i', 'sq_114i', 'sq_115i', 'sq_116i', 'sq_117i']
        for id in ddwns_ids:
            self.randomly_select_dropdown_id(id, start_index=1)
            time.sleep(0.1)

        # If last question is yes, another question pops up
        time.sleep(0.5)
        try:
            self.click_checkbox_series('pbody-select', threshold, sleep_time=0.1, skip_checkbox_index=22)  # Skip Other, causes problems, see below
        except ElementNotVisibleException:
            pass

        # If select Other, input textbox appears
        # TODO: I've tried a few things, could not get it to work....
        # try:
        #     # self._browser.find_element_by_class_name('form-control').send_keys(certif_name)
        #     el = self._browser.find_element_by_xpath('//*[contains(@data-bind, "question.survey.css.question.comment")]')
        #     is_visible = el.get_attribute('style')
        #     self._browser.find_element_by_xpath('//*[contains(@data-bind, "value: $data.question.koComment, visible: $data.visible, css: question.survey.css.question.comment")]').send_keys(certif_name)
        #     # self._browser.execute_script("arguments[0].value = 'hohohoho';", el)
        #     self._browser.execute_script("arguments[0].click();", el)
        # except ElementNotVisibleException:
        #     pass

        # Submit survey
        self._browser.find_element_by_xpath('//input[@value="Complete"]').click()



if __name__ == "__main__":
    if os.name == 'nt':
        DRIVER_PATH = '../chromedrivers/chromedriver_win.exe'
    else:
        DRIVER_PATH = '../chromedrivers/chromedriver_mac'
    headless_mode = False
    url = 'https://www.bsbsurvey.co.uk/#!/home/?survey=5abcf98475525330c4ef084a&key=6c1f65b3-f22b-46b3-bc4f-cde52c110ea2'
    # Some parameters to fill in the survey
    params = {
        'n_runs': 3,
        'input_words': ['JaveryAuto', 'Chromedriver'],
        'checkboxes_threshold_p7': 0.4,
        'checkboxes_threshold_p8': 0.3,
        'certif_name': 'RandomCertif'
    }

    # Instantiate navigator
    navigator = BSBSurveryNavigator(path_to_driver=DRIVER_PATH, headless_mode=headless_mode)

    # Fill in the survey a specified number of times
    for run in range(params['n_runs']):
        try:
            navigator.scrape_website(url, params)
        except Exception as e:
            print('Something wrong with run: {}'.format(run))
            print(e)
            time.sleep(3)


    # Close the browser window
    navigator.wind_down_browser()

    print('Done.')









