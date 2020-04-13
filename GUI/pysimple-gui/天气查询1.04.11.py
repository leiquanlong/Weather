#!/user/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Mr 雷'

import PySimpleGUI as sg
import requests
import json
import re
from lxml import etree
from PIL import Image

im = Image.open(r'tianqi.jpg')
im.save('tianqi.png')
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
sg.theme('Purple')
label = [[sg.Image(r'tianqi.png')],
         [sg.Text('请输入城市、乡镇、街道、景点名称查询天气',size=(33,0)),sg.InputText(size=(20,0))],
         [sg.Button('确认',pad=((120,0),20)), sg.Button('退出',pad=((150,0),20))],
         [sg.Text('请选择查询区域')],
         [sg.Listbox(values=['暂无信息,请输入关键城市进行显示'],size=(58,10),key='box',enable_events=True)]]
win1 = sg.Window('天气查询',label)
win2_active = False

def submit(city,id):
    weather_data = get_weather(id)
    frame_layout =[]
    for i in range(len(weather_data)):
        if len(weather_data[0]) == 6:
            frame_layout.append([[sg.Text('天气：' + weather_data[i][1])],
                                 [sg.Text('最高气温：' + weather_data[i][2])],
                                 [sg.Text('最低气温：' + weather_data[i][3])],
                                 [sg.Text('风向：' + weather_data[i][4])],
                                 [sg.Text('风级：' + weather_data[i][5])]])
        else:
            frame_layout.append([[sg.Text('天气：' + weather_data[i][1])],
                                 [sg.Text('风向：' + weather_data[i][2])],
                                 [sg.Text('风级：' + weather_data[i][3])]])
    layout = [[sg.Text('一周天气状况',justification='center')],
              [sg.Frame(weather_data[0][0],frame_layout[0]),
              sg.Frame(weather_data[1][0],frame_layout[1]),
              sg.Frame(weather_data[2][0],frame_layout[2]),
              sg.Frame(weather_data[3][0],frame_layout[3]),
              sg.Frame(weather_data[4][0],frame_layout[4]),
              sg.Frame(weather_data[5][0],frame_layout[5]),
              sg.Frame(weather_data[6][0],frame_layout[6])]]
    win2 = sg.Window(f'{city}天气预报', layout)
    return win2

def get_city(name):
    r = requests.get('http://toy1.weather.com.cn/search?cityname={}'.format(name),headers=header)
    r.encoding = r.apparent_encoding
    text = r.text.replace('(', '').replace(')', '')
    infos = json.loads(text)
    citys = []
    info_dict = {}
    for info in infos:
        id = info['ref'].split('~')[0]
        info = list(''.join(re.findall('[\u4e00-\u9fa5]', info['ref'])))
        new_info = []
        for i in info:
            if i not in new_info:
                new_info.append(i)
        new_info = ''.join(new_info)
        citys.append(new_info)
        info_dict[new_info] = id
    return citys,info_dict

def get_weather(id):
    data = []
    url1 = f'http://www.weather.com.cn/weather/{id}.shtml'
    url2 = f'http://forecast.weather.com.cn/town/weathern/{id}.shtml'
    r = requests.get(url1,headers=header)
    if r.text != '<!-- empty -->':
        r.encoding = r.apparent_encoding
        html = etree.HTML(r.text)
        elements = html.xpath('//ul[@class="t clearfix"]/li')
        for element in elements:
            date = element.xpath('./h1/text()')[0]
            weather = element.xpath('./p[@class="wea"]/text()')[0]
            min_tem = element.xpath('./p[@class="tem"]/i/text()')
            max_tem = element.xpath('./p[@class="tem"]/span/text()')
            if len(max_tem):
                if '℃' not in max_tem[0]:
                    max_tem = max_tem[0] + '℃'
                else:
                    max_tem = max_tem[0]
            else:
                max_tem = '无'
            if len(min_tem):
                if '℃' not in min_tem[0]:
                    min_tem = min_tem[0] + '℃'
                else:
                    min_tem = min_tem[0]
            else:
                min_tem = '无'
            wind_direction = '、'.join(element.xpath('./p[@class="win"]/em/span/@title'))
            wind_scale = element.xpath('./p[@class="win"]/i/text()')[0]
            data.append([date,weather,max_tem,min_tem,wind_direction,wind_scale])
    else:
        r = requests.get(url2, headers=header)
        r.encoding = r.apparent_encoding
        html = etree.HTML(r.text)
        elements = html.xpath('//ul[@class="blue-container backccc"]/li')
        data_elements = html.xpath('//ul[@class="date-container"]/li')
        for i in range(1,len(elements)-1):
            date = ' '.join(data_elements[i].xpath('./p/text()'))
            weather = elements[i].xpath('./p[@class="weather-info"]/text()')[0].strip()
            wind_direction = '、'.join(elements[i].xpath('./div[@class="wind-container"]/i/@title'))
            wind_scale = elements[i].xpath('./p[@class="wind-info"]/text()')[0].strip()
            data.append([date, weather, wind_direction, wind_scale])
    return data

while True:
    event1,value1 = win1.read()
    if event1 in (None,'退出'):
        break
    if event1 == '确认':
        city,info = get_city(value1[0])
        win1['box'].update(city)
        value1['box'] = False
    if value1['box'] and not win2_active:
        try:
            if value1['box'][0] in info.keys():
                id = info[value1['box'][0]]
                win2_active = True
                win1.Hide()
                win2 = submit(value1[0],id)
                while True:
                    event2, value2 = win2.read()
                    if event2 is None:
                        win2.close()
                        win2_active = False
                        win1.UnHide()
                        break
        except:
            continue
