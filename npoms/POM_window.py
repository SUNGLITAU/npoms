from POM import Ui_MainWindow
from TopicSpider import spider, get_topic_id
from SearchTerm import SearchTerm
from OtherTools import clear_all_var
from DataProcessing import analysis
from GetAbstract import get_abs
from ReportForms import html_report
from EmailTool import mail_report

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QPushButton, QMessageBox)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
from threading import Timer
from dateutil.parser import parse
import sys
import datetime
import random
import schedule
import time
import os


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        return


class PomWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, **kwargs):
        super(PomWindow, self).__init__()
        self.setupUi(self)
        self.key_words_le.setPlaceholderText('请在这里输入关键字')
        self.start_time_le.setPlaceholderText('开始时间')
        self.start_time_le.setValidator(QtGui.QIntValidator())  # 限制输入数字
        self.start_time_le.setMaxLength(8)
        self.end_time_le.setPlaceholderText('结束时间')
        self.end_time_le.setValidator(QtGui.QIntValidator())  # 限制输入数字
        self.end_time_le.setMaxLength(8)
        self.class_num.setPlaceholderText('簇')
        self.class_num.setValidator(QtGui.QIntValidator())

        # 事件
        self.query_btn.clicked.connect(lambda: self.query_btn_click())  # TODO 为什么要定义lambda需要进一步学习
        self.analysis_btn.clicked.connect(lambda: self.real_time_mode())
        self.checkBox.clicked.connect(lambda: self.check_check_btn())
        # self.zhihu_img.mouseDoubleClickEvent()
        # sys.stdout = EmittingStream(textWritten=self.update_info)  # TODO 需要进一步学习

    def hello(self):
        self.info.setText('Hello World\n程序静默运行中...')

    def closeEvent(self, event):
        self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子灰.png'))
        reply = QMessageBox.question(self, '请确认：',
                                     "退出系统嘛？", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子蓝.png'))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def blank_check(self):
        key_words = self.key_words_le.text()
        if key_words == '':
            self.warning_message('分析的关键字是必要的，请输入')
            return 0, 0, 0, 0
        print("关键字检查完成，开始确认是否有缺省值和检查数据，请稍候...")
        start_time = self.start_time_le.text()
        end_time = self.end_time_le.text()
        k = self.class_num.text()  # 注意生成的是str类型，需要转换类型

        # 缺省值处理
        if start_time == '':
            print('处理起始时间的缺省值')
            start_time = '20101201'  # 知乎网站2010年12月开放
        if end_time == '':
            print('结束时间的缺省值为今天')
            end_time = datetime.datetime.now().strftime('%Y%m%d')
        if k == '' or int(k) == 1:
            k = random.randint(3, 5)  # 缺省情况下，KMeans3-5类为理论拐点

        if int(start_time) > int(end_time):
            self.warning_message("开始日期不能大于结束日期")
            self.start_time_le.clear()
            self.end_time_le.clear()
            return 1, 1, 1, 1
        print('数据检查完成，开始传入参数开始分析，请稍候.....')
        return key_words, start_time, end_time, k

    def query_btn_click(self):
        key_words, start_time, end_time, k = self.blank_check()
        # key_words = self.key_words_le.text()
        if key_words == 0 and start_time == 0 and end_time == 0 and k == 0:
            QMessageBox.about(self, '无法查询', '请输入关键字，关键字是必须的')
            return
        elif key_words == 1 and start_time == 1 and end_time == 1 and k == 1:
            QMessageBox.about(self, '无法查询', '麻烦正确输入日期')
            return
        else:
            pass
        sys.stdout = EmittingStream(textWritten=self.update_info)
        print("开始查询，请稍候")
        self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控黑500.png);")
        self.setWindowIcon(QIcon('./data/tmp4design/网络舆情黑.png'))

        search = SearchTerm(key_words)
        # search.topic_id, note = get_topic_id(search.keywords, search.header)
        # IP出现问题时的临时解决办法：单机指定：测试模式
        # 19570564 武汉ID 19639859 境外ID 19575118 奋斗ID 19622792 痛苦ID
        search.topic_id = "19622792"
        note = 'IP或网站出现问题，临时解决措施：测试模式'
        print(search.keywords, search.topic_id, note)

        try:
            # spider(search.keywords, search.topic_id, search.header)
            print('=== 测试模式，所有数据已经存储到MySQL中 ===')
            self.update_info(' {} 的文章和回答已经存入数据库中，对应的ID为 {} \n 相关的数据已经存入MySQL'.format(key_words, search.topic_id))

            reply = QMessageBox.question(self, '你的想法', '是否要生成文摘呢？(如果要进行情感分析，需要文摘', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                print('开始生成摘要')
                get_abs(start_time, end_time, search.topic_id)
                os.startfile(now_path + '/data/textrank/topic{}_{}-{}abstract.csv'.format(search.topic_id, start_time, end_time))  # 弹出工作表
            else:
                pass
            print('查询阶段的工作已经完成')
        except Exception:
            print("请相关话题及内容较少，无需使用舆情分析系统，推荐自行了解")

        time.sleep(1)
        self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控蓝500.png);")
        self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子蓝.png'))
        return

    def analysis_btn_click(self):

        key_words, start_time, end_time, k = self.blank_check()
        if key_words == 0 and start_time == 0 and end_time == 0 and k == 0:
            QMessageBox.about(self, '无法查询', '请输入关键字，关键字是必须的')
            return
        elif key_words == 1 and start_time == 1 and end_time == 1 and k == 1:
            QMessageBox.about(self, '无法查询', '麻烦正确输入日期')
            return
        else:
            pass
        self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控红500.png);")
        self.setWindowIcon(QIcon('./data/tmp4design/网络舆情红.png'))
        sys.stdout = EmittingStream(textWritten=self.update_info)
        search = SearchTerm(key_words)
        # search.topic_id, note = get_topic_id(search.keywords, search.header)
        # IP出现问题时的临时解决办法：单机指定：测试模式
        # 19570564 武汉ID 19639859 境外ID 19575118 奋斗ID 19622792 痛苦ID
        search.topic_id = "19622792"
        note = 'IP或网站出现问题，临时解决措施：测试模式'
        print(search.keywords, search.topic_id, note)

        try:

            print('================== 数据分析：开始 ====================')

            cqc = analysis(start_time, end_time, search.topic_id, int(k))
            if cqc == 0:
                self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控蓝500.png);")
                self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子蓝.png'))
                return
            print('================== 聚类完成，图片生成 ====================')
            time.sleep(3)


            try:
                html_report(start_time, end_time, search.topic_id)
            except Exception:
                print('================== 没有生成文摘，优先生成文摘 ====================')
                time.sleep(5)
                get_abs(start_time, end_time, search.topic_id)
            finally:
                html_report(start_time, end_time, search.topic_id)
            print('================== 已经弹出了HTML报告 ====================')
            time.sleep(3)

            reply = QMessageBox.question(self, '来自邮件系统：',
                                         "需要讲HTML发送到邮箱作为历史保存嘛？（建议发送）\n如要发送，请关闭相关文件", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                try:
                    mail_report(start_time, end_time, search.topic_id)
                    print('================== 已发送相关文件 ====================')
                except Exception:
                    print('发送失败，请检查')
            else:
                pass
            self.update_info(' {} : {} 分析完成 请检查\n相关文件存放在data下面，如有需要请自行查看'.format(key_words, search.topic_id))

        except Exception:
            self.warning_message('有错误发生，请检查！\n建议增加单词分析的数据量（增大时间跨度）')
            self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控蓝500.png);")
            self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子蓝.png'))
            return
        self.img_change0.setStyleSheet("image: url(./data/tmp4design/舆情监控蓝500.png);")
        self.setWindowIcon(QIcon('./data/tmp4design/负面舆情帽子蓝.png'))
        clear_all_var()
        return

    def mouseDoubleClickEvent(self, event):
        random_int = random.randint(1, 2)
        if random_int == 1:
            self.title_img.setStyleSheet("image: url(./data/tmp4design/与世界分享你的知识、经验和见解.png);")
        else:
            self.title_img.setStyleSheet("image: url(./data/tmp4design/话题精华分析.png);")
        return

    def update_info(self, message):
        # cursor = self.info.textCursor()
        # cursor.movePosition(QtGui.QTextCursor.End)
        # cursor.insertText(message)
        # self.info.setText(cursor)
        # self.info.ensureCursorVisible()

        self.info.append(message)  # 在指定的区域显示提示信息
        cursor = self.info.textCursor()
        self.info.moveCursor(cursor.End)  # 光标移到最后，这样就会自动显示出来
        QtWidgets.QApplication.processEvents()  # 一定加上这个功能，不然有卡顿
        return

    def warning_message(self, message):
        # 图标的变化
        # QMessageBox.setIcon('./data/tmp4design/网络舆情红.png')
        QMessageBox.about(self, '错误警告！', message)
        return

    def clear_all(self):
        # 清空错误的值
        self.key_words_le.clear()
        self.start_time_le.clear()
        self.end_time_le.clear()
        self.class_num.clear()
        return

    def check_check_btn(self):
        c = self.checkBox.isChecked()  # False True
        # print(c)
        # 实时模式下请不要填入结束时间，系统会从
        # 实时模式运行下可以使用esc终止循环，回到主界面
        # 尽可能重复利用代码
        if c is True:
            self.label.setText(' >> >> >> >> Real time mode ：Running << << << << ')
            # print(c, type(c))
            self.info.setText('实时模式：准备就绪\n为保证程序稳定性，建议只分析最近一个月的数据;'
                              ' 如果要分析的时间较长，建议单次分析\n此模式下自动交互静默，不会有界面提示')
        else:
            self.label.setText("Copyright © 2020 sunglitau, All things for study.")
            self.info.clear()
        return

    def real_time_mode(self):
        sys.stdout = EmittingStream(textWritten=self.hello)
        # schedule.every(7).day.at('08:00').do(self.analysis_btn_click())
        # schedule.every(5).minutes.do(self.analysis_btn_click())
        key_words, start_time, end_time, k = self.blank_check()
        if key_words == 0 and start_time == 0 and end_time == 0 and k == 0:
            QMessageBox.about(self, '无法查询', '请输入关键字，关键字是必须的')
            return
        elif key_words == 1 and start_time == 1 and end_time == 1 and k == 1:
            QMessageBox.about(self, '无法查询', '麻烦正确输入日期')
            return
        else:
            pass
        # print('实施模式下，为保证程序稳定性，只分析最近一个月的数据')
        end_time = datetime.datetime.now().strftime('%Y%m%d')
        if int(start_time) > int(end_time):
            self.info.setText('本系统不支持查询未来')
            return

        search = SearchTerm(key_words)
        # search.topic_id, note = get_topic_id(search.keywords, search.header)
        # IP出现问题时的临时解决办法：单机指定：测试模式
        # 19570564 武汉ID 19639859 境外ID 19622792 痛苦ID 19564412 恋爱ID
        search.topic_id = "19564412"
        note = 'IP或网站出现问题，临时解决措施：测试模式'
        print(search.keywords, search.topic_id, note)
        if self.checkBox.isChecked():
            # print('实时模式：准备就绪\n为保证程序稳定性，建议只分析最近一个月的数据')
            try:

                global t  # 准确的时间
                t = Timer(1200, self.real_time_mode)  # 5min # 推荐是按天算的，所以没有判断文件存在的选项，必定不一样
                t.start()
                # 测试模式：数据暂时无法获取
                print("测试模式：使用本地数据，跳过数据获取")
                # spider(search.keywords, search.topic_id, search.header)
                time.sleep(5)
                get_abs(start_time, end_time, search.topic_id)
                time.sleep(5)
                analysis(start_time, end_time, search.topic_id, k)
                time.sleep(5)
                html_report(start_time, end_time, search.topic_id)
                time.sleep(5)
                mail_report(start_time, end_time, search.topic_id)
                time.sleep(5)

                # self.query_btn_click()  # 自动查询  TODO 注意这里是默认执行程序，需要更改
                # self.analysis_btn_click()  # 自动分析
                clear_all_var()

            except Exception:
                print('本轮出现了一个错误，跳过\n请检查日期内数据是否存在')
                # 看需不需要发送错误报告

            finally:
                # global t  # 模糊的时间
                # t = Timer(300, self.real_time_mode)  # 5min # 推荐是按天算的，所以没有判断文件存在的选项，必定不一样
                # t.start()
                pass

        else:
            self.analysis_btn_click()
        return


if __name__ == '__main__':
    now_path = os.getcwd()
    path = now_path.replace('\\', '/')
    # print(sys.getrecursionlimit())
    # sys.setrecursionlimit(2000)
    # print(sys.getrecursionlimit())
    app = QtWidgets.QApplication(sys.argv)
    window = PomWindow()
    window.show()
    # window.hello()  # info 显示出了hello world
    sys.exit(app.exec_())

