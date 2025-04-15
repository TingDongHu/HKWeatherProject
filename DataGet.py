import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from collections import defaultdict
import pandas as pd


class WeatherAnalyzer:
    def __init__(self):
        self.client = MongoClient('mongodb://DBadmin:DBpwd@127.0.0.1:27017/admin')
        self.db = self.client['weather_db']
        self.collections = {
            'temperature': self.db['temperatures'],
            'humidity': self.db['humidities'],
            'wind_speed': self.db['wind_speeds'],
            'wind_direction': self.db['other_data'],
            'forecast': self.db['weather_forecasts'],
        }

    # ==================== 多站点统计分析 ====================
    def get_sample_data(self, sample_size=15):
        samples = {
            'temperature': [],
            'humidity': [],
            'wind_speed': [],
            'wind_direction': [],
            'forecast': []
        }

        for metric, collection in self.collections.items():
            try:
                cursor = collection.find().sort("import_time", -1).limit(sample_size)

                for doc in cursor:
                    # 统一处理日期格式
                    date_str = doc.get("日期时间", "")
                    if "月" in date_str and "日" in date_str:  # 处理中文日期格式
                        try:
                            month_day = date_str.split("月")[0] + "月" + date_str.split("日")[0].split("月")[1] + "日"
                            date_str = f"2024年{month_day}"  # 添加假设年份
                        except:
                            date_str = str(doc.get("import_time", ""))

                    sample = {
                        'station': doc.get('station', '未知站点'),
                        'date': date_str,
                        'hourly_data': {}
                    }

                    # 处理24小时数据
                    for h in range(24):
                        hour_key = f"{h:02d}"
                        value = doc.get(hour_key, "nan")

                        # 根据数据类型转换值
                        if metric == 'temperature':
                            value = float(value) if value != "nan" else None
                        elif metric == 'humidity':
                            value = float(value) if value != "nan" else None
                        elif metric == 'wind_speed':
                            value = float(value) if value != "nan" else None
                        elif metric == 'wind_direction':
                            value = str(value) if value != "nan" else None
                        elif metric == 'forecast':
                            value = str(value) if value != "nan" else None

                        sample['hourly_data'][hour_key] = value

                    samples[metric].append(sample)

            except Exception as e:
                print(f"Error processing {metric}: {str(e)}")
                samples[metric] = []
        print(samples)
        return samples
    def get_multi_station_stats(self, metric='temperature', days=7):
        """
        完全修正版多站点统计方法
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 分两步处理：先获取所有文档，再用pandas计算
        docs = list(self.collections[metric].find({
            "import_time": {"$gte": start_date, "$lte": end_date}
        }))

        if not docs:
            return {
                "stations": {},
                "time_range": f"{start_date.date()} 至 {end_date.date()}",
                "message": "没有找到符合条件的数据"
            }

        # 处理数据
        all_data = []
        for doc in docs:
            station = doc['station']
            for h in range(24):
                hour_key = f"{h:02d}"
                value = doc.get(hour_key)
                try:
                    value = float(value) if value not in [None, "nan"] else None
                except (ValueError, TypeError):
                    continue

                if value is not None:
                    all_data.append({
                        "station": station,
                        "hour": hour_key,
                        "value": value,
                        "date": doc["日期时间"]
                    })

        # 使用pandas计算统计值
        df = pd.DataFrame(all_data)
        if df.empty:
            return {
                "stations": {},
                "time_range": f"{start_date.date()} 至 {end_date.date()}",
                "message": "没有有效数值数据"
            }

        # 按站点分组计算
        grouped = df.groupby('station')['value']
        stats = {
            station: {
                "avg": round(group.mean(), 2),
                "max": round(group.max(), 2),
                "min": round(group.min(), 2),
                "latest": round(df[df['station'] == station].iloc[-1]['value'], 2)
            }
            for station, group in grouped
        }

        return {
            "stations": stats,
            "time_range": f"{start_date.date()} 至 {end_date.date()}"
        }

    # ==================== 单站点时间序列分析 ====================

    def get_station_trend(self, station, metric='temperature', days=7):
        """
        获取单站点时间序列数据（优化版）
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        docs = list(self.collections[metric].find({
            "station": station,
            "import_time": {"$gte": start_date, "$lte": end_date}
        }).sort("import_time", 1))

        daily_data = []
        for doc in docs:
            hourly = []
            for h in range(24):
                hour_key = f"{h:02d}"
                value = doc.get(hour_key)
                try:
                    value = float(value) if value not in [None, "nan"] else None
                except (ValueError, TypeError):
                    value = str(value) if value else None

                hourly.append({
                    "hour": hour_key,
                    "value": value
                })

            daily_data.append({
                "date": doc["日期时间"],
                "hourly": hourly
            })

        return {
            "station": station,
            "metric": metric,
            "days": daily_data
        }

    # ==================== 风向特殊处理 ====================

    def get_wind_rose_data(self, station, days=7):
        """
        生成风向玫瑰图数据（优化版）
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        docs = list(self.collections['wind_direction'].find({
            "station": station,
            "import_time": {"$gte": start_date, "$lte": end_date}
        }))

        direction_counts = defaultdict(int)
        total = 0

        for doc in docs:
            for h in range(24):
                direction = doc.get(f"{h:02d}")
                if direction and direction != "nan":
                    direction_counts[direction] += 1
                    total += 1

        direction_map = {
            '北': 0, '东北': 45, '东': 90, '东南': 135,
            '南': 180, '西南': 225, '西': 270, '西北': 315
        }

        rose_data = []
        for dir_name, angle in direction_map.items():
            count = direction_counts.get(dir_name, 0)
            rose_data.append({
                "angle": angle,
                "direction": dir_name,
                "count": count,
                "percentage": round(count / total * 100, 2) if total else 0
            })

        return {
            "directions": rose_data,
            "station": station,
            "time_range": f"{start_date.date()} 至 {end_date.date()}"
        }

    def get_wind_speed_data(self, station=None, days=7):
        """
        获取风速数据
        :param station: 站点名称，None表示所有站点
        :param days: 获取最近多少天的数据
        :return: 风速数据列表
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = {
            "import_time": {"$gte": start_date, "$lte": end_date}
        }

        if station:
            query["station"] = station

        try:
            cursor = self.collections['wind_speed'].find(query).sort("import_time", -1)

            wind_data = []
            for doc in cursor:
                # 处理日期格式
                date_str = doc.get("日期时间", "")
                if "月" in date_str and "日" in date_str:  # 处理中文日期格式
                    try:
                        month_day = date_str.split("月")[0] + "月" + date_str.split("日")[0].split("月")[1] + "日"
                        date_str = f"2024年{month_day}"  # 添加假设年份
                    except:
                        date_str = str(doc.get("import_time", ""))

                # 处理每小时风速数据
                hourly_data = {}
                for h in range(24):
                    hour_key = f"{h:02d}"
                    value = doc.get(hour_key, "nan")

                    # 转换风速值为浮点数
                    try:
                        value = float(value) if value != "nan" else None
                    except (ValueError, TypeError):
                        value = None

                    hourly_data[hour_key] = value

                wind_data.append({
                    'station': doc.get('station', '未知站点'),
                    'date': date_str,
                    'hourly_data': hourly_data
                })

            return wind_data

        except Exception as e:
            print(f"获取风速数据时出错: {str(e)}")
            return []

    def get_station_list(self, metric='wind_speed'):
        """
        获取指定指标的站点列表
        :param metric: 指标名称 (temperature, humidity, wind_speed等)
        :return: 站点列表
        """
        try:
            collection = self.collections.get(metric)
            if not collection:
                return []

            # 使用distinct获取不重复的站点名称
            stations = collection.distinct("station")
            return sorted(stations)

        except Exception as e:
            print(f"获取站点列表时出错: {str(e)}")
            return []

    def get_weather_forecast_data(self, station=None, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        query = {
            "import_time": {"$gte": start_date, "$lte": end_date}
        }
        if station:
            query["station"] = station
        try:
            cursor = self.collections['forecast'].find(query).sort("import_time", -1)

            forecast_data = []
            for doc in cursor:
                # 处理日期格式
                date_str = doc.get("日期时间", "")
                if "月" in date_str and "日" in date_str:  # 处理中文日期格式
                    try:
                        month_day = date_str.split("月")[0] + "月" + date_str.split("日")[0].split("月")[1] + "日"
                        date_str = f"2024年{month_day}"  # 添加假设年份
                    except:
                        date_str = str(doc.get("import_time", ""))

                # 处理每小时天气数据
                hourly_data = {}
                for h in range(24):
                    hour_key = f"{h:02d}"
                    value = doc.get(hour_key, "nan")

                    # 处理天气数据
                    if value != "nan":
                        hourly_data[hour_key] = value
                    else:
                        hourly_data[hour_key] = None

                forecast_data.append({
                    'station': doc.get('station', '未知站点'),
                    'date': date_str,
                    'hourly_data': hourly_data
                })

            return forecast_data

        except Exception as e:
            print(f"获取天气预报数据时出错: {str(e)}")
            return []


# 使用示例
if __name__ == "__main__":
    analyzer = WeatherAnalyzer()
    analyzer.get_weather_forecast()

