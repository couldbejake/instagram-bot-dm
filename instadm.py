from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver.v2 as uc

from selenium.webdriver import ActionChains

from random import randint, uniform
from time import time, sleep
import logging
import sqlite3

DEFAULT_IMPLICIT_WAIT = 3

class InstaDM(object):

    def __init__(self, username, password, headless=True, instapy_workspace=None, profileDir=None):
        self.selectors = {
            "accept_cookies": "//button[text()='Allow essential and optional cookies']",
            "accept_cookies_post_login": "//button[text()='Allow all cookies']",
            "home_to_login_button": "//div[text()='Log in']",
            "username_field": "username",
            "password_field": "password",
            "button_login": "//button/*[text()='Log in']",
            "login_check": "//*[@aria-label='Home'] | //button[text()='Save Info'] | //button[text()='Not Now']",
            "search_user": "queryBox",
            "select_user": '//div[text()="{}"]',
            "name": "((//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar'])[1]//..//..//..//div[2]/div[2]/div)[1]",
            "next_button": "//button/*[text()='Next']",
            "textarea": "//textarea[@placeholder]",
            "send": "//button[text()='Send']"
        }

        # Selenium config
        options = webdriver.ChromeOptions()

        if profileDir:
            options.add_argument('--user-data-dir=' + profileDir)


        if headless:
            options.add_argument("--headless")
        

        self.driver = uc.Chrome(executable_path=CM().install(), options=options)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1000, 800)

        # Instapy init DB
        self.instapy_workspace = instapy_workspace
        self.conn = None
        self.cursor = None
        if self.instapy_workspace is not None:
            self.conn = sqlite3.connect(self.instapy_workspace + "InstaPy/db/instapy.db")
            self.cursor = self.conn.cursor()

            cursor = self.conn.execute("""
                SELECT count(*)
                FROM sqlite_master
                WHERE type='table'
                AND name='message';
            """)
            count = cursor.fetchone()[0]

            if count == 0:
                self.conn.execute("""
                    CREATE TABLE "message" (
                        "username"    TEXT NOT NULL UNIQUE,
                        "message"    TEXT DEFAULT NULL,
                        "sent_message_at"    TIMESTAMP
                    );
                """)

        self.driver.get('https://instagram.com/?hl=en')

        #try:
        #self.login(username, password)
        #except Exception as e:
        #    logging.error(e)
        #    print(str(e))

    def login(self, username, password):
        # homepage
        self.driver.get('https://instagram.com/?hl=en')
        self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['accept_cookies'], 'xpath', 10):
            self.__get_element__(self.selectors['accept_cookies'], 'xpath').click()
            self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['home_to_login_button'], 'xpath', 10):


            button = self.__get_element__(self.selectors['home_to_login_button'], 'xpath')

            el = self.driver.execute_script("arguments[0].click();", button)

            self.__random_sleep__(5, 7)

        # login
        logging.info(f'Login with {username}')
        self.__scrolldown__()
        if not self.__wait_for_element__(self.selectors['username_field'], 'name', 10):
            print('Login Failed: username field not visible')
        else:
            self.driver.find_element(By.NAME, self.selectors['username_field']).send_keys(username)
            self.driver.find_element(By.NAME, self.selectors['password_field']).send_keys(password)



            button = self.__get_element__(self.selectors['button_login'], 'xpath')
            el = self.driver.execute_script("arguments[0].click();", button)

            self.__random_sleep__()
            if self.__wait_for_element__(self.selectors['login_check'], 'xpath', 10):
                print('Login Successful')
                if self.__wait_for_element__(self.selectors['accept_cookies_post_login'], 'xpath', 10):
                    self.__get_element__(self.selectors['accept_cookies_post_login'], 'xpath').click()
                    self.__random_sleep__(2, 4)
            else:
                print('Login Failed: Incorrect credentials')

    def createCustomGreeting(self, greeting):
        # Get username and add custom greeting
        if self.__wait_for_element__(self.selectors['name'], "xpath", 10):
            user_name = self.__get_element__(self.selectors['name'], "xpath").text
            if user_name:
                greeting = greeting + " " + user_name + ", \n\n"
        else: 
            greeting = greeting + ", \n\n"
        return greeting

    def typeMessage(self, user, message):
        # Go to page and type message
        if self.__wait_for_element__(self.selectors['next_button'], "xpath"):
            self.__get_element__(self.selectors['next_button'], "xpath").click()
            self.__random_sleep__()

        if self.__wait_for_element__(self.selectors['textarea'], "xpath"):
            self.__type_slow__(self.selectors['textarea'], "xpath", message)
            self.__random_sleep__()

        if self.__wait_for_element__(self.selectors['send'], "xpath"):
            #self.__remove_browser_unsupported_banner_if_exists()
            self.__get_element__(self.selectors['send'], "xpath").click()
            self.__random_sleep__(1, 2)
            print('Message sent successfully')

    def sendMessage(self, user, message, greeting=None):
        logging.info(f'Send message to {user}')
        print(f'Send message to {user}')
        self.driver.get('https://www.instagram.com/direct/new/')
        self.__random_sleep__(5, 7)

        #try:
        self.__wait_for_element__(self.selectors['search_user'], "name")
        self.__type_slow__(self.selectors['search_user'], "name", user)
        self.__random_sleep__(7, 10)

        if greeting != None:
            greeting = self.createCustomGreeting(greeting)

        self.__random_sleep__(1, 3)

        # Select user from list
        elements = self.driver.find_elements(by=By.XPATH, value=self.selectors['select_user'].format(user))

        try:

            if elements and len(elements) > 0:
                elements[0].click()
                self.__random_sleep__()

                if greeting != None:
                    self.typeMessage(user, greeting + message)
                else:
                    self.typeMessage(user, message)
                
                if self.conn is not None:
                    self.cursor.execute('INSERT INTO message (username, message) VALUES(?, ?)', (user, message))
                    self.conn.commit()
                self.__random_sleep__(1, 4)

                return True

            # In case user has changed his username or has a private account
            else:
                print(f'User {user} not found! Skipping.')
                return False
                
        except Exception as e:
            logging.error(e)
            return False


    def sendGroupMessage(self, users, message):
        logging.info(f'Send group message to {users}')
        print(f'Send group message to {users}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(5, 7)

        try:
            usersAndMessages = []
            for user in users:
                if self.conn is not None:
                    usersAndMessages.append((user, message))

                self.__wait_for_element__(self.selectors['search_user'], "name")
                self.__type_slow__(self.selectors['search_user'], "name", user)
                self.__random_sleep__()

                # Select user from list
                elements = self.driver.driver.find_element(by=By.XPATH, value=self.selectors['select_user'].format(user))
                if elements and len(elements) > 0:
                    elements[0].click()
                    self.__random_sleep__()
                else:
                    print(f'User {user} not found! Skipping.')

            self.typeMessage(user, message)

            if self.conn is not None:
                self.cursor.executemany("""
                    INSERT OR IGNORE INTO message (username, message) VALUES(?, ?)
                """, usersAndMessages)
                self.conn.commit()
            self.__random_sleep__(50, 60)

            return True
        
        except Exception as e:
            logging.error(e)
            return False
            
    def sendGroupIDMessage(self, chatID, message):
        logging.info(f'Send group message to {chatID}')
        print(f'Send group message to {chatID}')
        self.driver.get('https://www.instagram.com/direct/inbox/')
        self.__random_sleep__(5, 7)
        
        # Definitely a better way to do this:
        actions = ActionChains(self.driver) 
        actions.send_keys(Keys.TAB*2 + Keys.ENTER).perform()
        actions.send_keys(Keys.TAB*4 + Keys.ENTER).perform()

            
        if self.__wait_for_element__(f"//a[@href='/direct/t/{chatID}']", 'xpath', 10):
            self.__get_element__(f"//a[@href='/direct/t/{chatID}']", 'xpath').click()
            self.__random_sleep__(3, 5)

        try:
            usersAndMessages = [chatID]

            if self.__wait_for_element__(self.selectors['textarea'], "xpath"):
                self.__type_slow__(self.selectors['textarea'], "xpath", message)
                self.__random_sleep__()
            
            if self.__wait_for_element__(self.selectors['send'], "xpath"):
                self.__get_element__(self.selectors['send'], "xpath").click()
                self.__random_sleep__(3, 5)
                print('Message sent successfully')
            
            if self.conn is not None:
                self.cursor.executemany("""
                    INSERT OR IGNORE INTO message (username, message) VALUES(?, ?)
                """, usersAndMessages)
                self.conn.commit()
            self.__random_sleep__(50, 60)

            return True
        
        except Exception as e:
            logging.error(e)
            return False

    def __get_element__(self, element_tag, locator):
        """Wait for element and then return when it is available"""
        try:
            locator = locator.upper()
            dr = self.driver
            if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                return self.driver.find_element(By.ID, element_tag)
            elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                return self.driver.find_element(By.NAME, element_tag)
            elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                return self.driver.find_element(By.XPATH, element_tag)
            elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                return self.driver.find_element(By.CSS_SELECTOR, element_tag)
            elif locator == 'CLASS' and self.is_element_present(By.CLASS_NAME, element_tag):
                return self.driver.find_element(By.CLASS_NAME, element_tag)
            else:
                logging.info(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            logging.error(e)
        logging.info(f"Element not found with {locator} : {element_tag}")
        return None

    def is_element_present(self, how, what):
        """Check if an element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def __wait_for_element__(self, element_tag, locator, timeout=30):
        """Wait till element present. Max 30 seconds"""
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()
        for i in range(timeout):
            initTime = time()
            try:
                if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                    result = True
                    break
                elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                    result = True
                    break
                elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                    result = True
                    break
                elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTORS, element_tag):
                    result = True
                    break
                else:
                    logging.info(f"Error: Incorrect locator = {locator}")
            except Exception as e:
                logging.error(e)
                print(f"Exception when __wait_for_element__ : {e}")

            sleep(1)
        else:
            print(f"Timed out. Element not found with {locator} : {element_tag}")
        self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
        return result

    def __type_slow__(self, element_tag, locator, input_text=''):
        """Type the given input text"""
        try:
            self.__wait_for_element__(element_tag, locator, 5)
            element = self.__get_element__(element_tag, locator)
            actions = ActionChains(self.driver)
            actions.click(element).perform()
            for index, s in enumerate(input_text):
                # https://stackoverflow.com/questions/53901388/how-do-i-manipulate-shiftenter-instead-of-n/53909017#53909017
                if s == '\n' and index != len(input_text) - 1:
                    element.send_keys(Keys.SHIFT, s)
                else:
                    element.send_keys(s)
                sleep(uniform(0.25, 0.75))

        except Exception as e:
            logging.error(e)
            print(f'Exception when __typeSlow__ : {e}')

    def __random_sleep__(self, minimum=10, maximum=20):
        #t = randint(minimum, maximum)
        t = 1
        logging.info(f'Wait {t} seconds')
        sleep(1)

    def __scrolldown__(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def teardown(self):
        self.driver.close()
        self.driver.quit()