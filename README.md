# 香港天文台天气信息采集可视化系统
爬取的网站链接：https://maps.weather.gov.hk/ocf/text_sc.html?mode=0&station
![image](https://github.com/user-attachments/assets/b36c9e50-f055-4c06-a6b4-5c5f6bddec84)


## 模块划分
- 爬虫模块：Weather_Get.py
- 数据存储：SaveToMongo.py
- 数据分析统计：DataGet.py
- 可视化模块：app.py
## 配置环境
基于`requirement.txt`完成库配置后，需要修改`Weather_Get.py`中的`webdriver`的链接地址,以及`SaveToMongo.py`和`DataGet.py`中的本地MongoDB库的链接，确保数据可以正常存储和读取。
## 使用说明
运行`Weather_Get.py`文件从香港天文台网站抓取数据。
抓取的数据默认存储在csv文件中，抓取完成后运行SaveToMongo.py进行数据清洗和存储。
存储后运行app.py在网页端进行可视化。
## 技术栈说明
### 爬虫部分
爬虫使用Selenium库和Chrome浏览器驱动来抓取数据。基于Selenium框架实现香港天气信息数据的自动化采集，采用模块化设计思路：首先通过精心配置的ChromeDriver初始化浏览器实例，注入反检测脚本并设置随机用户代理以规避反爬机制；随后模拟人类操作行为，包括随机延迟、平滑滚动和动作链点击，精准定位并触发页面查询功能。
### 可视化部分
通过re库、wordcloud库以及利用MongoDB中的aggregation管道函数等对爬取的到的天气信息的统计，再将统计以后的数据通过图表地方式展示在前端，即后端传数据，前端Echarts绘制图表。

## 运行测试结果
### MongoDB数据库的compass可视化工具的存储部分数据：
![image](https://github.com/user-attachments/assets/f421ade3-ec91-4f7d-9357-dead4ab05173)

### 可视化结果：
![image](https://github.com/user-attachments/assets/6bff1d9e-c660-4e5f-b819-f5b88f388eeb)

![image](https://github.com/user-attachments/assets/fa652dbf-5d23-40b6-8bd9-3fba56b1c147)

![image](https://github.com/user-attachments/assets/42c83cef-b0db-4401-b2e7-2302e04dae45)

![image](https://github.com/user-attachments/assets/820eb943-e360-4051-8b6a-f1ffc4ac481a)

