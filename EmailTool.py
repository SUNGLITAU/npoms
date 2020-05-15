# -*- coding: utf8  -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from TopicSpider import check_time
from OtherTools import clear_all_var
import time
import smtplib
import os


def mail_report(a, b, topic_id):
    # 路径
    now_path = os.getcwd()
    path = now_path.replace('\\', '/')

    x_code = "your code"
    img1_path = path + "/data/wordcloud/wc_tf_idf_topic{}.png".format(topic_id)
    img2_path = path + "/data/wordcloud/wc_k_means_topic{}_result.png".format(topic_id)
    csv_file = path + '/data/textrank/topic{}_{}-{}abstract.csv'.format(topic_id, a, b)
    html_file = path + '/data/reportforms/report_topic{}_{}-{}.html'.format(topic_id, a, b)

    content = MIMEMultipart()

    image1 = MIMEImage(open(img1_path, 'rb').read(), _subtype='octet-stream')
    image1.add_header('Content-Disposition', 'attachment', filename=img1_path)
    content.attach(image1)
    image2 = MIMEImage(open(img2_path, 'rb').read(), _subtype='octet-stream')
    image2.add_header('Content-Disposition', 'attachment', filename=img2_path)
    content.attach(image2)
    csv1 = MIMEApplication(open(csv_file, 'rb').read())
    csv1.add_header('Content-Disposition', 'attachment', filename=csv_file)
    content.attach(csv1)
    html1 = MIMEApplication(open(html_file, 'rb').read())
    html1.add_header('Content-Disposition', 'attachment', filename=html_file)
    content.attach(html1)

    with open(img1_path, 'rb') as im1:
        msg_image1 = MIMEImage(im1.read())
        msg_image1.add_header('Content-ID', '<image1>')
        content.attach(msg_image1)
    with open(img2_path, 'rb') as im2:
        msg_image2 = MIMEImage(im2.read())
        msg_image2.add_header('Content-ID', '<image2>')
        content.attach(msg_image2)

    msg = '''
    <h1>舆情分析简报：</h1>
    <h2 style="color:red">This is a tf-idf：</h1>
    <p><img src="cid:image1" width=75% /></p>
    <h2 style="color:blue">This is a k-means：</h1>
    <p><img src="cid:image2" width=75% /></p>
    <p>如果想看详细报告，请手动下载附件4：HTML网页报告</p>
    '''

    message = MIMEText(msg, 'html', 'utf-8')
    content.attach(message)

    content['Subject'] = '舆情监控系统 汇报 20分钟定时 模式 {}'.format(check_time(time.time()))
    content['To'] = 'to where@mail.com'
    content['From'] = "from where@mail.com"

    server = smtplib.SMTP_SSL("smtp.qq.com", port=465)
    try:
        server.login("from where@mail.com", x_code)
        print('login success!!!')
        server.sendmail("from where@mail.com", 'to where@mail.com', content.as_string())
        print('Send Successful!')
    except Exception:
        print('邮箱出现了一点异常，数据保存在文件夹下data文件中的reporforms中\n文件名为:report_topic{}_{}-{}.html'.format(topic_id, a, b))
    finally:
        clear_all_var()
        return


if __name__ == '__main__':

    # 希望其他模块直接传一块html过来，然后这边再补充
    # 需要显示的项包裹 查询的关键字（id自带）
    mail_report('20191201', '20200418', '19622792')


