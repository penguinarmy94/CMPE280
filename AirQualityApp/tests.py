from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class SearchTest(TestCase):
    driver = ""
    zip = ""

    def setUp(self):
        self.zip = ["9", "4", "0", "4", "0"]
        self.driver = webdriver.Chrome()
        self.driver.get("http://projectsites.xyz")
        self.assertTrue("AirSafe" in self.driver.title)

    
    def test_search(self):
        elem = self.driver.find_element_by_id("pac-input")
        elem.clear()

        for i in self.zip:
            elem.send_keys(i)
            time.sleep(1)

        elem.send_keys(Keys.DOWN)
        time.sleep(1)
        elem.send_keys(Keys.ENTER)
        time.sleep(5)
        forecast = self.driver.find_element_by_id("forecast_button")
        forecast.click()
        elem = self.driver.find_elements_by_class_name("highcharts-title")
        self.assertTrue("94040" in elem[0].text)
    
    
    def test_sections(self):
        forecast = self.driver.find_element_by_id("forecast_button")
        past = self.driver.find_element_by_id("past_data_button")
        home = self.driver.find_element_by_id("home_button")

        time.sleep(3)
        forecast.click()
        self.assertEquals(forecast.value_of_css_property("background"), "rgb(249, 112, 22) none repeat scroll 0% 0% / auto padding-box border-box")
        time.sleep(3)
        past.click()
        self.assertEquals(past.value_of_css_property("background"), "rgb(249, 112, 22) none repeat scroll 0% 0% / auto padding-box border-box")
        time.sleep(3)
        home.click()
        self.assertEquals(home.value_of_css_property("background"), "rgb(249, 112, 22) none repeat scroll 0% 0% / auto padding-box border-box")
        time.sleep(3)
    
    def test_localizaton(self):
        lang = self.driver.find_element_by_id("localization")
        title = self.driver.find_element_by_id("title-text")
        self.assertEquals(title.text, "Air Quality Monitoring System")
        time.sleep(3)
        lang.click()
        time.sleep(2)
        lang.send_keys(Keys.DOWN)
        time.sleep(2)
        lang.click()
        time.sleep(5)
        title = self.driver.find_element_by_id("title-text")
        self.assertEquals(title.text, "Sistema de monitoreo de calidad del aire")
        lang = self.driver.find_element_by_id("localization")
        lang.click()
        time.sleep(2)
        lang.send_keys(Keys.DOWN)
        time.sleep(2)
        lang.send_keys(Keys.DOWN)
        lang.click()
        time.sleep(5)
        title = self.driver.find_element_by_id("title-text")
        self.assertEquals(title.text, "वायु गुणवत्ता निगरानी प्रणाली")
    

    def test_section_content(self):
        content = self.driver.find_element_by_id("about_us_button")
        time.sleep(1)
        content.click()
        time.sleep(2)
        about = self.driver.find_element_by_id("about")
        if about.value_of_css_property("display"):
            self.assertTrue(about.value_of_css_property("display") == "block")
        else:
            self.assertTrue(1 == 2)
        

    
    def test_subscribe(self):
        subscribe = self.driver.find_element_by_id("subscribe_button")
        time.sleep(2)
        subscribe.click()
        time.sleep(2)
        email = self.driver.find_element_by_id("subscribe_email")
        zipcode = self.driver.find_element_by_id("subscribe_zipcode")
        type_email = ["l", "u", "i", "s", ".", "o", "t", "e", "r", "o", "@", "s", "j", "s", "u", ".", "e", "d", "u"]
        type_zipcode = ["9", "5", "1", "1", "2"]

        for letter in type_email:
            email.send_keys(letter)
            time.sleep(1)
        
        time.sleep(2)

        for letter in type_zipcode:
            zipcode.send_keys(letter)
            time.sleep(1)
        
        time.sleep(2)

        button = self.driver.find_element_by_id("subscribing")
        button.click()

        time.sleep(10)

        verify = self.driver.find_element_by_id("verfication_code")

        if verify.value_of_css_property("display"):
            self.assertTrue(verify.value_of_css_property("display") == "inline")
        else:
            self.assertTrue(1 == 2)
        


    def tearDown(self):
        self.driver.close()