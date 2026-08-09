from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': '127.0.0.1:8080',
    'sslProxy': '127.0.0.1:8080',
})

firefox_options = webdriver.FirefoxOptions()
firefox_options.proxy = proxy

driver = webdriver.Firefox(options=firefox_options)

driver.get("https://brutelogic.com.br/gym.php")

input_elements = driver.find_elements(By.CSS_SELECTOR, 'input[id], input[name]')
input_dict = {}
for input_element in input_elements:
    input_type = input_element.get_attribute('type')
    input_require = input_element.get_attribute('')
    input_id = input_element.get_attribute('id')
    input_name = input_element.get_attribute('name')
    if input_type:
        if input_type not in input_dict:
            input_dict[input_type] = []
        if input_id:
            input_dict[input_type].append(input_id)
        elif input_name:
            input_dict[input_type].append(input_name)

for input_type in input_dict.keys():
    if input_type == 'text':
        for input_name_or_id in input_dict[input_type]:
            input_element = driver.find_element(By.CSS_SELECTOR, f'input[id="{input_name_or_id}"], input[name="{input_name_or_id}"]')
            input_element.send_keys('Test_faeifnevnesesnn')
    elif input_type == 'password':
        for input_name_or_id in input_dict[input_type]:
            input_element = driver.find_element(By.CSS_SELECTOR, f'input[id="{input_name_or_id}"], input[name="{input_name_or_id}"]')
            input_element.send_keys('Password')
    elif input_type == 'email':
        for input_name_or_id in input_dict[input_type]:
            input_element = driver.find_element(By.CSS_SELECTOR, f'input[id="{input_name_or_id}"], input[name="{input_name_or_id}"]')
            input_element.send_keys('test@gmail.com')
    elif input_type == 'url':
        for input_name_or_id in input_dict[input_type]:
            input_element = driver.find_element(By.CSS_SELECTOR, f'input[id="{input_name_or_id}"], input[name="{input_name_or_id}"]')
            input_element.send_keys('www.test.com')

submit_elements = driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
for submit_element in submit_elements:
    submit_element.submit()
if driver.current_url != "https://brutelogic.com.br/gym.php":
    print("Form submission successful!")
else:
    print("Form submission failed.")
driver.quit()

print(input_dict)
