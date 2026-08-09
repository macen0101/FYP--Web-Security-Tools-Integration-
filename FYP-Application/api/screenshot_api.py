##################################
#Create time: 20230312
#Create by: CHAN Pak Hei 210054899
##################################
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import datetime,os,sys

# import Alert 
from selenium.webdriver.support import expected_conditions as EC

class ScreenShot:
    def __init__(self,url_list):
        self.url_list = url_list


    def check_folder_exist(self,folder_name:str):
        try:
            isExist = os.path.exists(folder_name)
            if not isExist:
                # Create a new directory because it does not exist
                os.makedirs(folder_name)
                return True
            else:
                return True
        except:
            return False

    def select_driver_by_os(self):
        if sys.platform.startswith('Linux'):
            # return f"{os.path.dirname(__file__)}/website_screenshot/chromedriver_linux64/chromedriver"
            return f"{os.path.dirname(__file__)}/website_screenshot/geckodriver_linux64/geckodriver"
        elif sys.platform.startswith('darwin'):
            # return f"{os.path.dirname(__file__)}/website_screenshot/chromedriver_mac64/chromedriver"
            return f"{os.path.dirname(__file__)}/website_screenshot/geckodriver_macos/geckodriver"
        else:
            return False

    def main(self):
        last_currnet_url = ""
        website_screenshoot_list = list()
        # options = webdriver.ChromeOptions()
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        try:
            # driver = webdriver.Chrome(self.select_driver_by_os(),chrome_options=options)
            driver = webdriver.Firefox(executable_path=self.select_driver_by_os(),options=options, service_log_path=f'{os.path.dirname(__file__)}/website_screenshot/geckodriver.log')
        except FileNotFoundError:
            print("ERROR: driver file error")
            return False
        
        driver.set_window_size(672, 378)
        for url in self.url_list:
            try:
                driver.set_page_load_timeout(4) # set timeout to 4 sec
                driver.get(url)
                # alert =Alert(driver)
                # alert.accept()
            
            except TimeoutException as ex:
                website_screenshoot_list.append({"url":url,"status":False,"png_path":"","note":"target website time out"})
                continue
            # except:
            #     website_screenshoot_list.append({"url":url,"status":False,"png_path":"","note":"other error"})
            #     continue

            now = datetime.datetime.now()
            folder_path =f"{os.path.dirname(__file__)}/website_screenshot/screenshot_history/"
            filename = now.strftime("%Y_%m_%d_%H_%M_%S_%f")
            if self.check_folder_exist(folder_path) == True:
                new_path = f"{os.path.dirname(__file__)}/website_screenshot/screenshot_history/{filename}.png"
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    screenshoot_status= driver.save_screenshot(new_path)
                except:
                    screenshoot_status= driver.save_screenshot(new_path)
                    
                if screenshoot_status == True and driver.current_url != last_currnet_url:
                    website_screenshoot_list.append({"url":url,"status":True,"png_path":new_path})
                    last_currnet_url = driver.current_url
                else:
                    website_screenshoot_list.append({"url":url,"status":False,"png_path":"","note":"file save error"})
                    
        driver.quit()
        return website_screenshoot_list


if __name__ == "__main__":

#     # url = "https://www.moonlol.com/twrp-recovery%E5%8D%A1%E5%88%B7rom-5967.html"
    # web_site_list= ["https://www.google.com/"]
    web_site_list= ["https://google.com"]
    tools_SC = ScreenShot(web_site_list)
    x = tools_SC.main()
    print (x)