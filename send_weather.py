"""
企业微信天气推送脚本
部署于 GitHub Actions，每天北京时间 7:00 自动执行
"""

import requests
import sys
import os
import traceback
from datetime import datetime

# ---- 配置 ----
CORPID = os.environ["WECOM_CORPID"]
SECRET = os.environ["WECOM_SECRET"]
AGENTID = int(os.environ["WECOM_AGENTID"])
TO_USERS = os.environ.get("WECOM_TO_USERS", "@all")
CITY = "遵化"


def get_access_token():
    print("[1/3] 获取 access_token ...")
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    try:
        resp = requests.get(url, params={"corpid": CORPID, "corpsecret": SECRET}, timeout=15)
        print(f"  HTTP {resp.status_code}")
        data = resp.json()
        print(f"  响应: {data}")
        if data.get("errcode") != 0:
            errmsg = data.get("errmsg", "unknown")
            if "not allow" in errmsg.lower() or "ip" in errmsg.lower():
                print("\n!!! 错误原因：企业微信后台未配置可信IP。")
                print("!!! 解决：企业微信管理后台 → 应用管理 → 你的应用 → 企业可信IP → 清空或不限制\n")
            raise Exception(f"access_token 失败: errcode={data.get('errcode')} errmsg={errmsg}")
        print("  access_token 获取成功")
        return data["access_token"]
    except requests.exceptions.Timeout:
        raise Exception("获取 access_token 超时，检查网络")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接企业微信 API，检查网络")


def get_weather():
    print("[2/3] 获取天气数据 ...")
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

    msg = f"""遵化市天气预报 | {now}

天气：{desc}
当前温度：{temp}℃（体感 {feels}℃）
今日温度：{low}℃ ~ {high}℃
湿度：{humidity}%
风力：{wind_dir} {wind_speed} km/h
紫外线指数：{uv}
日出/日落：{sunrise} / {sunset}

祝您一天顺利！"""

    print("  天气数据获取成功")
    return msg


def send_message(token, content):
    print("[3/3] 发送消息 ...")
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
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
    try:
        resp = requests.post(url, params={"access_token": token}, json=body, timeout=15)
        print(f"  HTTP {resp.status_code}")
        data = resp.json()
        print(f"  响应: {data}")
        if data.get("errcode") != 0:
            raise Exception(f"发送失败: errcode={data.get('errcode')} errmsg={data.get('errmsg')}")
        print("  消息发送成功！")
    except requests.exceptions.Timeout:
        raise Exception("发送消息超时")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接企业微信 API")


def main():
    try:
        weather = get_weather()
        token = get_access_token()
        send_message(token, weather)
        print("\n全部完成！")
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()