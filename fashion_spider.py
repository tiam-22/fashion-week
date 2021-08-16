# -*- coding: utf-8 -*-
# @Time    : 2021/4/5 11:29
# @Author  : 田蜜
# @FileName: fashion_spider.py

import os
import time
import requests
import selenium

from tqdm import tqdm
from selenium import webdriver


def main():
    # 做几个需要遍历的字段
    brand_list = []
    season_list = ['aw', 'ss']
    years_list = ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
    place_list = ['paris', 'milan', 'london', 'newyork']
    pages_list = [item for item in range(1, 16)]

    # 创建火狐窗口
    driver = webdriver.Firefox()
    start_time = time.time()
    for season in tqdm(season_list):
        for year in tqdm(years_list):
            for place in tqdm(place_list):
                # get brand list
                url = f'http://shows.vogue.com.cn/{year}-{season}-RTW/{place}-2.html'
                driver.get(url)
                brand_list = \
                    driver.find_elements_by_css_selector('#main > div.xc-list > div.content > div > div.xcl-city > ul')[
                        0].text.split('\n')
                for brand in brand_list:
                    brand = brand.replace(' ', '-').replace('.', '').lower()
                    # 如果不存在该文件夹则创建，下面的makedirs是可以遍历创建，如果用mkdir的话会报错
                    if not os.path.exists(f'./data/{season}/{year}/{place}/'):
                        os.makedirs(f'./data/{season}/{year}/{place}/{brand}')
                    num = 0  # 方便下面命名
                    for page in pages_list:
                        url_brand = f'http://shows.vogue.com.cn/{brand}/{year}-{season}-RTW/runway/page-{page}.html'

                        driver.get(url_brand)  # 打开网页

                        # 检查是否有第一张照片
                        first_pic = driver.find_elements_by_css_selector(
                            '#main > div.xc-list > div.content > div.section.xcl-p4 > ul > li:nth-child(1) > a > img')

                        if len(first_pic) == 0:  # 如果连第一张图片都没有就直接判定停止
                            print(f'{year} 年 {season} 季节 {place} 秀场 无第 {page} 页，停止！')
                            break
                        else:
                            print(f'{year} 年 {season} 季节 {place} 秀场 第 {page} 页有内容，开始爬取。。。')
                            for index in range(1, 17):
                                try:
                                    img_url = driver.find_element_by_xpath(
                                        f'/html/body/div[1]/div[3]/div[2]/div[1]/div/div[2]/ul/li[{index}]/a/img').get_property(
                                        'src')
                                    r = requests.get(img_url)
                                except selenium.common.exceptions.NoSuchElementException:  # 这个try是用来捕捉和处理不满16张照片的那个异常
                                    print(f'{year} 年 {season} 季节 {place} 秀场 第 {page} 页已到结尾，停止爬取，开始下个秀场！')
                                    break
                                # 往文件夹里面写，命名我写的比较繁琐是为了你方便后期用split去处理和打标签
                                with open(f'./data/{season}/{year}/{place}/{season}_{year}_{place}_{num}.png',
                                          'wb') as f:
                                    f.write(r.content)
                                num += 1

    print(f'所有图片爬取完成，共花费{time.time() - start_time / 60} mins')


if __name__ == '__main__':
    main()
