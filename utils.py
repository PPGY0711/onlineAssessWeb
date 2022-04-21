# -*- coding: utf-8 -*-
"""
@objective: global helper functions
@author: pengguanyan
@update date: 2022/04/21
"""

from scipy.optimize import curve_fit
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.pyplot import MultipleLocator, margins
# 从pyplot导入MultipleLocator类，这个类用于设置刻度间隔
import matplotlib.ticker as mtick
import os
import matplotlib
import seaborn as sns
import json

# 指定默认字体（没用上，黑体用宋体替代了）
CHINESE_FONT = 'SimHei'
# 解决负号'-'显示为方块的问题
config = {
    "font.family": 'serif', # 衬线字体
    "font.size": 12, # 相当于小四大小
    "font.serif": ['SimHei'], # 黑体
    "mathtext.fontset": 'stix', # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False # 处理负号，即-号
}
rcParams.update(config)
sns.set(font=CHINESE_FONT)  # 解决Seaborn中文显示问题
SongTiFont = matplotlib.font_manager.FontProperties(fname='./fonts/Songti.ttc')


# 生成8位长度的唯一标识
def generateUUID():
    array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
             "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
             "v", "w", "x", "y", "z",
             "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
             "V", "W", "X", "Y", "Z"
             ]
    id = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(id[start:end], 16)
        buffer.append(array[val % 62])
    return "".join(buffer)


