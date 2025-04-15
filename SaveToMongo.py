import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime
import re
from urllib.parse import quote_plus

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

# 文件名映射到集合名称
COLLECTION_MAPPING = {
    "weather_forecast": "weather_forecasts",
    "temperature_c": "temperatures",
    "humidity_percent": "humidities",
    "wind_direction": "wind_directions",
    "wind_speed_kmh": "wind_speeds"
}


def clean_text(text):
    """清理文本中的特殊字符和多余空格"""
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\n\t\r]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_station_and_type(filepath):
    """从文件路径提取站点名称和数据类型"""
    parts = filepath.split(os.sep)
    if len(parts) >= 3:
        station_name = parts[-2]  # 站点目录名
        data_type = os.path.splitext(parts[-1])[0]  # 去掉.csv后缀
        return station_name, data_type
    return "unknown", "unknown"


def csv_to_mongodb(csv_folder="weather_data",
                   mongodb_uri="mongodb://DBadmin:DBpwd@127.0.0.1:27017/admin",
                   db_name="weather_db"):
    """
    将CSV文件数据导入MongoDB
    :param csv_folder: 包含CSV文件的根目录
    :param mongodb_uri: MongoDB认证连接字符串
    :param db_name: 数据库名称
    """
    # 连接MongoDB
    try:
        print(f"正在连接到MongoDB: {mongodb_uri.split('@')[-1]}")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]

        # 测试连接是否有效
        db.command('ping')
        print("✓ 成功连接到MongoDB服务器")
    except Exception as e:
        print(f"× 连接MongoDB失败: {str(e)}")
        print("请检查: 1. MongoDB服务是否运行 2. 认证信息是否正确 3. 网络连接")
        return

    processed_files = 0
    skipped_files = 0
    total_records = 0

    print("\n开始处理CSV文件...")
    # 遍历所有CSV文件
    for root, _, files in os.walk(csv_folder):
        for file in files:
            if file.endswith(".csv"):
                filepath = os.path.join(root, file)
                station_name, data_type = get_station_and_type(filepath)

                try:
                    # 读取CSV文件
                    df = pd.read_csv(filepath)

                    # 获取对应的集合名称
                    collection_name = COLLECTION_MAPPING.get(data_type, "other_data")
                    collection = db[collection_name]

                    # 转换数据格式（展平结构）
                    records = []
                    for _, row in df.iterrows():
                        # 创建展平的文档结构
                        doc = {
                            "station": station_name,
                            "source_file": file,
                            "import_time": datetime.now()
                        }
                        # 添加所有数据字段（不再嵌套）
                        doc.update({k: clean_text(str(v)) for k, v in row.items()})
                        records.append(doc)

                    # 批量插入MongoDB
                    if records:
                        result = collection.insert_many(records)
                        processed_files += 1
                        total_records += len(result.inserted_ids)
                        print(f"✓ 成功: {station_name}/{file} → {collection_name} ({len(records)}条)")

                except pd.errors.EmptyDataError:
                    skipped_files += 1
                    print(f"× 跳过: {filepath} (空文件)")
                except Exception as e:
                    skipped_files += 1
                    print(f"× 失败: {filepath} - {str(e)}")
                    continue

    client.close()

    print("\n处理结果:")
    print(f"总文件数: {processed_files + skipped_files}")
    print(f"成功处理: {processed_files}")
    print(f"跳过文件: {skipped_files}")
    print(f"总插入记录: {total_records}")

    if skipped_files > 0:
        print("\n注意: 有文件被跳过，请检查上述错误信息")


if __name__ == "__main__":
    # 配置MongoDB连接
    mongodb_uri = "mongodb://DBadmin:DBpwd@127.0.0.1:27017/admin"
    db_name = "weather_db"

    print("==== CSV数据导入MongoDB工具 ====")
    print(f"目标数据库: {db_name}")
    print(f"连接地址: {mongodb_uri.split('@')[-1]}")

    # 执行导入
    csv_to_mongodb(
        csv_folder="weather_data",
        mongodb_uri=mongodb_uri,
        db_name=db_name
    )

    print("\n导入完成！")