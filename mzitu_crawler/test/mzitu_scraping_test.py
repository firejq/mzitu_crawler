# 异步IO--协程版本
# TODO 重复爬取后会抛出异常，待解决
import asyncio
import os
import random
import time
# def getips():
#     '''
#     爬取haoip.cc上可用的代理ip
#     :return: 代理ip列表
#     '''
#     iplist = []
#     html = requests.get("http://haoip.cc/tiqu.htm", 'lxml')
#     iplistn = re.findall(r'r/>(.*?)<b', html.text, re.S)
#     for ip in iplistn:
#         i = re.sub('\n', '', ip)
#         iplist.append(i.strip())
#         # print(i.strip())
#     return iplist
from multiprocessing import Queue, Process

import requests
from bs4 import BeautifulSoup


def getips():
    '''
    爬取http://www.xicidaili.com/nn/首页的高匿代理ip
    :return: 代理ip列表
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    url = 'http://www.xicidaili.com/nn/'
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list


def get(url, timeout=None, proxy=None, num_retries=6, extra=None):
    '''
    自定义请求逻辑：
    先尝试直接连接请求，随机使用User-Agent，
    若请求失败，重试6次，
    若重试6次之后仍旧失败，开始使用代理ip，
    若使用代理ip请求失败，则随机更换代理ip，最高尝试更换6次代理ip，
    更换6次代理ip后仍旧请求失败，放弃使用代理，延长timeout直接连接
    :param url:
    :param timeout:
    :param proxy:
    :param num_retries:
    :return:
    '''
    UserAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3072.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.32',
        ''
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.9.2.1000 Chrome/39.0.2146.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400',
        'Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36 MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 QQ/5.2.1.302 NetType/WIFI Mem/28']
    headers = {'User-Agent': random.choice(UserAgents)}
    if extra is not None:
        headers[extra[0]] = extra[1]
    if proxy is None:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except BaseException:
            if num_retries > 0:  # num_retries:限定的重试次数
                print(u'获取网页出错，10秒后将重新获取，倒数第：',
                      num_retries, u'次')
                time.sleep(10)
                return get(url, timeout, num_retries=(num_retries - 1))
            else:
                print(u'重试6次失败，开始使用代理')
                time.sleep(10)
                iplist = getips()
                IP = ''.join(str(random.choice(iplist)).strip())
                proxy = {'http': IP}
                return get(url, timeout, proxy)
    else:
        try:
            iplist = getips()
            IP = ''.join(str(random.choice(iplist)).strip())
            proxy = {'http': IP}
            print(u'当前代理是：', proxy)
            return requests.get(url, headers=headers, proxies=proxy)
        except BaseException:
            if num_retries > 0:
                time.sleep(10)
                iplist = getips()
                IP = ''.join(str(random.choice(iplist)).strip())
                proxy = {'http': IP}
                print(u'使用代理获取网页失败，正在更换代理，10秒后将重新获取倒数第',
                      num_retries, u'次')
                print(u'当前代理是：', proxy)
                return get(url, timeout, proxy, num_retries - 1)
            else:
                print(u'更换6次代理仍旧失败，代理可能已失效，取消代理')
                return get(url, 3)


async def img_get(url, timeout=None, proxy=None, num_retries=6, extra=None):
    '''
    自定义请求逻辑：
    先尝试直接连接请求，随机使用User-Agent，
    若请求失败，重试6次，
    若重试6次之后仍旧失败，开始使用代理ip，
    若使用代理ip请求失败，则随机更换代理ip，最高尝试更换6次代理ip，
    更换6次代理ip后仍旧请求失败，放弃使用代理，延长timeout直接连接
    :param url:
    :param timeout:
    :param proxy:
    :param num_retries:
    :return:
    '''
    UserAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3072.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.32',
        ''
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.9.2.1000 Chrome/39.0.2146.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400',
        'Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36 MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 QQ/5.2.1.302 NetType/WIFI Mem/28']
    headers = {'User-Agent': random.choice(UserAgents)}
    if extra is not None:
        headers[extra[0]] = extra[1]
    if proxy is None:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except BaseException:
            if num_retries > 0:  # num_retries:限定的重试次数
                print(u'获取网页出错，10秒后将重新获取，倒数第：',
                      num_retries, u'次')
                time.sleep(10)
                return get(url, timeout, num_retries=(num_retries - 1))
            else:
                print(u'重试6次失败，开始使用代理')
                time.sleep(10)
                iplist = getips()
                IP = ''.join(str(random.choice(iplist)).strip())
                proxy = {'http': IP}
                return get(url, timeout, proxy)
    else:
        try:
            iplist = getips()
            IP = ''.join(str(random.choice(iplist)).strip())
            proxy = {'http': IP}
            print(u'当前代理是：', proxy)
            return requests.get(url, headers=headers, proxies=proxy)
        except BaseException:
            if num_retries > 0:
                time.sleep(10)
                iplist = getips()
                IP = ''.join(str(random.choice(iplist)).strip())
                proxy = {'http': IP}
                print(u'使用代理获取网页失败，正在更换代理，10秒后将重新获取倒数第',
                      num_retries, u'次')
                print(u'当前代理是：', proxy)
                return get(url, timeout, proxy, num_retries - 1)
            else:
                print(u'更换6次代理仍旧失败，代理可能已失效，取消代理')
                return get(url, 3)


async def img_download(img_url, topic_url):
    # 为图片起名
    name = str(img_url).split('/')[-1]
    # 向图片地址发起请求并获取response
    extra = ['Referer', topic_url]
    img = await img_get(url=img_url, extra=extra)
    # 在本地以追加模式创建二进制文件
    f = open(name, 'ab')
    # 将response的二进制内容写入到文件中
    f.write(img.content)
    # 关闭文件流对象
    f.close()


def topic_download(topic_queue):
    while not topic_queue.empty():
        topic = topic_queue.get()
        r = {
            'href': topic['href'],
            'text': topic['text']
        }

        dirname = str(r['text']).replace(' ', '_').replace('\\', '_').replace(
            '/', '_').replace(':', '_').replace('*', '_').replace(
            '?', '_').replace('"', '_').replace('<', '_').replace(
            '>', '_').replace('|', '_')
        path = os.path.join('D:\\mzitu', dirname)

        if os.path.exists(path):
            print(r['href'], r['text'], '文件夹已存在，进行下一个主题的爬取')
            continue
        else:
            print(r['href'], r['text'], '开始爬取')
            os.makedirs(path)
            os.chdir(path)

            html = get(r['href']).text
            res_soup = BeautifulSoup(html, 'lxml')

            # 解决AttributeError异常
            flag = 0
            while flag == 0:
                try:
                    max_span = res_soup.find('div', class_='pagenavi').findAll(
                        'span')[-2].get_text()
                    flag = 1
                except AttributeError:
                    print('捕获AttributeError异常，1秒后重试')
                    time.sleep(3)
                    res_soup = BeautifulSoup(html, 'lxml')
                    continue

            img_list = []
            for page in range(1, int(max_span) + 1):
                page_url = r['href'] + '/' + str(page)

                # 获取图片地址res_img
                res_soup = BeautifulSoup(get(page_url).text, 'lxml')
                # 解决AttributeError异常
                flag = 0
                while flag == 0:
                    try:
                        res_img = res_soup.find(
                            'div', class_='main-image').find('img')['src']
                        flag = 1
                    except AttributeError:
                        print('捕获AttributeError异常，1秒后重试')
                        time.sleep(3)
                        res_soup = BeautifulSoup(get(page_url).text, 'lxml')
                        continue
                # 将该主题的所有url放到列表中
                img_list.append(res_img)

            begin_time = time.time()
            loop = asyncio.get_event_loop()
            tasks = [img_download(img_url, r['href']) for img_url in img_list]
            # print('开始进入事件循环')
            loop.run_until_complete(asyncio.wait(tasks))
            # print('事件循环结束')
            loop.close()
            print(r['href'], r['text'], '爬取完毕，耗时【'
                  + str(time.time() - begin_time) + '】秒')


if __name__ == '__main__':
    index_url = 'http://www.mzitu.com'
    start_html = get(index_url)
    Soup = BeautifulSoup(start_html.text, 'xml')

    last_page_url = Soup.find('div', class_='nav-links').findAll(
        'a', class_='page-numbers')[-1]['href']
    last_page_number = str(last_page_url).split('/')[-2]

    for index in range(1, int(last_page_number) + 1):
        print('开始爬取第', index, '页')
        url = index_url + '/page/' + str(index)
        Soup = BeautifulSoup(get(url).text, 'lxml')

        # 为解决因网络问题随机出现的AttributeError异常，加此循环逻辑
        # TODO 寻找更好的解决方案
        flag = 0
        while flag == 0:
            try:
                all_a = Soup.find('ul', id='pins').findAll('span')
                flag = 1
            except AttributeError:
                print('捕获AttributeError异常，1秒后重试')
                time.sleep(5)
                Soup = BeautifulSoup(get(url).text, 'lxml')
                continue

        for i in range(0, len(all_a)):
            all_a[i] = all_a[i].find('a')
        all_a = all_a[0:len(all_a):3]

        res = list()
        for i in range(0, len(all_a)):
            res.append({'href': all_a[i]['href'], 'text': all_a[i].get_text()})

        topic_queue = Queue(maxsize=50)
        # 将该页的所有主题加入队列
        for r in res:
            topic_queue.put({
                'href': r['href'],
                'text': r['text']
            })

        # 多进程并发进行该页面主题的爬取
        # TODO 开了多进程后，即便程序结束运行，仍有很多个进程驻留在内存中，怎么让这些无用进程自动销毁？
        process_number = 1
        for process_number_i in range(process_number):
            process = Process(target=topic_download, args=(topic_queue,))
            process.start()

        # 等待该页面所有topic都下载完毕后才返回
        while not topic_queue.empty():
            time.sleep(0.5)
            continue
        # TODO 当topic队列为空时，实际上最后的正在执行的几个进程还没执行完，因此会出现：print
        # 该页已经爬取完毕，实际上还没完毕，解决：更改其它的检测方式，而不是检测队列是否为空
        print('第', index, '页爬取完毕')
    print('全站爬取完毕')
    exit()
