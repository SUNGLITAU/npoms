Network Public Opinion Monitoring System  
The abbreviation is npoms  


写在前面：  
因为之前没有接触过这方面的东西，所以虽然做出来，但是自我评价其实是比较菜的。  
完成这个毕设参考了很多大佬的代码，向看过的所有文章的作者表示感谢~ 
另一方面，在完成毕设的途中导师因为工作调度离开了，**导致整个项目是由自己一个人摸索出来的，因此这个项目还存在许多缺陷，如果有同学想学习，建议只需参考下大概的思路，没有必要深究**，因为真的写的不好我也怕误导人。

整体逻辑：  
![Image text](https://i0.hdslb.com/bfs/album/11456ac71e5b39ec9f81eb3e8494bb04d94f2870.png@518w_1e_1c.png)
> 通过Python爬虫程序爬取知乎网站的精华文章和回答到MySQL中进行保存，在对得到的文本进行数据清洗之后，沿着两条分析可视化处理过程：一是抽取文本特征值并向量化，使用K-Means聚类算法进行中文文本聚类，通过WordCloud展示出用户指定关键词相关的词语；二是通过TR抽取文本摘要，并在此基础上对文本摘要进行情感分析，利用pycharts可视化统计结果。最终和词云图片组装生成舆情报告的HTML文件，并将上述过程中所有得到的结果通过邮件发送到用户的邮箱作为查询历史数据保存。  

具体效果展示：https://www.bilibili.com/video/BV1Te411W7DQ  

如果你对这个项目还有兴趣，可以看看位于ProcessON上的流程图：  
在界面点击按钮后的触发流程：  
https://www.processon.com/view/link/5e9beb665653bb1a686ed8cf  
整体的大致逻辑：  
https://www.processon.com/view/link/59410eeae4b0848d3ecfa356  


虽然很早就了解到了GitHub，但是因为各种各样的原因一直没有用起来，希望这次能好好利用。  
如果对这个有什么意见或者建议，请联系：sunglitau@foxmail.com
