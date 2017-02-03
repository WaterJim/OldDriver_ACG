# 处理下载模块
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import re
import FileWriter

'''
主要有两个功能
1. 向队列中添加下载任务（注意锁）
2. 从队列中取出任务，并进行下载（注意锁）
3. 下载完成后，将结果存放到磁盘中
'''

# lock = threading.Lock()
queue = queue.Queue(maxsize=100)  # 最多保存1000个下载任务
proxies = {
    "http": "dev-proxy.oa.com:8080"
}

r_seed_link_match = r'>[a-zA-Z0-9]{30,100}'
head_seed = 'magnet:?xt=urn:btih:'


def addDownloadTask(task):
    '''
    向队列中添加任务（生产者）
    一旦队列满了，则会堵塞调用线程
    :return:
    '''
    queue.put(task, 1)


def getDownloadTaskFromQueue():
    '''
    从队列中获取任务（消费者）
    一旦队列为空，则堵塞调用线程
    :return:
    '''
    return queue.get(True)


def downloadAndSave(url, savePath):
    try:
        response = requests.get(url, proxies=proxies)
        html_source = response.text
        soup = BeautifulSoup(html_source, "html.parser")
        # 获取文章名称
        title_entity = soup.select('head > title')[0]
        title = title_entity.text
        seed_urls = re.findall(r_seed_link_match, html_source)
        seed_save = []
        for link in seed_urls:
            print(link)
            seed_save.append(head_seed + link)

        file_task = FileWriter.FileWriteMission(FileWriter.FileWriteMission.MISSION_NOMAL,
                                                title, url, seed_save)
        FileWriter.add_file_write_task(file_task)
    except Exception as e:
        print(e)
        pass


def startDownload():
    download_thread = DownloadThread()
    download_thread.start()

    file_writer = FileWriter.FileWriterTask()
    file_writer.start()


class DownloadMission(object):
    MISSION_STOP = 1
    MISSION_NOMAL = 2

    def __init__(self, type, url='', path=''):
        self.url = url
        self.savePath = path
        self.missionType = type


# 启动线程，不断地从队列中获取任务
class DownloadThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.flag = True
        self.downloadThreadPool = ThreadPoolExecutor(32)

    def run(self):
        while self.flag == True:
            task = getDownloadTaskFromQueue()
            if task != None:
                # 设置停止任务
                if task.missionType == DownloadMission.MISSION_STOP:
                    self.flag = False
                    continue
                self.downloadThreadPool.submit(
                    downloadAndSave, task.url, task.savePath)
        print("Download task stop!")


if __name__ == '__main__':
    downloadThread = DownloadThread()
    downloadThread.start()
