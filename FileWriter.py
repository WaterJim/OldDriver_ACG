import queue
import threading
import os

queue = queue.Queue(maxsize=100)  # 最多保存1000个下载任务
queue_lock = threading.Lock()


class FileWriteMission(object):
    MISSION_STOP = 1
    MISSION_NOMAL = 2

    def __init__(self, type, title='', url='', seed=[]):
        self.file_title = title
        self.file_url = url
        self.file_seed = seed
        self.missionType = type


def add_file_write_task(task):
    queue_lock.acquire()
    queue.put(task, 1)
    queue_lock.release()


def pop_file_write_task():
    return queue.get(True)


def file_write():
    queue_lock.acquire()
    parentPath = os.path.abspath('.')
    filePath = os.path.join(parentPath, "html_bilibili.txt")
    file = open(filePath, mode="a", encoding="UTF-8")
    while not queue.empty():
        task = pop_file_write_task()
        file.write('-------------------------------------------------\n')
        file.write(task.file_title + '\n')
        file.write(task.file_url + '\n')
        for seed in task.file_seed:
            file.write(seed + '\n')
        file.write('-------------------------------------------------\n')

    file.flush();
    file.close();
    queue_lock.release()


class FileWriterTask(threading.Thread):
    def __init__(self):
        super().__init__()
        self.flag = True

    def run(self):
        while self.flag == True:
            if queue.qsize() > 5:
                file_write()
