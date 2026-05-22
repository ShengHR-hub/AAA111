"""
企业微信天气推送脚本
部署于 GitHub Actions，每天北京时间 7:00 自动执行
将遵化市天气推送到指定企业微信应用成员
"""

import requests
import json
import os
from datetime import datetime


# ---- 配置区（通过 GitHub Secrets 注入） ----
CORPID = os.environ["WECOM_CORPID"]       # 企业ID
SECRET = os.environ["WECOM_SECRET"]       # 应用 Secret
AGENTID = int(os.environ["WECOM_AGENTID"])  # 应用 AgentID

# 要推送的成员账号列表（企业微信成员UserID），为空则推送给应用可见范围内的所有人
TO_USERS = os.environ.get("WECOM_TO_USERS", "@all")

# 天气城市
CITY = "遵化"


# ---- 获取企业微信 access_token ----
def get_access_token():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    resp = requests.get(url, params={"corpid": CORPID, "corpsecret": SECRET})
    data = resp.json()
    if data.get("errcode") != 0:
        raise Exception(f"获取 access_token 失败: {data}")
    return data["access_token"]


# ---- 获取天气信息（免费 API，无需 key） ----
def get_weather():
    # 使用 wttr.in，format=j1 返回 JSON
    url = f"https://wttr.in/{CITY}?format=j1&lang=zh"
    resp = requests.get(url, timeout=10)
    data = resp.json()

    current = data["current_condition"][0]
    weather_today = data["weather"][0]

    temp_c = current["temp_C"]
    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_speed = current["windspeedKmph"]
    wind_dir = current["winddir16Point"]
    weather_desc = current["weatherDesc"][0]["value"]
    uv_index = current["uvIndex"]

    high = weather_today["maxtempC"]
    low = weather_today["mintempC"]

    sunrise = weather_today["astronomy"][0]["sunrise"]
    sunset = weather_today["astronomy"][0]["sunset"]

    # 空气质量（wttr.in 可能没有，使用备用 API）
    aqi_info = ""
    try:
        aqi_resp = requests.get(
            f"https://wttr.in/{CITY}?format=%C+%h&lang=zh", timeout=5
        )
    except Exception:
        pass

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"""☀️ 遵化市天气预报 | {now}

🌤 天气：{weather_desc}
🌡 当前温度：{temp_c}℃（体感 {feels_like}℃）
📊 今日温度：{low}℃ ~ {high}℃
💧 湿度：{humidity}%
🌬 风力：{wind_dir} {wind_speed} km/h
☀️ 紫外线指数：{uv_index}
🌅 日出/日落：{sunrise} / {sunset}

祝您一天顺利！"""

    return msg


# ---- 发送消息 ----
def send_message(access_token, content):
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
    params = {"access_token": access_token}

    body = {
        "touser": TO_USERS,
        "msgtype": "textcard",
        "agentid": AGENTID,
        "textcard": {
            "title": "遵化市天气预报",
            "description": content,
            "url": f"https://wttr.in/{CITY}?lang=zh",
        },
    }

    resp = requests.post(url, params=params, json=body)
    data = resp.json()
    if data.get("errcode") != 0:
        raise Exception(f"发送消息失败: {data}")
    print("消息发送成功！")


# ---- 主流程 ----
def main():
    print("开始获取天气...")
    weather_msg = get_weather()

    print("获取 access_token...")
    token = get_access_token()

    print("发送消息...")
    send_message(token, weather_msg)


if __name__ == "__main__":
    main()