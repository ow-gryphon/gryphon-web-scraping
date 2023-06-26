import os
import time

import pandas as pd
import selenium
from selenium.webdriver.common.keys import Keys

from src.base_scraper import BaseScraper
from src.utilities import find_runs_already_done


class CompareTheMarket(BaseScraper):
    def website_specific_actions(self, params):
        """
        Function to do all the set of actions (clicks, form filling etc.) required for a website. To be overridden
        by child website-specific classes.

        :return:
        """
        self.get_to_form()
        self.your_vehicle_tab(params)
        self.your_details_tab(params)
        self.your_policy_tab(params)
        self.summary_tab()
        self.quotes_tab(params)
        self.delete_cookies()


    def get_to_form(self):
        """
        Function to click the initial buttons to get to the quote form.

        :return:
        """
        try:
            scraper._browser.find_element_by_xpath("//a[@title='Car Insurance']").click()
            scraper._browser.find_element_by_id('lph-cta-car').click()
        except selenium.common.exceptions.ElementNotVisibleException:
            # We're reopening again page for second quote, request new quote
            scraper._browser.find_element_by_id('hh-info-bar-cta-secondary').click()

    def your_vehicle_tab(self, params):
        """
        Function to fill in the tab "your vehicle" in the form.

        :return:
        """

        # Now it has navigated to the car insurance detailed parameters page
        # PAGE 1
        # Select no reg-number
        time.sleep(3)
        plate_input = scraper._browser.find_element_by_id('registration-number')
        plate_input.send_keys(params['plate'], Keys.ENTER)
        time.sleep(3)

        # LEFT AS THE DEFAULT OPTIONS
        # - fitted tracking device: Factory-fitted Thatcham alarm
        # - is can an import: no
        # - Car is righ-hand drive
        # - Market value of the car, pre-populated by comparethemarket.com
        # - Car has been modified in any way: NO

        scraper.click_javascript_element('vehicle-lookup-next')
        time.sleep(3)

        # Do more input
        mileage_input = scraper._browser.find_element_by_id('annual-mileage')
        mileage_input.send_keys(params['mileage'], Keys.ENTER)
        for id, value in params['car_params'].items():
            scraper.select_value_dropdown_id(id, value)
            time.sleep(2)

        # Other params
        if params['usage'] == 'SDP':
            scraper.click_javascript_element('use-of-vehicle-05NN')
        elif params['usage'] == 'SDPC':
            scraper.click_javascript_element('use-of-vehicle-02YN')
        if params['car_kept_day'] == 'home':
            scraper.click_javascript_element('vehicle-kept-during-day-VKD1')
        elif params['car_kept_day'] == 'office_factory':
            scraper.click_javascript_element('vehicle-kept-during-day-VKD2')
        scraper.click_javascript_element('vehicle-kept-during-night-4')
        time.sleep(1)

        # Next page
        scraper.click_javascript_element('vehicle-usage-next')

    def your_details_tab(self, params):
        """
        Function to fill in the tab "your details" in the form.

        :return:
        """

        # Now it has navigated to Your details page
        # PAGE 2
        time.sleep(3)

        # Fill up all the drop downs
        for id, value in params['proposer_params'].items():
            print('setting: {}'.format(id))
            try:
                scraper.select_value_dropdown_id(id, value)
            except selenium.common.exceptions.ElementNotVisibleException:
                pass  # TODO: SOME OPTIONS DO NOT APPEAR UNDER CERTAIN OTHER OPTION CONDITIONS: example: if driving licence > 25y, it does not ask for driving licence start date
            time.sleep(1)

        # Fill up all the text boxes
        fName_input = scraper._browser.find_element_by_id('proposer-first-name')
        fName_input.send_keys(params['fName'], Keys.ENTER)

        lName_input = scraper._browser.find_element_by_id('proposer-last-name')
        lName_input.send_keys(params['lName'], Keys.ENTER)

        houseNum_input = scraper._browser.find_element_by_id('proposer-home-address-house-number')
        houseNum_input.send_keys(params['houseNumber'], Keys.ENTER)

        postCode_input = scraper._browser.find_element_by_id('proposer-home-address-postcode')
        postCode_input.send_keys(params['postCode'], Keys.ENTER)
        # scraper._browser.find_element_by_id('proposer-home-address-find-address').click()

        # Additional selections if the person is employed
        if params['proposer_params']['proposer-employment-status'] == 'E' or params['proposer_params']['proposer-employment-status'] == 'S':
            occupation_input = scraper._browser.find_element_by_id('proposer-occupation-title-search-text')
            occupation_input.send_keys(params['occupation'], Keys.ENTER)
            time.sleep(5)
            occupation_input.send_keys(Keys.ENTER)

            businessType_input = scraper._browser.find_element_by_id('proposer-business-type-search-text')
            businessType_input.send_keys(params['industry'], Keys.ENTER)
            time.sleep(5)
            businessType_input.send_keys(Keys.ENTER)

        # Fill up all the check boxes
        scraper.click_javascript_element('proposer-home-owner-yes')
        scraper.click_javascript_element('proposer-children-yes')
        scraper.click_javascript_element('proposer-licence-number-no')
        scraper.click_javascript_element('proposer-policy-declined-no')
        scraper.click_javascript_element('proposer-claims-convictions-motor-accidents-no')
        scraper.click_javascript_element('proposer-claims-convictions-penalties-no')
        scraper.click_javascript_element('proposer-claims-convictions-criminal-no')

        # Click the Next button
        scraper.click_javascript_element('personal-details-next')

        #Click the continue button on the following page
        # scraper.click_javascript_element('continue-button')
        time.sleep(2)
        scraper.click_javascript_element('additional-drivers-next')

    def your_policy_tab(self, params):
        """
        Function to fill in the tab "your policy" in the form.

        :return:
        """

        # Now it has navigated to the policy details parameters page
        # TAB 3

        # LEFT AS THE DEFAULT OPTIONS
        # - Who is the main driver of this vehicle?: Prepopulated from previous "Your Details" pages
        # - Are you (or will you be) the registered keeper and legal owner?: Yes
        time.sleep(2)
        scraper.select_value_dropdown_id('cover-type', '01')
        if params['paymethod'] == 'Annual':
            scraper.click_javascript_element('payment-method-F')
        elif params['paymethod'] == 'Monthly':
            scraper.click_javascript_element('payment-method-M')
        time.sleep(3)

        for id, value in params['policy_params'].items():
            scraper.select_value_dropdown_id(id, value)
            time.sleep(2)

        if params['how_earn_discount'] == 'With this vehicle or a previous vehicle':
            scraper.click_javascript_element('ncd-source-1')

        if params['protect_NCD']=='No':
            scraper.click_javascript_element('protected-ncd-no')
        elif params['protect_NCD']=='Yes':
            scraper.click_javascript_element('protected-ncd-yes')

        # Next page
        scraper.click_javascript_element('policy-details-next')

        # Must insert email to continue but not required to input phone number
        time.sleep(1)
        email_input = scraper._browser.find_element_by_id('email')
        time.sleep(2)

        # Enter email only on first run. other times it's cached
        email_input.clear()
        email_input.send_keys(params['emailadd'], Keys.ENTER)
        time.sleep(1)

        # Do more input
        scraper.click_javascript_element('communication-options-provider-no')
        scraper.click_javascript_element('iq-user-preference-no')
        scraper.click_javascript_element('communication-options-email')
        scraper.click_javascript_element('communication-options-post')

        # Agree to terms and conditions
        scraper.click_javascript_element('agree-t-and-c')

        # Next page
        scraper.click_javascript_element('contact-details-next')

    def summary_tab(self):
        time.sleep(2)
        scraper.click_javascript_element('go-to-your-quote-button')

    def quotes_tab(self, params):
        """
        Last tab, with quotes.

        :return: Outputs to csv
        """
        time.sleep(60)
        quotes = scraper._browser.find_elements_by_xpath('//*[contains(@id,"quote-")]')
        quotes_text = [q.text for q in quotes if q.text != '']
        quote_split = [q.split('\n') for q in quotes_text]
        prices = [q[0] for q in quote_split]

        logos = scraper._browser.find_elements_by_xpath('//*[contains(@class,"provider-logo")]')
        providers = [l.get_attribute('alt') for l in logos]
        p_unique = providers[0::2]
        pics = [l.get_attribute('src') for l in logos]
        pics_unique = pics[0::2]
        pics_names = [p.split('/').pop() for p in pics_unique]

        df = pd.DataFrame({'provider': p_unique, 'price': prices, 'pics': pics_names, 'run_id':[params['run_id']]*len(p_unique)})
        output_file = '../../data/output/scraping_output.csv'
        if os.path.exists(output_file):
            with open(output_file, 'a') as f:
                df.to_csv(f, index=False, header=False)
        else:
            df.to_csv(output_file, index=False) # Might need to check path depending on how it is run
            # df.to_csv('./data/output/scraping_output.csv', index=False) # Might need to check path depending on how it is run

    @staticmethod
    def prepare_input(input_file):
        input_data = pd.read_csv(input_file).astype(str)
        all_inputs = []
        static_params = {
            'mileage': '10000',
            'car_params': {
                'purchase-month': '4',
                'purchase-year': '2017',
                'number-of-vehicles-in-household': '2',
                'use-of-other-vehicles': 'UVE'
            },
            'emailadd': 'rachelgregory12345@outlook.com'
        }

        for _, row in input_data.iterrows():
            run_param = {}
            run_param['run_id'] = row['run_id']
            run_param['plate'] = row['plate']
            run_param['usage'] = row['usage']
            run_param['car_kept_day'] = row['car_kept_day']
            run_param['fName'] = row['First name']
            run_param['lName'] = row['Surname']
            run_param['houseNumber'] = row['Address']
            run_param['postCode'] = row['PostCode']
            run_param['occupation'] = row['job']
            run_param['industry'] = row['industry']
            run_param['proposer_params'] = {
                'proposer-title': 'MS',
                'proposer-dob-day': row['proposer-dob-day'],
                'proposer-dob-month': row['proposer-dob-month'],
                'proposer-dob-year': row['proposer-dob-year'],
                'proposer-marital-status': row['proposer-marital-status'],
                'proposer-employment-status': row['proposer-employment-status'],
                'proposer-driving-license-duration': row['driving_licence_duration'],
                'proposer-licence-monthandyear-month': '1',
                'proposer-licence-monthandyear-year': '2018'
            }
            run_param['own_home'] = row['own_home']
            run_param['children_16'] = row['children_16']
            run_param['policy_params'] = {
                'commencement-date': '19/04/2018',
                'voluntary-excess': row['voluntary_excess'],
                'ncd-period': row['ncd_period']
            }
            run_param['how_earn_discount'] = row['how_earn_discount']
            run_param['protect_NCD'] = row['protect_NCD?']
            run_param['paymethod'] = row['monthly_annual']

            merged = {**static_params, **run_param}
            all_inputs.append(merged)

        return all_inputs

    @staticmethod
    def filter_done_ids(output_file_path, range_l, range_h, full_set_params):
        done_ids = find_runs_already_done(output_file_path)
        filter_one = full_set_params[range_l:range_h]
        filter_two = [item for item in filter_one if int(item['run_id']) not in done_ids]
        return filter_two


if __name__ == "__main__":
    # DRIVER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chromedrivers', 'chromedriver_mac')

    if os.name == 'nt':
        DRIVER_PATH = '../chromedrivers/chromedriver_win.exe'
    else:
        DRIVER_PATH = '../chromedrivers/chromedriver_mac'
    headless_mode = False
    url = 'https://www.comparethemarket.com/'

    # input_file = './data/input/comparethemarket_input_set.csv'
    input_file = '../../data/input/CTM_Input_Set_RG.csv'
    combined_output_file = '../../data/output/TOTAL.csv'
    range_lower = 100
    range_upper = 500
    all_params = CompareTheMarket.prepare_input(input_file)
    # filtered_range = CompareTheMarket.filter_done_ids(combined_output_file, range_lower, range_upper, all_params)

    # Instantiate scraper
    scraper = CompareTheMarket(DRIVER_PATH, headless_mode=headless_mode)

    # scraper.get_page_source(url)
    for params in all_params:
        try:
            scraper.scrape_website(url, params)
        except Exception as e:
            print("SOMETHING WRONG WITH RUN: {}".format(str(params['run_id'])))
            print(e)
        time.sleep(10)   # Avoid too many requests in a row

    # Close the browser window
    # scraper.wind_down_browser()


