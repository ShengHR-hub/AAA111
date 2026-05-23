"""
WxPusher 天气推送脚本
部署于 GitHub Actions，每天北京时间 7:00 自动执行
推送到微信，无需企业微信，无 IP 限制
"""

import requests
import sys
import os
import traceback
from datetime import datetime

# ---- 配置（通过 GitHub Secrets 注入） ----
APP_TOKEN = os.environ["WXPUSHER_APPTOKEN"]
TOPIC_ID = "44623"  # 主题ID，家人扫码订阅后都能收到
CITY = "遵化"


def get_weather():
    print("[1/2] 获取天气数据 ...")
    url = f"https://wttr.in/{CITY}?format=j1&lang=zh"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "curl/7.0"})
        print(f"  HTTP {resp.status_code}")
        if resp.status_code != 200:
            raise Exception(f"wttr.in 返回非200: {resp.status_code}")
        data = resp.json()
    except requests.exceptions.Timeout:
        raise Exception("wttr.in 请求超时")
    except Exception as e:
        raise Exception(f"天气获取失败: {e}")

    current = data["current_condition"][0]
    today = data["weather"][0]

    temp = current["temp_C"]
    feels = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_speed = current["windspeedKmph"]
    wind_dir = current["winddir16Point"]
    desc = current["weatherDesc"][0]["value"]
    uv = current["uvIndex"]
    high = today["maxtempC"]
    low = today["mintempC"]
    sunrise = today["astronomy"][0]["sunrise"]
    sunset = today["astronomy"][0]["sunset"]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"""## 遵化市天气预报 | {now}

- **天气**：{desc}
- **当前温度**：{temp}℃（体感 {feels}℃）
- **今日温度**：{low}℃ ~ {high}℃
- **湿度**：{humidity}%
- **风力**：{wind_dir} {wind_speed} km/h
- **紫外线指数**：{uv}
- **日出/日落**：{sunrise} / {sunset}

祝您一天顺利！"""

    print("  天气数据获取成功")
    return msg


def send_message(content):
    print("[2/2] 发送消息到微信 ...")
    url = "https://wxpusher.zjiecode.com/api/send/message"
    body = {
        "appToken": APP_TOKEN,
        "content": content,
        "contentType": 3,
        "topicIds": [int(TOPIC_ID)],
        "summary": f"遵化市天气预报 {datetime.now().strftime('%m-%d')}",
    }
    try:
        resp = requests.post(url, json=body, timeout=15)
        print(f"  HTTP {resp.status_code}")
        data = resp.json()
        print(f"  响应: {data}")
        if data.get("code") != 1000:
            raise Exception(f"发送失败: code={data.get('code')} msg={data.get('msg')}")
        print("  消息发送成功！")
    except requests.exceptions.Timeout:
        raise Exception("发送消息超时")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接 WxPusher API")


def main():
    try:
        content = get_weather()
        send_message(content)
        print("\n全部完成！")
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()