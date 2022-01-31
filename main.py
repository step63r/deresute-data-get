import argparse
import csv

from msedge.selenium_tools import Edge, EdgeOptions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import Any

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def main(args: Any) -> None:
    """
    メインメソッド

    Parameters
    ----------
    args : Any
        コマンドライン引数
    """
    src_file: str = args.src_file
    engine: str = args.engine
    output_path: str = args.output_path
    exact_card: bool = args.exact_card

    print('WebDriverを構成中...')
    if engine == 'chrome':
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)

    elif engine == 'edge':
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument('headless')
        driver = Edge(executable_path=EdgeChromiumDriverManager().install(), options=options)

    elif engine == 'firefox':
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(executable_path=GeckoDriverManager.install(), firefox_options=options)

    else:
        raise argparse.ArgumentError(f"このエンジン名は使用できません: {engine}")

    driver_wait = WebDriverWait(driver=driver, timeout=10)

    cards = []
    with open(src_file, 'r', encoding='utf-8') as f:
        cards = f.read().splitlines()

    ret = [[
        'カード番号',
        'カード名',
        'タイプ',
        '初期ライフ',
        '初期ボーカル',
        '初期ダンス',
        '初期ビジュアル',
        '最大ライフ',
        '最大ボーカル',
        '最大ダンス',
        '最大ビジュアル',
        'センター効果',
        '特技']]
    
    for card in cards:
        query = card if exact_card else f"{card}＋"
        driver.get(f"https://imascg-slstage-wiki.gamerch.com/{query}")
        driver_wait.until(EC.presence_of_all_elements_located)

        card_type = driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[1]/div/p[2]").text.replace('タイプ\n ', '')
        card_id = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[1]/p[2]").text.replace('カード番号\n ', '').replace(',', ''))

        init_life = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/div/p[1]").text.replace('初期ライフ\n ', '').replace(',', ''))
        init_vo = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/div/p[2]").text.replace('初期ボーカル\n ', '').replace(',', ''))
        init_da = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/div/p[3]").text.replace('初期ダンス\n ', '').replace(',', ''))
        init_vi = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/div/p[4]").text.replace('初期ビジュアル\n ', '').replace(',', ''))

        max_life = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/p[1]").text.replace('最大ライフ\n ', '').replace(',', ''))
        max_vo = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/p[2]").text.replace('最大ボーカル\n ', '').replace(',', ''))
        max_da = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/p[3]").text.replace('最大ダンス\n ', '').replace(',', ''))
        max_vi = int(driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[1]/div[2]/div[2]/p[4]").text.replace('最大ビジュアル\n ', '').replace(',', ''))

        center_ability = driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[2]/p[1]").text.replace('センター効果\n ', '').splitlines()[0]
        special_skill = driver.find_element(By.XPATH, "//*[@id=\"js_async_main_column_text\"]/div[2]/p[3]").text.replace('特技分類\n ', '').splitlines()[0]
        
        row = [card_id, card, card_type, init_life, init_vo, init_da, init_vi, max_life, max_vo, max_da, max_vi, center_ability, special_skill]
        ret.append(row)
        print(query)
    
    with open(output_path, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(ret)
    print('取得完了')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='デレステのカード名から能力値等を取得する')
    parser.add_argument('src_file', type=str, help='検索カード一覧ファイル')
    parser.add_argument('--engine', '-e', type=str, default='chrome', help='ブラウザの種類 [\'chrome\', \'edge\', \'firefox\']')
    parser.add_argument('--output_path', '-o', type=str, default='./result.csv', help='出力ファイルパス')
    parser.add_argument('--exact_card', action='store_true', help='特訓前のカード名でもその名前で検索する')
    args = parser.parse_args()
    main(args)
