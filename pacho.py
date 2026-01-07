import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

db_config =   """
            CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            tags TEXT
            );
            """
db_path = 'quotes.db'
url = 'https://quotes.toscrape.com/js/'


if __name__ == '__main__':

    # 資料庫建立
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(db_config)
    conn.commit()

    # 瀏覽器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5.0)
    browser.get(url)

    print('爬取中...')

    for n in range(1,6): # 總共要爬取5頁

        quotes = browser.find_elements(By.XPATH ,"//div[@class='quote']")

        for quote in quotes:
            # 獲取內容、作者、標籤資料
            text = quote.find_element(By.XPATH ,".//span[@class='text']").text
            author = quote.find_element(By.XPATH ,".//small[@class='author']").text
            tags = ','.join(field.text for field in quote.find_elements(By.XPATH ,".//a[@class='tag']"))
            # 儲存到資料庫
            cursor.execute('INSERT INTO quotes (text ,author ,tags) VALUES (? ,? ,?)' ,(text ,author ,tags))
            conn.commit()
        
        print(f' 第{n}頁: ok')
        
        # 下一頁
        if(n<5):
            next = browser.find_element(By.XPATH ,"//li[@class='next']/a")
            actions = ActionChains(browser)
            actions.move_to_element(next).click(next).perform()
            WebDriverWait(browser ,30.0).until(presence_of_element_located((By.XPATH ,f"//li[@class='next']/a[@href='/js/page/{n+2}/']")))

    print('結束')
    cursor.close()
    conn.close()