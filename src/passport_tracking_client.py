import logging
from datetime import date, datetime
from typing import Union, Dict

import requests
from bs4 import BeautifulSoup

from requests.cookies import RequestsCookieJar


class PassportTrackingClient:

    def __init__(self):
        self.session: requests.Session = requests.session()
        self.cookie_jar: RequestsCookieJar = RequestsCookieJar()
        self.step_one_url = "https://passporttracking.dfa.ie/PassportTracking/"
        self.step_two_url = "https://passporttracking.dfa.ie/PassportTracking/Home/GetStep"
        self.token_identifier = "__RequestVerificationToken"
        self.date_class = "status-date"
        self.status_table_class = "table"
        self.request_token: Union[str, None] = None

    def get_status(self, reference: str) -> Dict[str, object]:
        self.__set_one()
        soup = self.__step_two(reference)
        danger_div = soup.find('div', class_='alert alert-danger')
        if danger_div is not None:
            return {
                "Status": danger_div.text.strip()
            }
        status = self.__get_current_status(soup)
        return {
            "Expected Date": date,
            "Status": status
        }

    def __set_one(self) -> None:
        with self.session as s:
            logging.log(logging.INFO, f"Sending GET request to {self.step_one_url}")
            response = s.get(self.step_one_url)
            if response.status_code == 200:
                logging.log(logging.DEBUG, "Updating cookie jar")
                self.cookie_jar.update(response.cookies)
                logging.log(logging.DEBUG, "Parsing response content to soup")
                soup = BeautifulSoup(response.content, 'lxml')
                try:
                    logging.log(logging.INFO, f"Attempting to find {self.token_identifier} in soup")
                    token = soup.find('input', {'name': f'{self.token_identifier}'})['value']
                    logging.log(logging.INFO, "Successfully located request token in response")
                    self.request_token = token
                except TypeError:
                    logging.log(logging.ERROR, f"Could not fine {self.token_identifier} in response from "
                                               f"{self.step_one_url}")
            else:
                logging.log(logging.ERROR, f"Status code {response.status_code} returned when requesting "
                                           f"{self.step_one_url}")

    def __step_two(self, reference: str) -> Union[BeautifulSoup, None]:
        if self.request_token is None:
            logging.log(logging.ERROR, "Cannot proceed with step-two as request token has not been set")
            return
        logging.log(logging.DEBUG, "Creating form data for post request")
        form_data = {
            "__RequestVerificationToken": self.request_token,
            "search[Criteria][ReferenceNumber]": reference
        }
        with self.session as s:
            logging.log(logging.INFO, f"Sending POST request to {self.step_two_url}")
            response = s.post(self.step_two_url, cookies=self.cookie_jar, data=form_data)
            if response.status_code == 200:
                logging.log(logging.DEBUG, "Parsing response content to soup")
                soup = BeautifulSoup(response.content, 'lxml')
                return soup
            else:
                logging.log(logging.ERROR, f"Status code {response.status_code} returned when requesting "
                                           f"{self.step_two_url}")
                return None

    def __get_expected_date(self, soup: BeautifulSoup) -> Union[date, None]:
        if soup is not None:
            logging.log(logging.INFO, f"Attempting to find {self.date_class} in soup")
            date_str = soup.find('div', class_='status-date').text.strip()
            if date_str is None:
                logging.log(logging.ERROR, f"Could not fine {self.date_class} in response from {self.step_two_url}")
                return None
            logging.log(logging.DEBUG, f"Parsing {date_str} to datetime object")
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj
        return None

    def __get_current_status(self, soup: BeautifulSoup) -> Union[str, None]:
        if soup is not None:
            logging.log(logging.INFO, f"Attempting to find {self.status_table_class} in soup")
            table = soup.find('table', class_='table')
            if table is None:
                logging.log(logging.ERROR, f"Could not fine {self.status_table_class} in response from {self.step_two_url}")
                return None
            h2_tag = table.find('h2')
            p_tag = table.find('p')
            if h2_tag is None:
                logging.log(logging.ERROR, "Could not find status tag in soup")
                return None
            if p_tag is None:
                logging.log(logging.ERROR, "Could not find sub-status tag in soup")
                return f"{h2_tag.text.strip()}"
            return f"{h2_tag.text.strip()}: {p_tag.text.strip()}"
