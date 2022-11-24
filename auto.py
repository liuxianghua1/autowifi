import socket
import os
import time
import socket
import subprocess
import requests
from retrying import retry
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime



# 查询ip
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


request_count = 0
wait_wifi_time = 5
request_url = 'https://www.baidu.com'
wifi_name = 'JSCY'
#校园网账号 
user_account= ''
# 校园网密码
user_passwor= ''
# 校园网类型 中国移动填cmcc 中国联通填unicom 中国电信填telecom
login_type="unicom"

login_url = "http://10.255.255.154:801/eportal/?c=Portal&a=login&callback=dr1004&login_method=1&user_account=%2C0%2C{}%40{}&user_password={}&wlan_user_ip={}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=3.3.3&v=5272".format(user_account,login_type,user_passwor,get_host_ip())



def _result(result):
    return result is None

@retry(stop_max_attempt_number=2,stop_max_delay=1000, wait_random_min=1000, wait_random_max=2000, retry_on_result=_result)
def my_request_get(url, headers=None):
    global request_count
    request_count = request_count + 1
    print('Request Count Is: {}'.format(request_count))
    response = requests.get(url, timeout=6)
    if response.status_code != 200:
        raise requests.RequestException('my_request_get error!!!!')
    return response


# 连上校园网wifi
def open_wifi():
    global request_url
    cmd = 'networksetup -setairportpower en0 on'
    subprocess.call(cmd, shell=True)
    cmd = 'networksetup -setairportnetwork en0  {wifi_name}'.format(
        wifi_name=wifi_name)
    subprocess.call(cmd, shell=True)
    print('open Wifi after {}s'.format(wait_wifi_time))
    
    time.sleep(wait_wifi_time)
    try:
        requests.get(login_url, timeout=6)
        r = requests.get(request_url, timeout=6)
        if r.status_code == 200:
            print('重启')
    except Exception as e:
        print(e)
        open_wifi()


class PingObject():
    def job():
        try:
            print(request_url)
            if my_request_get(request_url).status_code == 200:
                print('正常')
        except Exception as e:
            print(e)
            open_wifi()


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(PingObject.job, trigger='interval', seconds=10, id='my_job_id_test', next_run_time=datetime.now())

    scheduler.start()

    print('按 Ctrl+{0} 退出'.format('Break' if os.name == 'nt' else 'C'))
    try:
        while True:
            time.sleep(2)  # 其他任务是独立的线程执行
    except (KeyboardInterrupt, SystemExit):
        print('退出!')