# def makePdf(flag, data, pdfFileName, listPages):
#     report_name = pdfFileName[:-4]
#     report_dir = os.path.join(report_name)
#     if not os.path.isdir(report_dir):
#         os.makedirs(report_dir)
#
#     zone = ""
#     if 0 < data['y30'] and data['y30'] <= 0.15:
#         zone = "A"
#     elif 0.15 < data['y30'] and data['y30'] <= 0.25 and 0.15 < data['e1_e0'] and data['e1_e0'] <= 0.25:
#         zone = "B"
#     elif 0.15 < data['y30'] and data['y30'] <= 0.25 and data['e1_e0'] > 0.25:
#         zone = "C"
#     elif data['y30'] > 0.25 and 0.25 < data['e1_e0'] and data['e1_e0'] <= 0.35:
#         zone = "D"
#     elif data['y30'] > 0.25 and data['e1_e0'] > 0.35:
#         zone = "E"
#
#     # 加载static图片
#     listPages.append("./static/img/01.png")
#     if flag == "long":
#         listPages.append("./static/img/02.png")
#         listPages.append("./static/img/03.png")
#         listPages.append("./static/img/04.png")
#         listPages.append("./static/img/05.png")
#
#     import pdfkit
#     import webbrowser
#     import PyPDF2 as pypdf
#     from PIL import Image
#     from fpdf import FPDF
#
#     def txt2html2pdf(data, out_html, out_pdf):
#         f = open(out_html, 'w')
#         if flag == "long":
#             message = """
#             <!DOCTYPE html>
#             <html>
#             <head>
#             <meta charset="utf-8">
#             <title>空调系统逐日能耗评估结果</title>
#             <style type="text/css">
#                 table.info{a1}
#
#                 table.zero{a2}
#
#                 table.comment{a3}
#
#                 td.comment{a4}
#                 td.px{a5}
#                 td.firstc{a6}
#             </style>
#             </head>
#
#             <body>
#             <h1 align="center"><b>空调系统逐日能耗评估结果</b></h1>
#
#             <table class="info" border="0">
#                 <tr>
#                     <td width="5px"> </td>
#                     <td align="left", width=20%>
#                         <!-- <b >建筑名称</b> -->
#                     </td>
#                     <td>{name}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>建筑地址</td></b> -->
#                     </td>
#                     <td>{address}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <div class="formula">
#                             <label><b>建筑面积 (</b> </label>
#                             $m^2$
#                             <b>)</b>
#                         </div> -->
#                         <div>
#                             <!-- 建筑面积  $(m^2)$ -->
#                         </div>
#                     </td>
#                     <td>{area}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>空调系统冷源形式</td></b> -->
#                     </td>
#                     <td>{coldsource}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>空调系统末端形式</td></b> -->
#                     </td>
#                     <td>{endform}</td>
#                 </tr>
#             </table>
#
#             <br>
#
#             <table class="info">
#                 <tr>
#                     <td width="5px"> </td>
#                     <td width=20%>
#                         <!-- <b>使用评价方法</b> -->
#                     </td>
#                     <td width=30%>长期评价</td>
#
#                     <td width="20%"><b>Sigmoid拟合公式</b></td>
#                     <td>
#                         <div  style="color:rgba(0, 0, 0, 0)">
#                             $E(t)=\frac(E_1)(1+e^(-k(t-t_0)))+E_0aaaaaa$
#                         </div>
#                     </td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <div class="formula">
#                             <!-- $[E_1+E_0,E_(30^\circ C)]$ -->
#                         </div>
#                     </td>
#                     <td>{e1_e0}</td>
#
#                     <td><b>所属评价区间</b></td>
#                     <td>{range}</td>
#                 </tr>
#             </table>
#
#             <!-- <table class="zero" border-bottom="0">
#                 <tr align="center">
#                     <td>
#                         <img src="static/img01.png" width="100%">
#                     </td>
#
#                     <td>
#                         <img src="static/img02.png" width="100%">
#                     </td>
#                 </tr>
#             </table> -->
#
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#
#
#
#             <table class="comment" cellspacing="0">
#                 <tr>
#                     <!-- <td class="px" align="center"></td> -->
#                     <td class="firstc" width="10%" align="center"><b>区域名称</b></td>
#                     <td class="comment" width="20%" align="center">
#                         <!-- <div>$E_(T=30^\circ C)^(\ast)$<b>区间值 </b>$kWh/m^2$</div> -->
#                     </td>
#                     <td class="comment" align="center" width="20%">
#                         <!-- <div class="formula">$E_1^\ast+E_0^\ast$<b>区间值 </b>$kWh/m^2$</div> -->
#                     </td>
#                     <td class="comment" align="center"><b>结论及建议</b></td>
#                 </tr>
#
#                 <tr{colorA}>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center"><b>A区</b></td>
#                     <td class="comment" align="center"><div>(0,0.15]</div></td>
#                     <td class="comment" align="center">-</td>
#                     <td class="comment">空调系统运行优秀。</td>
#                 </tr>
#
#                 <tr{colorB}>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center"><b>B区</b></td>
#                     <td class="comment" align="center"><div>(0.15,0.25]</div></td>
#                     <td class="comment" align="center"><div class="formula">(0.15,0.25]</div></td>
#                     <td class="comment">空调系统运行良好。有一定节能潜力。需在冷源与末端的符合匹配上进行节能诊断，部分符合的节能运行等。</td>
#                 </tr>
#
#                 <tr{colorC}>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center"><b>C区</b></td>
#                     <td class="comment" align="center"><div class="formula">(0.15,0.25]</div></td>
#                     <!-- <td class="comment" align="center"><div class="formula">>0.25</div></td> -->
#                     <td class="comment" align="center">>0.25</td>
#                     <td class="comment">空调系统运行良好。</td>
#                 </tr>
#
#                 <tr{colorD}>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center"><b>D区</b></td>
#                     <td class="comment" align="center"><div class="formula">>0.25</div></td>
#                     <td class="comment" align="center"><div class="formula">(0.25,0.35]</div></td>
#                     <td class="comment">空调系统运行较差。系统节能潜力很大，系统设计较为合理，运行不当造成运行能耗较大。主要从冷源机组与输配系统等能耗占比较大的组件开始进行节能诊断分析。</td>
#                 </tr>
#
#                 <tr{colorE}>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center"><b>E区</b></td>
#                     <td class="comment" align="center"><div class="formula">>0.25</div></td>
#                     <td class="comment" align="center"><div class="formula">>0.35</div></td>
#                     <td class="comment">空调系统运行效果很差。可能的原因：系统设计缺陷，冷源机组或输配系统出现较大故障等。需要对系统中各部分组件深度节能诊断。</td>
#                 </tr>
#             </table>
#             </body>
#             </html>
#             """.format(a1="{border: 1px solid #000;width: 100%;}",
#                     a2="{border: 0;width: 100%;}",
#                     a3="{border-right: 1px solid #000;border-bottom: 1px solid #000;width: 100%;}",
#                     a4="{border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     a5="{width: 5px;border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     a6="{border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     name=data["buildingName"],
#                     address=data["address"],
#                     area=data["area"],
#                     coldsource=data["coldSource"],
#                     endform=data["terminalEquipment"],
#                     e1_e0="{:.4f}".format(data['e1_e0']),
#                     range=zone+"区",
#                     colorA=''' style="color:#0000FF"''' if zone == "A" else "",
#                     colorB=''' style="color:#0000FF"''' if zone == "B" else "",
#                     colorC=''' style="color:#0000FF"''' if zone == "C" else "",
#                     colorD=''' style="color:#0000FF"''' if zone == "D" else "",
#                     colorE=''' style="color:#0000FF"''' if zone == "E" else "")
#         else:
#             message = """
#             <!DOCTYPE html>
#             <html>
#             <head>
#             <meta charset="utf-8">
#             <title>空调系统逐日能耗评估结果</title>
#             <style type="text/css">
#                 table.info{a1}
#
#                 table.zero{a2}
#
#                 table.comment{a3}
#
#                 td.comment{a4}
#                 td.px{a5}
#                 td.firstc{a6}
#             </style>
#             </head>
#
#             <body>
#             <h1 align="center"><b>空调系统逐日能耗评估结果</b></h1>
#
#             <table class="info" border="0">
#                 <tr>
#                     <td width="5px"> </td>
#                     <td align="left", width=20%>
#                         <!-- <b >建筑名称</b> -->
#                     </td>
#                     <td>{name}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>建筑地址</td></b> -->
#                     </td>
#                     <td>{address}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <div class="formula">
#                             <label><b>建筑面积 (</b> </label>
#                             $m^2$
#                             <b>)</b>
#                         </div> -->
#                         <div>
#                             <!-- 建筑面积  $(m^2)$ -->
#                         </div>
#                     </td>
#                     <td>{area}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>空调系统冷源形式</td></b> -->
#                     </td>
#                     <td>{coldsource}</td>
#                 </tr>
#
#                 <tr>
#                     <td width="5px"> </td>
#                     <td>
#                         <!-- <b>空调系统末端形式</td></b> -->
#                     </td>
#                     <td>{endform}</td>
#                 </tr>
#             </table>
#
#             <br>
#
#             <table class="info">
#                 <tr>
#                     <td width="5px"> </td>
#                     <td width=20%>
#                         <b>使用评价方法</b>
#                     </td>
#                     <td width=30%>短期评价</td>
#
#                     <td width="20%">
#                         <!-- <b>Sigmoid拟合公式</b> -->
#                     </td>
#                     <td style="color:rgba(0,0,0,0)">
#                         <div>
#                         $E(t)=\frac(E_1)(1+e^(-k(t-t_0)))+E_0$aaaa
#                         </div>
#                     </td>
#                 </tr>
#
#             </table>
#
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#             <br>
#
#
#
#             <table class="comment" cellspacing="0">
#                 <tr>
#                     <!-- <td class="px" align="center"></td> -->
#                     <td class="firstc" width="10%" align="center"><b>区域范围</b></td>
#                     <td class="comment" width="20%" align="center">
#                         <b>区域特征</b>
#                     </td>
#                 </tr>
#
#                 <tr>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center">上线之上</td>
#                     <td class="comment" align="center"><div>高能耗区</div></td>
#                 </tr>
#
#                 <tr>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center">介于上下线之间</td>
#                     <td class="comment" align="center"><div>良好区域</div></td>
#                 </tr>
#
#                 <tr>
#                     <!-- <td class="px"></td> -->
#                     <td class="firstc" align="center">低于下线</td>
#                     <td class="comment" align="center"><div class="formula">低能耗区</div></td>
#                 </tr>
#
#             </table>
#
#
#             </body>
#
#             </html>
#
#             """.format(a1="{border: 1px solid #000;width: 100%;}",
#                     a2="{border: 0;width: 100%;}",
#                     a3="{border-right: 1px solid #000;border-bottom: 1px solid #000;width: 100%;}",
#                     a4="{border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     a5="{width: 5px;border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     a6="{border-left: 1px solid #000;border-top: 1px solid #000;}",
#                     name=data["buildingName"],
#                     address=data["address"],
#                     area=data["area"],
#                     coldsource=data["coldSource"],
#                     endform=data["terminalEquipment"])
#
#         f.write(message)
#         f.close()
#
#         config=pdfkit.configuration(wkhtmltopdf=r'/usr/local/bin/wkhtmltopdf')
#         pdfkit.from_file(out_html, out_pdf, configuration=config, )
#
#     def html2pdf(html_path, output_path, wkhtmltopdf_path):
#         # output_path = "pdfkit_test.pdf"
#         config=pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
#         pdfkit.from_file(html_path, output_path, configuration=config, )
#
#     def mpdf(pdfFileName, listPages):
#         if flag == "long":
#             cover = Image.open(listPages[0])
#             width, height = cover.size
#             pdf = FPDF()
#             pdf.add_page()
#             pdf.image(listPages[0], 10, 75, w=width*0.12, h=height*0.12)
#             pdf.image(listPages[1], 105, 75, w=width*0.12, h=height*0.12)
#
#             # i01 = Image.open(listPages[1])
#             # pdf.image(listPages[2], 14, 23, w=0.035*i01.size[0], h=0.038*i01.size[1])
#             i01 = Image.open(listPages[2])
#             pdf.image(listPages[2], 14, 23, w=0.017*i01.size[0], h=0.017*i01.size[1])
#
#             i02 = Image.open(listPages[3])
#             pdf.image(listPages[3], 14, 52, w=0.07*i02.size[0], h=0.07*i02.size[1])
#
#             i03 = Image.open(listPages[4])
#             pdf.image(listPages[4], 33, 152, w=0.06*i03.size[0], h=0.06*i03.size[1])
#
#             i04 = Image.open(listPages[5])
#             pdf.image(listPages[5], 70, 152, w=0.06*i04.size[0], h=0.06*i04.size[1])
#
#             i05 = Image.open(listPages[6])
#             pdf.image(listPages[6], 142, 50, w=0.05*i05.size[0], h=0.05*i05.size[1])
#         else:
#             cover = Image.open(listPages[0])
#             width, height = cover.size
#             pdf = FPDF()
#             pdf.add_page()
#             pdf.image(listPages[0], 55, 60, w=width*0.14, h=height*0.14)
#
#             i01 = Image.open(listPages[1])
#             pdf.image(listPages[1], 14, 23, w=0.017*i01.size[0], h=0.017*i01.size[1])
#
#         pdf.output(pdfFileName, 'F')
#
#     pdf01 = os.path.join(report_dir, "pdfkit_test.pdf")
#     pdf02 = os.path.join(report_dir, "imgs.pdf")
#     html_report = os.path.join(report_dir, "report.html")
#     pdf03 = report_name + ".pdf"
#     html_static = "./static/homepage.html"
#
#     # html2pdf(html_static, pdf01, r'/usr/local/bin/wkhtmltopdf')
#     txt2html2pdf(data, html_report, pdf01)
#     mpdf(pdf02, listPages)
#     # !cd /Users/dengzihao/Desktop/ht/outlierDetection
#     # with open("pdfkit_test.pdf", "rb") as inFile, open("imgs.pdf", "rb") as overlay:
#     with open(pdf02, "rb") as inFile, open(pdf01, "rb") as overlay:
#         original = pypdf.PdfFileReader(inFile)
#         background = original.getPage(0)
#         foreground = pypdf.PdfFileReader(overlay).getPage(0)
#
#         # merge the first two pages
#         background.mergePage(foreground)
#
#         # add all pages to a writer
#         writer = pypdf.PdfFileWriter()
#         for i in range(original.getNumPages()):
#             page = original.getPage(i)
#             writer.addPage(page)
#
#         # write everything in the writer to a file
#         with open(pdf03, "wb") as outFile:
#             writer.write(outFile)


