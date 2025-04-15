from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import os
import random
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains


def setup_driver():
    """配置Selenium WebDriver，添加反反爬措施"""
    chrome_options = Options()

    # 反反爬设置
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'user-agent={user_agent}')

    # 禁用自动化特征
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 其他常规设置
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--lang=zh-CN")

    # 随机化窗口位置
    chrome_options.add_argument(f"--window-position={random.randint(0, 500)},{random.randint(0, 500)}")

    # 使用代理设置（如果需要）
    # proxy = "123.123.123.123:8888"
    # chrome_options.add_argument(f'--proxy-server={proxy}')

    # 禁用图片加载提高速度
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 修改navigator.webdriver值
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })

    return driver


def human_like_mouse_movement(driver, element):
    """模拟人类鼠标移动"""
    action = ActionChains(driver)
    action.move_to_element_with_offset(element, random.randint(1, 5), random.randint(1, 5))
    action.perform()
    time.sleep(random.uniform(0.2, 0.7))


def human_like_scroll(driver):
    """模拟人类滚动行为"""
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(0, scroll_height, random.randint(100, 300)):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(random.uniform(0.1, 0.3))


def random_delay(min_seconds=1, max_seconds=3):
    """随机延迟"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def clean_text(text):
    """清理文本中的特殊字符和多余空格"""
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\n\t\r]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_filename(name):
    """清理文件名，移除所有特殊字符"""
    name = clean_text(name)
    cleaned = re.sub(r'[^\w\u4e00-\u9fff\-\.$$ ]', '', name)
    cleaned = cleaned.replace(' ', '_')
    return cleaned[:50]


# 定义所有站点及其代码
STATION_LIST = {
    "CCH": "長洲",
    "HKA": "赤鱲角",
    "HKO": "香港天文台",
    "HKS": "黃竹坑",
    "JKB": "將軍澳",
    "LFS": "流浮山",
    "PEN": "坪洲",
    "SEK": "石崗",
    "SHA": "沙田",
    "SKG": "西貢",
    "TKL": "打鼓嶺",
    "TPO": "大埔",
    "TUN": "屯門",
    "TY1": "青衣",
    "WGL": "橫瀾島",
    "SSH": "上水",
    "DF3647": "承啟道多功能智慧燈柱",
    "GF3640": "觀塘市中心多功能智慧燈柱",
    "ARWF_MKA": "旺角空氣質素監測站",
    "ARWF_SFY": "天星碼頭(尖沙咀)",
    "ARWF_TWS": "大環山公園",
    "ARWF_TIT": "啟德工業貿易大樓",
    "ARWF_CCC": "香港中文大學(大學站)",
    "ARWF_CYS": "香港中文大學(伍宜孫書院)",
    "ARWF_WCC": "保良局胡忠中學",
    "ARWF_HMM": "香港海事博物館",
    "ARWF_VIP": "維多利亞公園"
}

# 文件名映射
FILE_NAME_MAPPING = {
    "天气_预测": "weather_forecast",
    "气温_预测_C": "temperature_c",
    "相对湿度_预测_": "humidity_percent",
    "风向_预测_深度": "wind_direction",
    "风速_预测_公里小时": "wind_speed_kmh"
}


def save_to_csv(tables_data, station_name, output_dir="weather_data"):
    """将每个表格保存为单独的CSV文件（使用英文文件名）"""
    station_dir = os.path.join(output_dir, clean_filename(station_name))
    os.makedirs(station_dir, exist_ok=True)

    saved_files = []

    for table_name, df in tables_data.items():
        cleaned_name = clean_filename(table_name)

        en_filename = None
        for ch_pattern, en_pattern in FILE_NAME_MAPPING.items():
            if ch_pattern in cleaned_name:
                en_filename = en_pattern + ".csv"
                break

        if not en_filename:
            en_filename = "weather_data_" + str(len(saved_files)) + ".csv"

        filepath = os.path.join(station_dir, en_filename)

        try:
            df_cleaned = df.applymap(clean_text)
            df_cleaned.to_csv(filepath, index=False, encoding='utf-8-sig')
            saved_files.append(filepath)
            print(f"已保存: {filepath} (原始中文名: {table_name})")
        except Exception as e:
            print(f"保存文件 {en_filename} 时出错: {e}")

    return saved_files


def fetch_dynamic_weather_data(driver, station_code):
    """使用Selenium动态获取天气数据"""
    try:
        url = f"https://maps.weather.gov.hk/ocf/text_sc.html?mode=0&station={station_code}"

        # 随机延迟后再访问
        random_delay(1, 3)
        driver.get(url)

        # 模拟人类滚动行为
        human_like_scroll(driver)

        # 等待页面加载
        try:
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "wxtable"))
            )
            # 模拟人类鼠标移动
            human_like_mouse_movement(driver, element)
        except Exception as e:
            print(f"等待元素加载超时: {e}")
            return None

        # 随机延迟
        random_delay(2, 5)

        # 获取页面源码
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        all_tables_data = {}
        weather_sections = soup.find_all('div', class_='pb-3')

        for section in weather_sections:
            header = section.find('p', class_='wxheader')
            if not header:
                continue

            title = clean_text(header.get_text())
            table = section.find('table', class_='wxtable')
            if not table:
                continue

            data = []
            columns = []

            # 处理表头
            header_row = table.find('tr')
            if header_row:
                first_header = header_row.find('th')
                if first_header:
                    columns.append("日期时间")

                other_headers = header_row.find_all(['th', 'td'])[1:]
                for idx, cell in enumerate(other_headers):
                    colspan = int(cell.get('colspan', 1))
                    cell_text = clean_text(cell.get_text())
                    if cell_text == "香港时间 (小时)":
                        cell_text = f"小时_{idx}"
                    if colspan > 1:
                        columns.extend([f"{cell_text}_{i}" for i in range(colspan)])
                    else:
                        columns.append(cell_text)

            # 处理数据行
            for row in table.find_all('tr')[1:]:
                row_data = []
                first_cell = row.find(['th', 'td'])
                if first_cell:
                    row_data.append(clean_text(first_cell.get_text()))

                data_cells = row.find_all(['th', 'td'])[1:]
                for cell in data_cells:
                    colspan = int(cell.get('colspan', 1))
                    cell_text = clean_text(cell.get_text()) or "N/A"
                    row_data.extend([cell_text] * colspan)

                data.append(row_data)

            if data and columns:
                max_cols = max(len(row) for row in data)
                if len(columns) < max_cols:
                    columns.extend([f"未命名_{i}" for i in range(max_cols - len(columns))])

                df = pd.DataFrame(data, columns=columns[:max_cols])
                all_tables_data[title] = df

        return all_tables_data

    except Exception as e:
        print(f"获取站点 {station_code} 数据时出错: {e}")
        return None


if __name__ == "__main__":
    # 随机化执行间隔
    initial_delay = random.uniform(5, 15)
    print(f"程序将在 {initial_delay:.1f} 秒后开始执行...")
    time.sleep(initial_delay)

    driver = setup_driver()
    try:
        # 随机打乱站点顺序
        stations = list(STATION_LIST.items())
        random.shuffle(stations)

        for station_code, station_name in stations:
            print(f"\n正在获取 {station_name}({station_code}) 的天气数据...")

            # 获取数据
            all_weather_tables = fetch_dynamic_weather_data(driver, station_code)

            if all_weather_tables is not None:
                print(f"\n成功获取 {station_name} 的天气数据表格:")
                for table_name, df in all_weather_tables.items():
                    print(f"\n{table_name}:")
                    print(df.to_string(index=False))

                # 保存数据
                saved_files = save_to_csv(all_weather_tables, station_name)
                print(f"\n已保存 {len(saved_files)} 个CSV文件到 {station_name} 目录")
            else:
                print(f"未能获取 {station_name} 的天气数据表格")

            # 随机间隔，避免请求过于频繁
            delay = random.uniform(5, 15)
            print(f"等待 {delay:.1f} 秒后继续...")
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n用户中断程序执行")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        driver.quit()
        print("\n所有站点数据获取完成！")