'''
爬取琉璃神社中的所有种子连接

基本功能：
1. 获取迅雷种子连接，并且接上迅雷连接头
2. 获取百度网盘连接，并且街上百度网盘连接头
3. 附上连接地址，里番（本子）的名称

注意：真爱身体，补充营养，小撸怡情大撸伤身
'''
from bs4 import BeautifulSoup
from selenium import webdriver
from SeedGeterTask import DownloadMission, DownloadThread;
import SeedGeterTask

root_url = 'http://hacg.la/wp/'  # 扫描根目录
phantom_path = "E:\phantomjs-2.1.1-windows\\bin\phantomjs.exe"
text_save_path = ''  # 结果存储目录，比如“学习资料”

r_seed_link_match = r'>[a-zA-Z0-9]{30,100}'
head_seed = 'magnet:?xt=urn:btih:'


class OldDriverCar(object):
    def __init__(self):
        self.web_driver = webdriver.PhantomJS(executable_path=phantom_path)

    def get_current_page_html(self, url):
        '''获取当前页面的内容'''
        self.web_driver.get(url)
        return self.web_driver.page_source

    def get_next_page_url(self, html_source):
        '''获取下一个页面的页面地址'''
        try:
            soup = BeautifulSoup(html_source, "html.parser")
            next_page_cell = soup.select('a.nextpostslink')
            page = next_page_cell[0]['href']
            return page
        except Exception as e:
            print("已经是最后一页的，快去学习吧~")
            # 停止下载任务
            mission = DownloadMission(DownloadMission.MISSION_STOP, "", "")
            SeedGeterTask.addDownloadTask(mission)
            exit(0)
        pass

    def get_page_contain_url(self, html_source):
        '''获取当前页面中所有的文章连接'''
        try:
            soup = BeautifulSoup(html_source, "html.parser")
            contain_article_list = soup.select('h1.entry-title > a')
            article_link_list = []  # 保存连接
            for article in contain_article_list:
                article_link_list.append(article['href'])

            return article_link_list
        except Exception as e:
            print(e)

    def get_seed_url(self, article_url):
        '''
        获取当前文章的种子地址，有两个任务：
        1. 获取地址 2.识别是百度网盘还是迅雷地址
        '''
        mission = DownloadMission(DownloadMission.MISSION_NOMAL, article_url, article_url)
        SeedGeterTask.addDownloadTask(mission)


def take_your_safety_belt():
    print('老司机要发车咯！请带好你的安全带~翻车事故一概不负责！')
    print('本次始发站：' + root_url)
    print("准备咯......倒数三秒~")
    # time.sleep(3)

    SeedGeterTask.startDownload() #启动下载任务管理器
    old_driver = OldDriverCar()
    crawl_page_queue = [root_url]  # 保存待爬页路径 （未去重）
    crawl_content_queue = []  # 保存待爬内容页面路径
    seen_page_queue = set(crawl_content_queue)  # 保存待爬路径 （去重）
    while crawl_page_queue:
        page_url = crawl_page_queue.pop()
        html_source = old_driver.get_current_page_html(page_url)
        crawl_page_queue.append(old_driver.get_next_page_url(html_source))
        crawl_content_queue = old_driver.get_page_contain_url(html_source)
        for article in crawl_content_queue:
            if article not in seen_page_queue:
                old_driver.get_seed_url(article)
                seen_page_queue.add(article)


if __name__ == '__main__':
    take_your_safety_belt()
