from flask import Flask, render_template, jsonify
from DataGet import WeatherAnalyzer
from datetime import datetime
from flask import request
app = Flask(__name__)
analyzer = WeatherAnalyzer()

# 首页路由
@app.route('/')
@app.route('/index/')
def index():
    samples = analyzer.get_sample_data(15)

    return render_template('index.html', samples=samples)

# 温湿度业面
@app.route('/humidities/')
def humidities():

    return render_template('tempandhumi.html')

# 风向玫瑰图页面
@app.route('/rose/')
def wind_rose_page():
    return render_template('rose.html')


@app.route('/api/wind_speeds')
def api_wind_speeds():
    station = request.args.get('station', None)
    days = int(request.args.get('days', 3))

    data = analyzer.get_wind_speed_data(station=station, days=days)

    return jsonify({
        'status': 'success',
        'data': data
    })


@app.route('/wind_speeds/')
def wind_speeds_page():
    stations = analyzer.get_station_list('wind_speed')
    return render_template('wind_speeds.html', stations=stations)

    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/weather_forecasts')
def api_weather_forecasts():
    station = request.args.get('station', None)
    days = int(request.args.get('days', 3))

    # 获取天气预报数据
    data = analyzer.get_weather_forecast_data(station=station, days=days)

    # 输出数据以检查
    print(f"返回的天气预报数据：{data}")  # 调试输出

    return jsonify({
        'status': 'success',
        'data': data
    })



@app.route('/weather_forecast/')
def weather_forecast_page():
    return render_template('weather_forecast.html', )



# ============== API 接口 ==============

# 获取多站点统计数据的API
@app.route('/api/multi_stats/<metric>')
@app.route('/api/multi_stats/<metric>/<int:days>')
def get_multi_stats(metric='temperature', days=7):
    try:
        data = analyzer.get_multi_station_stats(metric, days)
        return jsonify({
            'status': 'success',
            'data': data,
            'metric': metric,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 获取单站点趋势数据的API
@app.route('/api/station_trend/<station>/<metric>')
@app.route('/api/station_trend/<station>/<metric>/<int:days>')
def get_station_trend(station='上水', metric='temperature', days=7):
    try:
        data = analyzer.get_station_trend(station, metric, days)
        return jsonify({
            'status': 'success',
            'data': data,
            'station': station,
            'metric': metric
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 获取风向玫瑰图数据的API
@app.route('/api/wind_rose/<station>')
@app.route('/api/wind_rose/<station>/<int:days>')
def get_wind_rose(station='上水', days=7):
    try:
        data = analyzer.get_wind_rose_data(station, days)
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)