from flask import Flask, send_file, render_template, redirect, url_for, request
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
import os
import textwrap
import json
import pygsheets
import datetime
import urllib.request
from urllib.parse import quote
import string

app = Flask(__name__)

@app.route('/')
def hello():
    return 'This is server for sparka'


@app.route('/img/<text>/<canvas_ID>')
def img(text, canvas_ID):
    im = Image.open(f"img/canvas/canvas_{canvas_ID}.png").resize((2434, 2479))
    im = im.convert("RGB")
    print(text)

    box = ((400, 840, 2050, 1740))
    draw = Pilmoji(im)
        
    text = textwrap.fill(text, width=12)
    font_size = 1000

    size = None
    while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
    	font = ImageFont.truetype("img/DFTT_R8.TTC", font_size)
    	size = font.getsize_multiline(text)
    	font_size -= 1
    draw.text((box[0], box[1]), text, "white", font)

    im.save('img/poster.png')
    return send_file('img/poster.png',mimetype='image/png')
    

@app.route('/anoypage/<ID>')
def anoypage(ID):
    
    data = json.load(open('anoypage/account_dictionary.json',encoding='utf-8'))
    #開啟並讀取json檔案
    
    '''f = open('anoypage/sparkpage.html', 'r',encoding='utf-8') #開啟網頁檔案
    websitehtml = f.read() #讀取並存取網頁檔案
    
    websitehtml = websitehtml.replace('{{cnname}}',data[ID]['cnname']) #更改中文帳號名
    websitehtml = websitehtml.replace('{{enname}}',data[ID]['enname']) #更改英文帳號名'''
    
    return render_template('sparkpage.html', **data[ID], ID= ID)

@app.route('/addanoy/<ID>/<cnname>/<enname>')
def addanoy(ID,cnname,enname):

    jsonfile = open('anoypage/account_dictionary.json','r' ,encoding='utf-8').read() #用檢視模式開啟檔案並存入變數
    
    #防止ID重複
    if ID in jsonfile:
        return '錯誤，本ID已存在'
    
    jsonfile = jsonfile[0:-1] + f', "{ID}":「"cnname":"{cnname}", "enname":"{enname}"」」' 
    #加上新的資訊(用「」取代{}解決符號衝突問題
    
    #復原替代符號
    jsonfile = jsonfile.replace('「',"{")
    jsonfile = jsonfile.replace('」',"}")
    
    savejsonfile = open('anoypage/account_dictionary.json','w' ,encoding='utf-8') #用編輯模式開啟檔案
    savejsonfile.write(jsonfile) #將修改解果存回檔案
    
    #________________建立表單工作區_________________#
    
    gc = pygsheets.authorize(service_file='anoypage/notional-grove-386009-56b8b2dcdb4c.json')
    #設置google密鑰

    sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1hxuM-6el_JJkDZTvLpDt4-QcDjSfokYySf05j2ucJh8/')
    #開啟表單
    
    sht.add_worksheet(ID)
    #新增工作區
    
    ws = sht.worksheet_by_title(ID)
    #開啟工作區
    
    ws.update_values('A{1}:D{1}' ,[['MSG', 'ID', 'TIME', 'index'] ] )
    #輸入標題
    
    ws.update_value('D2', '0') 
    #重製index
    
    #________________建立底圖_________________#
    
    url = str(f'https://rest.apitemplate.io/52c77b238504d6f4@LnY73QO6/image.png?cnnameB.text=*{cnname}*&cnnameS.text=*{cnname}%20|%20自動發文*&enname.text=*{enname}*')
    url = quote(url, safe=string.printable)


    filename = os.path.join('img','canvas', 'canvas_' + ID +'.png')
    urllib.request.urlretrieve(url, filename) #存檔
    
    return jsonfile


@app.route('/form/<ID>')
def form(ID):
    return render_template('Fromtest.html' , ID= ID)

@app.route('/formSubmit/<ID>', methods=['POST'])
def Submit(ID):
    msg = request.form['msg'] #接收表單資料
    
    gc = pygsheets.authorize(service_file='anoypage/notional-grove-386009-56b8b2dcdb4c.json')
    #設置google密鑰
    
    sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1hxuM-6el_JJkDZTvLpDt4-QcDjSfokYySf05j2ucJh8/')
    #開啟表單
    
    ws = sht.worksheet_by_title(ID)
    #依照ID開啟工作表
    
    msgINDEX = int(ws.cell('D2').value)
    #讀取序號
    
    time = datetime.datetime.now().strftime('%H:%M:%S') #確定時間

    ws.update_value('A'+ str(msgINDEX +2), msg) #輸入訊息
    ws.update_value('B'+ str(msgINDEX +2), ID) #輸入ID
    ws.update_value('C'+ str(msgINDEX +2), time) #輸入時間

    
    ws.update_value('D2', str(msgINDEX +1))
    msgINDEX += 1
    #更新序號
    
    return img(msg, ID)