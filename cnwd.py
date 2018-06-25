from __future__ import division
import os
import sys
import re
import getopt
import math

def usage():
	print('gnwd.py Input Output [options]\n\
		options:\n\
		 -c CountThresholdPercent,(0,1),default=0.5\n\
		 -C CountThreshold\n\
		 -b BindThresholdPercent,(0,1),default=0.5\n\
		 -B BindThreshold\n\
		 -e EntropyThresholdPercent,(0,1),default=0.5\n\
		 -E EntropyThreshold\n\
		 -d whether output debug file,default=False')
		 
def threshold_cal(lst, thres_percent):
	lst = sorted(lst)
	length = len(lst)
	return lst[math.floor(length * thres_percent)]
	
def candi_word_gen(sen, sen_len, nword):
	lst = []
	i = nword
	while(i < sen_len + 1):
		lst.append(sen[i-nword:i])
		i += 1
	return lst
	
def update_count_dict(dict, sen, nword):
	sen_len = len(sen)
	lst = candi_word_gen(sen, sen_len, nword)
	word_set = set(lst)
	for word in word_set:
		count = lst.count(word)
		if word in dict.keys():
			pre_count = dict[word]
			dict[word] = pre_count + count
		else:
			dict[word] = count	
			
def bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM):
	return (TOTAL_WORD_NUM * count) / (count_part1 * count_part2)
	
def update_w2_bind_dict(dict_w1, dict_w2, TOTAL_WORD_NUM):
	for word, count in dict_w2.items():
		count_part1 = dict_w1[word[0]]
		count_part2 = dict_w1[word[1]]
		bind = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		dict_w2[word] = [count, bind]
		
def update_w3_bind_dict(dict_w1, dict_w2, dict_w3, TOTAL_WORD_NUM):
	for word, count in dict_w3.items():
		count_part1 = dict_w1[word[0]]
		count_part2 = dict_w2[word[1:]][0]
		bind1 = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		count_part1 = dict_w1[word[-1]]
		count_part2 = dict_w2[word[0:-1]][0]
		bind2 = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		bind = min([bind1, bind2])
		dict_w3[word] = [count, bind]

def update_w4_bind_dict(dict_w1, dict_w2, dict_w3, dict_w4, TOTAL_WORD_NUM):
	for word, count in dict_w4.items():
		count_part1 = dict_w1[word[0]]
		count_part2 = dict_w3[word[1:]][0]
		bind1 = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		count_part1 = dict_w2[word[0:2]][0]
		count_part2 = dict_w2[word[2:]][0]
		bind2 = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		count_part1 = dict_w3[word[0:3]][0]
		count_part2 = dict_w1[word[-1]]
		bind3 = bind_cal(count, count_part1, count_part2, TOTAL_WORD_NUM)
		bind = min([bind1, bind2, bind3])
		dict_w4[word] = [count, bind]

		
def ent_cal(lst):
	count_total = sum(lst)
	ent = 0
	for count in lst:
		prob = count / count_total
		ent = ent - prob * math.log(prob, 2)
	return ent	

def update_ent_dict(dict1, dict2, nword):
	words_lst = sorted(dict2.keys())
	words_num = len(words_lst)
	LstForCalEnt=[]
	words_lst.append('*' * nword)
	for i in range(1, words_num + 1):
		if words_lst[i][:-1] == words_lst[i-1][:-1]:
			if type(dict2[words_lst[i-1]]) == list:
				LstForCalEnt.append(dict2[words_lst[i-1]][0])
			else:
				LstForCalEnt.append(dict2[words_lst[i-1]])
		else:
			if type(dict2[words_lst[i-1]]) == list:
				LstForCalEnt.append(dict2[words_lst[i-1]][0])
			else:
				LstForCalEnt.append(dict2[words_lst[i-1]])
			ent = ent_cal(LstForCalEnt)
			info = dict1[words_lst[i-1][:-1]]
			info.append(ent)
			dict1[words_lst[i-1][:-1]] = info
			LstForCalEnt = []

	words_lst.pop()
	for i in range(words_num):
		words_lst[i] = words_lst[i][::-1]
	words_lst = sorted(words_lst)
	
	words_lst.append('*' * nword)
	LstForCalEnt=[]
	for i in range(1, words_num + 1):
		if words_lst[i][:-1] == words_lst[i-1][:-1]:
			if type(dict2[words_lst[i-1][::-1]]) == list:
				LstForCalEnt.append(dict2[words_lst[i-1][::-1]][0])
			else:
				LstForCalEnt.append(dict2[words_lst[i-1][::-1]])
		else:
			if type(dict2[words_lst[i-1][::-1]]) == list:
				LstForCalEnt.append(dict2[words_lst[i-1][::-1]][0])
			else:
				LstForCalEnt.append(dict2[words_lst[i-1][::-1]])
			ent = ent_cal(LstForCalEnt)
			info = dict1[words_lst[i-1][:-1][::-1]]
			if len(info) == 2:
				info.append(ent)
				dict1[words_lst[i-1][:-1][::-1]] = info
			else:
				if info[2] > ent:
					info[2] = ent
					dict1[words_lst[i-1][:-1][::-1]] = info
			LstForCalEnt = []
	
	for word, info in dict1.items():
		if len(info) < 3:
			info.append(0)
			dict1[word] = info