def getAssessLevel(y30, e1_e0):
    if 0 < y30 <= 0.15:
        return 'A'
    elif y30 <= 0.25 and 0.15 < e1_e0 <= 0.25:
        return 'B'
    elif y30 <= 0.25 and e1_e0 > 0.25:
        return 'C'
    elif y30 > 0.25 and 0.25 < e1_e0 <= 0.35:
        return 'D'
    else:
        return 'E'


class LineFit():
    def __init__(self, jsonData, coldSource, figPath, caseId):
        # 给LineFit的是json格式的数据，即修正成具有 'temperature', 'energy_consume',('fix_consume')的dict
        self.coldSource = coldSource
        self.figPath = figPath  # 记录对应的caseId，保存时互相对应
        self.caseId = caseId  # 记录对应的caseId，保存时互相对应
        self.data = jsonData['records']
        self.xData = np.array(self.data['temperature'])
        self.yData = np.array(self.data['energy_consume'])
        if 'fix_consume' in self.data:
            # 有修正数据时进行修正
            self.fData = np.array(self.data['fix_consume'])
            scopDict = {'螺杆式冷水机组': 4.2, '离心式冷水机组': 4.4, '风冷冷水机组': 3.0, '多联式空调机组': 3.8}
            q0 = 0.2  # 标准热扰，调研案例均值为：0.2kWh/(m^2d)
            if self.coldSource != "其他":
                scop = scopDict[self.coldSource]
                self.yData = self.yData - (self.fData - q0) / scop

    @staticmethod
    def readFromExcel(file, ext):
        if ext == 'csv':
            # 默认第一行是表头
            data = pd.read_csv(file, header=0, engine='python')
        else:
            # .xls/.xlsx，同样默认第一行是表头，否则第一行的数据会被忽略
            data = pd.read_excel(file, header=0)
        print(data.shape)
        return data

    def fix(self):
        import pandas as pd
        from sklearn.cluster import KMeans

        threshold = 4 # 离散点阈值
        k = 6 # 聚类类别
        b = 500 # 聚类最大循环次数
        # key = 2.5
        key = 2.0

        def model_data_zs(k, b):
            data = {"x": self.xData, "y": self.yData}
            data = pd.DataFrame(data)

            data_zs = 1.0 * (data - data.mean()) / data.std()

            model = KMeans(n_clusters=k, max_iter=b)
            model.fit(data_zs)

            # 标准化数据及其类别
            r = pd.concat(
                [data_zs, pd.Series(model.labels_, index=data.index)], axis=1)
            # print(r.head())
            # 每个样本对应的类别
            r.columns = list(data.columns) + [u'聚类类别']  # 重命名表头
            return model, r, k

        def make_norm(model, k, r):
            norm = []
            for i in range(k):
                norm_tmp = r[['x', 'y']][
                    r[u'聚类类别'] == i] - model.cluster_centers_[i]
                norm_tmp = norm_tmp.apply(np.linalg.norm, axis=1)  # 求出绝对距离
                norm.append(norm_tmp / norm_tmp.median())  # 求相对距离并添加
            norm = pd.concat(norm)
            return norm

        def draw_discrete_point(norm, key):
            pd_norm = norm
            count, mean, std, min, p25, p50, p75, max = pd_norm.describe()
            Q3 = p75
            Q1 = p25
            IQR = Q3 - Q1
            bottom = Q1 - key * IQR
            top = Q3 + key * IQR

            discrete_points = norm[norm > top]  # 离散点阈值

            x_abnormal, y_abnormal, x_normal, y_normal = list(), list(), list(), list()
            for idx, y in enumerate(self.yData):
                if idx in discrete_points:
                    x_abnormal.append(self.xData[idx])
                    y_abnormal.append(y)
                else:
                    x_normal.append(self.xData[idx])
                    y_normal.append(y)

            # x = np.linspace(15, 45, 100)
            x = np.linspace(int(np.min(self.xData))-1, int(np.max(self.xData))+1, 100)

            self.xData = x_normal
            self.yData = y_normal

        model, r, k = model_data_zs(k, b)
        norm = make_norm(model, k, r)
        
        draw_discrete_point(norm, key)
        print('All Done')

    def fit_long_term_data(self):
        print("\nLONG TERM\n")
        def sigmoid(x, L, x0, k, b):
            y = L / (1 + np.exp(-k * (x - x0))) + b
            return (y)

        def draw_fit_curve(coef):
            # seaborn设置风格
            sns.set_style('whitegrid')
            e1_e0 = coef[0] + coef[3]
            # 控制上下左右尽量包含所有的散点，同时留出一定的边距
            x = np.linspace(min(30, np.min(self.xData))-1, max(30, np.max(self.xData)+1), 100)
            y = sigmoid(x, *coef)
            # 设置画布大小
            plt.figure(figsize=(8, 6))
            # 原始数据画散点图
            plt.scatter(self.xData, self.yData, marker='o', c='white', edgecolors='black', label=u'Raw Data')
            # 画E(t=30℃)
            y30 = sigmoid(np.array([30, ]), *popt)
            plt.scatter(np.array([30, ]), y30, marker='*', c='royalblue', s=60, label=u'E(T=30℃)')
            # 拟合曲线
            plt.plot(x, y, c='orangered', label=u'Sigmoid Fit Curve')
            # plt.plot(x, y, c='orangered', label=r'$\frac{E_1}{1+e^k-a}$')
            # 辅助线 x=30
            plt.plot(np.array([30]*5), np.linspace(0, y30, 5), c='royalblue', linestyle='--')
            # 辅助线 y=E1+E0
            # plt.text(np.min(self.xData), e1_e0+0.01, 'E1 + E0 = %.3f' % (e1_e0), c='orangered',
                    #  size=15, fontproperties=SongTiFont)
            plt.plot(np.linspace(0, np.max(x), 5), np.array([e1_e0]*5), c='c', linestyle='--', label='E1 + E0 = %.3f' % (e1_e0))
            # 辅助线 y=E30
            # plt.text(np.min(self.xData), y30 + 0.01, 'E(T=30℃) = %.3f' % (y30), c='orangered',
                    #  size=15, fontproperties=SongTiFont)
            plt.plot(np.linspace(0, 30, 5), np.array([y30] * 5), c='royalblue', linestyle='--', label='E(T=30℃) = %.3f' % (y30))
            # 控制坐标轴范围
            x_major_locator = MultipleLocator(2)
            # 把x轴的刻度间隔设置为1，并存在变量里
            y_major_locator = MultipleLocator(0.05)
            # 把y轴的刻度间隔设置为10，并存在变量里
            ax = plt.gca()
            # ax为两条坐标轴的实例
            ax.xaxis.set_major_locator(x_major_locator)
            # 把x轴的主刻度设置为1的倍数
            ax.yaxis.set_major_locator(y_major_locator)
            # 设置坐标轴刻度显示精度
            ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
            # 控制坐标轴显示范围
            plt.xlim(np.min(x), np.max(x))
            plt.ylim(min(np.min(self.yData), np.min(y))-0.05, max(np.max(self.yData), np.max(y))+0.05)
            plt.xticks(fontproperties='DejaVu Sans')
            plt.yticks(fontproperties='DejaVu Sans')
            # 设置坐标轴/标题
            # sig = r"E(t)=\frac{" + "{:.4f}".format(coef[0]) + r"}{1+e^{-" + "{:.4f}".format(coef[2]) + r"[t-" + "({:.4f})".format(coef[1]) + r"]}}+" + "({:.4f})".format(coef[3])
            sig = r"$E(t)=\frac{%.4f}{1+e^{-%.4f(t-%.4f)}}+%.4f$"%(coef[0], coef[2], coef[1], coef[3])
            # plt.title(sig, size=20)
            plt.suptitle('空调系统能耗特征函数Sigmoid方程拟合曲线\n'+sig, size=20, y=1, fontproperties=SongTiFont)
            plt.xlabel(u'日均室外温度(℃)', size=14, fontproperties=SongTiFont)
            plt.ylabel(r'日空调系统能耗强度(kWh/(m^2·d))', size=14, fontproperties=SongTiFont)
            plt.legend(prop={'family': 'DejaVu Sans', 'size': 10, 'weight': 'normal'}, loc='best')
            plt.savefig(os.path.join(self.figPath, self.caseId+"_sigmoid_fit.png"))
            # plt.show()
            return y30, e1_e0

        def draw_divide_zone(y30, e1_e0):
            y30 = y30.tolist()[0]
            # 基本画幅大小x:[0~0.5],y:[0~0.5]
            sns.set_style("ticks")
            # 设置画布大小
            plt.figure(figsize=(8, 6))
            # 控制上下左右尽量包含所有的散点，同时留出一定的边距
            x1 = np.linspace(0, np.max(0.5, e1_e0.astype('int'))+0.05, 10)
            y1 = x1
            # 画基本的分区
            plt.plot(x1, y1, c='black', linestyle='-')
            x2 = np.linspace(0.15, np.max(0.5, e1_e0.astype('int'))+0.05, 10)
            y2 = np.array([0.15, ]*x2.shape[0])
            plt.plot(x2, y2, c='black', linestyle='-')
            x3 = np.linspace(0.25, np.max(0.5, e1_e0.astype('int'))+0.05, 10)
            y3 = np.array([0.25, ] * x3.shape[0])
            plt.plot(x3, y3, c='black', linestyle='-')
            y4 = np.linspace(0.15, 0.25, 10)
            x4 = np.array([0.25, ] * y4.shape[0])
            plt.plot(x4, y4, c='black', linestyle='-')
            y5 = np.linspace(0.25, 0.35, 10)
            x5 = np.array([0.35, ] * y4.shape[0])
            plt.plot(x5, y5, c='black', linestyle='-')
            plt.text(0.03, 0.005, 'A', c='red', size=12, fontproperties=SongTiFont)
            plt.text(0.18, 0.155, 'B', c='red', size=12, fontproperties=SongTiFont)
            plt.text(0.255, 0.155, 'C', c='red', size=12, fontproperties=SongTiFont)
            plt.text(0.28, 0.255, 'D', c='red', size=12, fontproperties=SongTiFont)
            plt.text(0.355, 0.255, 'E', c='red', size=12, fontproperties=SongTiFont)
            plt.scatter(e1_e0, y30, marker='o', c='r', edgecolors='black', label=u'特征区间点')
            # 加上标志线
            plt.plot(np.array([e1_e0, ]*5), np.linspace(0, y30, 5), c='r', linestyle='--')
            plt.plot(np.linspace(0, e1_e0, 5), np.array([y30, ] * 5), c='r', linestyle='--')
            # 控制坐标轴范围
            x_major_locator = MultipleLocator(0.1)
            # 把x轴的刻度间隔设置为1，并存在变量里
            y_major_locator = MultipleLocator(0.1)
            # 把y轴的刻度间隔设置为10，并存在变量里
            ax = plt.gca()
            # ax为两条坐标轴的实例
            ax.xaxis.set_major_locator(x_major_locator)
            # 把x轴的主刻度设置为1的倍数
            ax.yaxis.set_major_locator(y_major_locator)
            # 设置坐标轴刻度显示精度
            ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
            # 控制坐标轴显示范围
            plt.xlim(np.min(x1), np.max(x1))
            plt.ylim(np.min(y1), np.max(y1))
            plt.xticks(fontproperties='DejaVu Sans')
            plt.yticks(fontproperties='DejaVu Sans')
            plt.tick_params(direction="in")
            # 设置坐标轴/标题
            plt.title(u'空调系统能耗特征评价区间拟合结果', size=20, fontproperties=SongTiFont)
            plt.xlabel(u'E1+E0(kWh/m^2)', size=15, fontproperties=SongTiFont)
            plt.ylabel(r'E(T=30℃)(kWh/m^2)', size=15, fontproperties=SongTiFont)
            plt.legend(prop={'family': 'SimHei', 'size': 12, 'weight': 'normal'}, loc='best')
            plt.savefig(os.path.join(self.figPath, self.caseId+"_divide_zone.png"))
            # plt.show()

        x, y = self.xData, self.yData
        self.fix()
        # from pdb import set_trace as st
        # st()
        print("has been fixed: {}".format((len(x)==len(self.xData)) == False))
        p0 = [max(self.yData), np.median(self.xData), 1, min(self.yData)]  # this is an mandatory initial guess
        popt, pcov = curve_fit(sigmoid, self.xData, self.yData, p0, method='dogbox', maxfev=500000)
        # 拟合参数，左到右依次对应L,x0,k,b
        # print(popt)
        y30, e1_e0 = draw_fit_curve(popt)
        level = getAssessLevel(y30, e1_e0)
        draw_divide_zone(y30, e1_e0)
        # 返回图片名
        return [os.path.join(self.figPath, self.caseId+"_sigmoid_fit.png"),
                os.path.join(self.figPath, self.caseId+"_divide_zone.png")], float(y30), (float(popt[0]), float(popt[3]), float(popt[2]), float(popt[1])), level, "long"

    def fit_short_term_data(self):
        print("\nSHORT\n")
        # 当数据量小于60时仅画散点图
        sns.set_style('whitegrid')
        borderX = np.array([22, 29, 33, 33, 29, 22, 22])
        borderY = np.array([0.33, 0.61, 0.64, 0.42, 0.38, 0.22, 0.33])
        plt.figure(figsize=(8, 6))
        # 控制上下左右尽量包含所有的散点，同时留出一定的边距
        x = np.linspace(np.min(self.xData), np.max(self.xData), 100)
        # 控制坐标轴显示范围
        plt.xlim(min(22, np.min(x))-1, max(np.max(x), 33)+1)
        plt.ylim(min(np.min(self.yData), 0), max(np.max(self.yData), 1))
        plt.scatter(self.xData, self.yData, marker='o', c='r', label=u'RawData')
        plt.plot(borderX, borderY, c='black', linestyle='--')
        plt.xticks(fontproperties='DejaVu Sans')
        plt.yticks(fontproperties='DejaVu Sans')
        plt.tick_params(direction="in")
        # 控制坐标轴刻度线
        x_major_locator = MultipleLocator(1)
        # 把x轴的刻度间隔设置为1，并存在变量里
        y_major_locator = MultipleLocator(0.2)
        # 把y轴的刻度间隔设置为10，并存在变量里
        ax = plt.gca()
        # ax为两条坐标轴的实例
        ax.xaxis.set_major_locator(x_major_locator)
        # 把x轴的主刻度设置为1的倍数
        ax.yaxis.set_major_locator(y_major_locator)
        # 设置坐标轴刻度显示精度
        ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
        # 设置坐标轴/标题
        plt.title(u'空调系统能耗评价指标', size=16, fontproperties=SongTiFont)
        plt.xlabel(u'供冷季日均温度(℃)', size=15, fontproperties=SongTiFont)
        plt.ylabel(r'日空调系统能耗强度(kWh/m^2·d)', size=15, fontproperties=SongTiFont)
        plt.legend(prop={'family': 'DejaVu Sans', 'size': 12, 'weight': 'normal'}, loc='best')
        plt.savefig(os.path.join(self.figPath, self.caseId+"_scatter.png"))
        # plt.show()
        return [os.path.join(self.figPath, self.caseId+"_scatter.png"), ], 0, 0, 0, "short"


    @staticmethod
    def readFromJSON(file):
        data = pd.read_json(file)
        # print(data)
        dj = dict()
        if data.shape[1] == 2:
            dj['temperature'] = data['temperature'].tolist()
            dj['energy_consume'] = data['energy_consume'].tolist()
        else:
            dj['temperature'] = data['temperature'].tolist()
            dj['energy_consume'] = data['energy_consume'].tolist()
            dj['fix_consume'] = data['fix_consume'].tolist()
        return dj, True if data.shape[1] == 3 else False, 0 if data.shape[0] < 60 else 1

    @staticmethod
    def generateReportOfDataCase(caseInfo, filePath, picPath):
        coldSource = caseInfo['coldSource']
        caseId = caseInfo['caseId']
        jsonPath = os.path.join(filePath, caseId+".json")
        data, _, dt = LineFit.readFromJSON(jsonPath)
        lf = LineFit(jsonData={'records': data}, coldSource=coldSource, figPath=picPath, caseId=caseId)
        if dt == 0:
            pics, y30, e1_e0, level, flag = lf.fit_short_term_data()
        else:
            pics, y30, e1_e0, level, flag = lf.fit_long_term_data()
        return pics, y30, e1_e0, level, flag


if __name__ == '__main__':
    print(generateUUID())
    # data, _, _ = LineFit.readFromJSON('./dataJson/uDkkIYF1.json')
    # lf = LineFit(jsonData={'records': data}, coldSource="风冷冷水机组", figPath='./curveFitPics', caseId='IepcJj0x')
    # lf.fit_short_term_data()
    caseInfo = {'caseId': 'uDkkIYF1', 'coldSource': "风冷冷水机组"}
    LineFit.generateReportOfDataCase(caseInfo, './dataJson', './curveFitPics')