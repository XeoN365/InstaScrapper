from time import sleep
from selenium import webdriver
from dotenv import load_dotenv
import os, os.path
import json

class Helper():
    def load_json(filename):
        if not os.path.exists(filename):
            f = open(filename, "w")
            print("File doesn't exist!, creating new file.")
            return None
        else:
            with open(filename) as file:
                t = json.load(file)
                return t
    
    def save_json(filename, data):
        with open(filename, "w") as file:
            json.dump(data, file)

    def compare_collections(old_data, new_data):
        result = (set(new_data) - set(old_data))
        return result

class InstaBot():
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.url = 'http://www.instagram.com'
        self.username = username
        self.password = password
        self.driver.get(f"{self.url}")
        self.data_file = "data.json"
    
    def login(self):
        input_element = self.driver.find_element_by_xpath("//input[@name='username']")
        input_element2 = self.driver.find_element_by_xpath("//input[@name='password']")
        input_element.send_keys(self.username)
        input_element2.send_keys(self.password)

        button_element = self.driver.find_element_by_xpath("//button[@type='submit']")
        button_element.click()
        
    def skipCookies(self):
        button_element = self.driver.find_element_by_xpath("//button[text()='Accept All']")
        button_element.click()
        
    def skipPopUps(self):
        button_element = self.driver.find_element_by_xpath("//button[text()='Not Now']")
        button_element.click()

        button_element2 = self.driver.find_element_by_xpath("//button[text()='Not Now']")
        button_element2.click()
    
    def go_to_profile(self):
        self.driver.get(f"{self.url}/{self.username}/")

    def scrape_followers(self):
        button_element = self.driver.find_element_by_xpath(f"//a[@href='/{self.username}/followers/']")
        button_element.click()
        SCROLL_COOLDOWN = 1
        sleep(2)
        lists = self.driver.find_elements_by_xpath("//ul[@class]")
        if len(lists) == 2:
            selector = 1
        else:
            selector = 2
        parent = lists[selector].find_element_by_xpath("..")
        el = lists[selector].get_attribute("class")[6:]
        parent_el = parent.get_attribute("class")
        self.driver.execute_script(f"follower = document.getElementsByClassName('{parent_el}')[0]")
        last_height = self.driver.execute_script("return follower.scrollHeight;")
        scrolling = True
        while scrolling:
            self.driver.execute_script("follower.scrollTo(0, follower.scrollHeight);")
            sleep(SCROLL_COOLDOWN)

            new_height = self.driver.execute_script("return follower.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height
        
        followers = self.driver.execute_script("return follower.children[0].children[0].children")
        data = []
        for follower in followers:
            raw_id = follower.find_element_by_xpath(".//a[@href]").get_attribute("href")[:]
            url = raw_id.replace("https://www.instagram.com/","")
            id = url.replace("/","")
            data.append(id)
        print("Finished collecting followers...")
        return data

    def scrape_following(self):
        button_element = self.driver.find_element_by_xpath(f"//a[@href='/{self.username}/following/']")
        button_element.click()
        SCROLL_COOLDOWN = 1
        sleep(2)
        lists = self.driver.find_elements_by_xpath("//ul[@class]")
        if len(lists) == 2:
            selector = 1
        else:
            selector = 2
        parent = lists[selector].find_element_by_xpath("..")
        el = lists[selector].get_attribute("class")[6:]
        parent_el = parent.get_attribute("class")
        self.driver.execute_script(f"follower = document.getElementsByClassName('{parent_el}')[0]")
        last_height = self.driver.execute_script("return follower.scrollHeight;")
        scrolling = True
        while scrolling:
            self.driver.execute_script("follower.scrollTo(0, follower.scrollHeight);")
            sleep(SCROLL_COOLDOWN)

            new_height = self.driver.execute_script("return follower.scrollHeight;")
            if new_height == last_height:
                scrolling = False
            last_height = new_height
        
        followers = self.driver.execute_script("return follower.children[0].children[0].children")
        data = []
        for follower in followers:
            raw_id = follower.find_element_by_xpath(".//a[@href]").get_attribute("href")[:]
            url = raw_id.replace("https://www.instagram.com/","")
            id = url.replace("/","")
            data.append(id)
        print("Finished collecting following...")
        return data

    def close(self):
        self.driver.close()


if __name__=="__main__":
    load_dotenv()
    USER = os.getenv('USER')
    PASS = os.getenv('PASS')
    DATA_FILE = "data.json"

    bot = InstaBot(USER,PASS)
    bot.skipCookies()
    bot.login()
    bot.skipPopUps()
    bot.go_to_profile()
    following = bot.scrape_following()
    bot.go_to_profile()
    followers = bot.scrape_followers()
    bot.go_to_profile()
    
    data = {}
    data['followers'] = followers
    data['following'] = following
    old_data = Helper.load_json(DATA_FILE)
    if old_data is None:
        print("No data to load, saving current list.")
        Helper.save_json(DATA_FILE,data)
    else:
        followers_diff_positive = Helper.compare_collections(old_data['followers'], data['followers'])
        followers_diff_negative = Helper.compare_collections(data['followers'], old_data['followers'])
        following_diff_positive = Helper.compare_collections(old_data['following'], data['following'])
        following_diff_negative = Helper.compare_collections(data['following'], old_data['following'])
        print(f"Followers: {len(followers)}\n \x09Gained: {followers_diff_positive} \n \x09Lost: {followers_diff_negative}")
        print(f"Following: {len(following)}\n \x09Gained: {following_diff_positive} \n \x09Lost: {following_diff_negative}")
    Helper.save_json(DATA_FILE,data)

    
  