def new_words_output(count_threshold_per, count_threshold,
					 bind_threshold_per, bind_threshold,
					 ent_threshold_per, ent_threshold,
					 dict, nword, output, debug):
	count_lst = []
	bind_lst = []
	ent_lst = []
	for word, info in dict.items():
		count_lst.append(info[0])
		bind_lst.append(info[1])
		ent_lst.append(info[2])
	count_lst = sorted(count_lst)
	bind_lst = sorted(bind_lst)
	ent_lst = sorted(ent_lst)
	
	if count_threshold != '':
		count_threshold = count_threshold
	elif count_threshold_per:
		count_threshold = threshold_cal(count_lst, count_threshold_per)
	
	if bind_threshold != '':
		bind_threshold = bind_threshold
	elif bind_threshold_per:
		bind_threshold = threshold_cal(bind_lst, bind_threshold_per)
		
	if ent_threshold != '':
		ent_threshold = ent_threshold
	elif ent_threshold_per:
		ent_threshold = threshold_cal(ent_lst, ent_threshold_per)
	
	fout = open(output + '_' + nword, 'w', encoding='utf8')
	if debug:
		fdebug = open(output + '_' + nword + '_debug', 'w', encoding='utf8')
	for word, info in dict.items():
		if debug:
			fdebug.write(word + '          ' + str(info[0])
							+'          ' + str(float('%.1f' %info[1]))
							+'          ' + str(float('%.3f' %info[2]))+'\n')
		if info[0] > count_threshold and info[1] > bind_threshold and info[2] > ent_threshold:
			fout.write(word + '\n')
	fout.close()
	if debug:
		fdebug.close()
		
def main(argc, argv):
	if argc < 3:
		usage()
		exit()
	file_in = argv[1]
	file_out = argv[2]
	opts, args = getopt.getopt(sys.argv[3:],"hdc:C:b:B:e:E:")
	count_threshold_per = 0.5
	count_threshold = ''
	bind_threshold_per = 0.5
	bind_threshold = ''
	ent_threshold_per = 0.5
	ent_threshold = ''
	debug = False
	for opt, value in opts:
		if opt == '-c':
			count_threshold_per = float(value)
		elif opt == '-C':
			count_threshold = float(value)
		elif opt == '-b':
			bind_threshold_per = float(value)	
		elif opt == '-B':
			bind_threshold = float(value)
		elif opt == '-e':
			ent_threshold_per = float(value)
		elif opt == '-E':
			ent_threshold = float(value)
		elif opt == '-d':
			debug = True
		elif opt == '-h':
			usage()
			exit()	
	dict_w1={}
	dict_w2={}
	dict_w3={}
	dict_w4={}
	dict_w5={}
	TOTAL_WORD_NUM = 0
	with open(file_in, 'r', encoding='utf8') as fin:
		for sen in fin.readlines():
			sen = sen.strip()
			if not sen:
				continue
			sub_sen_lst = re.split(r"\W", sen)
			for sub_sen in sub_sen_lst:
				sub_sen_len = len(sub_sen)
				TOTAL_WORD_NUM = TOTAL_WORD_NUM + sub_sen_len
				if sub_sen_len >= 1:
					update_count_dict(dict_w1, sub_sen, 1)  
					if sub_sen_len >= 2:
						update_count_dict(dict_w2, sub_sen, 2)  
						if sub_sen_len >= 3:
							update_count_dict(dict_w3, sub_sen, 3)  
							if sub_sen_len >= 4:
								update_count_dict(dict_w4, sub_sen, 4)  
								if sub_sen_len >= 5:
									update_count_dict(dict_w5, sub_sen, 5)
								else:
									continue
							else:
								continue
						else:
							continue
					else:
						continue
				else:
					continue				
			
	if not dict_w1 or not dict_w2 or not dict_w3 or not dict_w4 or not dict_w5:
		print('warning:  too short txt or lines are too short, no new words output')
		exit()
	
	update_w2_bind_dict(dict_w1, dict_w2, TOTAL_WORD_NUM)
	update_w3_bind_dict(dict_w1, dict_w2, dict_w3, TOTAL_WORD_NUM)
	update_w4_bind_dict(dict_w1, dict_w2, dict_w3, dict_w4, TOTAL_WORD_NUM)
	
	update_ent_dict(dict_w2, dict_w3, 3)
	update_ent_dict(dict_w3, dict_w4, 4)
	update_ent_dict(dict_w4, dict_w5, 5)
	
	new_words_output(count_threshold_per, count_threshold,
					 bind_threshold_per, bind_threshold,
					 ent_threshold_per, ent_threshold,
					 dict_w2, 'word2', file_out, debug)
	new_words_output(count_threshold_per, count_threshold,
					 bind_threshold_per, bind_threshold,
					 ent_threshold_per, ent_threshold,
					 dict_w3, 'word3', file_out, debug)
	new_words_output(count_threshold_per, count_threshold,
					 bind_threshold_per, bind_threshold,
					 ent_threshold_per, ent_threshold,
					 dict_w4, 'word4', file_out, debug)
					 
if __name__=='__main__':
	main(len(sys.argv),sys.argv)	