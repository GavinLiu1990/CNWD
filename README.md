#### 概述

1.本程序用于中文新词发现。不依赖于已有词典、词库，输入中文文本，即可发现中文新词，属非监督式学习。 <br>
2.本程序支持中文2字新词、3字新词和4字新词的发现。 <br>
3.需要python3及以上。 <br>

#### 算法参考

基于大规模语料的新词发现算法，顾森，《程序员》 <br>
不过，在顾森文章中提及的次数阈值、凝固度阈值、信息熵阈值是实数值，本程序支持基于统计的比值。 <br>
本程序，次数阈值、凝固度阈值、信息熵阈值参数设置分别为-c、-b、-e(统计比值)，-C、-B、-E(实数值)。 <br>

#### 使用

cnwd.py Input Output [options]

	options:
	 
	 -c CountThresholdPercent,(0,1),default=0.5
	 
	 -C CountThreshold
	 
	 -b BindThresholdPercent,(0,1),default=0.5
	 
	 -B BindThreshold
	 
	 -e EntropyThresholdPercent,(0,1),default=0.5
	 
	 -E EntropyThreshold
	 
	 -d whether output debug file,default=False
	 
>示例1  cnwd.py  TestData  newword <br>
>示例2  cnwd.py  TestData  newword  -c 0.9  -b 0.9  -e 0.9 <br>
>示例3  cnwd.py  TestData  newword  -C 3  -b 0.9  -E 0 <br>
	 
#### 建议

1.如果文件较大，如一部长篇小说，新词发现参数建议使用比值。如cnwd.py  TestData  newword  -c 0.9  -b 0.9  -e 0.9 <br>
2.如果文件较小，如一篇体育新闻，新词发现参数建议使用实数实数值。如cnwd.py  TestData  newword  -C 3  -B 2  -E 0 <br>
 