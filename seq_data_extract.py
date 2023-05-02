#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
import chardet
import random 
from stanfordcorenlp import StanfordCoreNLP
from nltk.stem import WordNetLemmatizer
import nltk
import javalang
import jieba

def normalize_word(sentence):
	lemmatizer = WordNetLemmatizer()
	tokens = nltk.word_tokenize(sentence)
	pos_tags = nltk.pos_tag(tokens)
	res = []
	for word, pos in pos_tags:
		if pos.startswith('J'):
			tmp = lemmatizer.lemmatize(word.lower(), 'a')
		elif pos.startswith('V'):
			tmp = lemmatizer.lemmatize(word.lower(), 'v')
		elif pos.startswith('N'):
			tmp = lemmatizer.lemmatize(word.lower(), 'n')
		elif pos.startswith('R'):
			tmp = lemmatizer.lemmatize(word.lower(), 'r')
		else:
			tmp = lemmatizer.lemmatize(word.lower())
		res.append(tmp)
	return ' '.join(res)

def get_ast(code):
	tokens=javalang.tokenizer.tokenize(code)
	parser=javalang.parse.Parser(tokens)
	ast=parser.parse_member_declaration()
	return ast

def get_code(path):
	code = ''
	l = 0
	with open(path,'r',encoding='UTF-8') as f:
		lines = f.readlines()
		for line in lines:
			if line[0:7] == 'package':
				continue
			if line[0:6] == 'import':
				continue
			if line[0:4] == 'from':
				continue
			code += line
			l += 1
	return code, l


def get_structure(ast):
	global code_structure
	ast_type = type(ast)
	if ast_type == javalang.tree.ClassDeclaration:
		code_structure += 'ClassDeclaration '
		if ast.body is not None:
			for t in ast.body:
				get_structure(t)
	elif ast_type == javalang.tree.MethodDeclaration:
		code_structure += 'MethodDeclaration '
		if ast.body is not None:
			for t in ast.body:
				get_structure(t)
	elif ast_type == javalang.tree.ConstructorDeclaration:
		code_structure += 'ConstructorDeclaration '
		if ast.body is not None:
			for t in ast.body:
				get_structure(t)
	elif ast_type == javalang.tree.InterfaceDeclaration:
		code_structure += 'InterfaceDeclaration '
		if ast.body is not None:
			for t in ast.body:
				get_structure(t)
	elif ast_type == javalang.tree.AnnotationDeclaration:
		code_structure += 'AnnotationDeclaration '
		if ast.body is not None:
			for t in ast.body:
				get_structure(t)
	elif ast_type == javalang.tree.SynchronizedStatement:
		code_structure += 'SynchronizedStatement '
		if ast.block is not None:
			for t in ast.block:
				get_structure(t)
	elif ast_type == javalang.tree.LocalVariableDeclaration:
		code_structure += 'LocalVariableDeclaration '
	elif ast_type == javalang.tree.ForStatement:
		code_structure += 'ForStatement '
		if ast.body is not None:
			get_structure(ast.body)
	elif ast_type == javalang.tree.BlockStatement:
		code_structure += 'BlockStatement '
		if ast.statements is not None:
			for t in ast.statements:
				get_structure(t)
	elif ast_type == javalang.tree.IfStatement:
		code_structure += 'IfStatement '
		if ast.then_statement is not None:
			get_structure(ast.then_statement)
		if ast.else_statement is not None:
			get_structure(ast.else_statement)
	elif ast_type == javalang.tree.TryStatement:
		code_structure += 'TryStatement '
		if ast.block is not None:
			for t in ast.block:
				get_structure(t)
	elif ast_type == javalang.tree.WhileStatement:
		code_structure += 'WhileStatement '
		if ast.body is not None:
			get_structure(ast.body)
	elif ast_type == javalang.tree.DoStatement:
		code_structure += 'DoStatement '
		if ast.body is not None:
			get_structure(ast.body)
	elif ast_type == javalang.tree.StatementExpression:
		code_structure += 'StatementExpression '
	elif ast_type == javalang.tree.ReturnStatement:
		code_structure += 'ReturnStatement '
	elif ast_type == javalang.tree.ConstantDeclaration:
		code_structure += 'ConstantDeclaration '
	elif ast_type == javalang.tree.FieldDeclaration:
		code_structure += 'FieldDeclaration '
	elif ast_type == javalang.tree.EnumDeclaration:
		code_structure += 'EnumDeclaration '
	elif ast_type == javalang.tree.ThrowStatement:
		code_structure += 'ThrowStatement '
	elif ast_type == javalang.tree.SwitchStatement:
		code_structure += 'SwitchStatement '
	elif ast_type == javalang.tree.AssertStatement:
		code_structure += 'AssertStatement '
	elif ast_type == javalang.tree.AnnotationMethod:
		code_structure += 'AnnotationMethod '
	else:
		# 处理特殊情况
		if ast_type != list and ast_type != javalang.tree.Statement:
			with open('./d2/other_statement.txt','w',encoding='UTF-8') as f:
				f.write(str(ast) + '\n')
				f.write(str(ast_type) + '\n')


def get_method(ast,at):
	global method_list
	ast_type = type(ast)
	if ast_type == javalang.tree.ClassDeclaration or ast_type == javalang.tree.InterfaceDeclaration:
		if ast.body is not None:
			for t in ast.body:
				get_method(t,at)
	else:
		method_list[at].append(ast)


def get_snippet(ast,at):
	global snippet_list
	ast_type = type(ast)
	split_type = [javalang.tree.ClassDeclaration,javalang.tree.MethodDeclaration,javalang.tree.ConstructorDeclaration,javalang.tree.InterfaceDeclaration]
	if ast_type in split_type:
		if ast.body is not None:
			for t in ast.body:
				get_snippet(t,at)
	else:
		snippet_list[at].append(ast)


def _get_diff(r,ty):
	# print(r)
	if ty == 0:
		global diff_list
		p = (0,0)
		for c in r[1:]:
			if c[0] - p[0] == 1 and c[1] - p[1] == 0:
				diff_list[0].append(p[0])
			elif c[0] - p[0] == 0 and c[1] - p[1] == 1:
				diff_list[1].append(p[1])
			# if c[0] - p[0] == 1:
			# 	if c[1] - p[1] == 1:
			# 		print(l1[p[0]])
			# 		print(type(l1[p[0]]))
			# 	else:
			# 		print('-'+str(l1[p[0]]))
			# else:
			# 	print('+'+str(l2[p[1]]))
			p = c
	if ty == 1:
		global code_structure, old_list, new_list
		code_structure = ''
		p = (0,0)
		for c in r[1:]:
			if c[0] - p[0] == 1:
				if c[1] - p[1] == 1:
					code_structure += (old_list[p[0]] + ' ')
				else:
					code_structure += '-' + old_list[p[0]] + ' '
			else:
				code_structure += '+' + new_list[p[1]] + ' '
			p = c


def get_diff(l1,l2,ty):
	n = len(l1)
	m = len(l2)

	v = [{0:[(0,0)]},{}]
	find = 0
	c1 = (0,0)
	while c1[0] < n and c1[1] < m and str(l1[c1[0]]) == str(l2[c1[1]]):
		c1 = (c1[0] + 1,c1[1] + 1)
		v[0][0].append(c1)
	if c1 == (n,m):
		_get_diff(v[0][0],ty)
		find = 1

	pre = 1
	cur = 0

	for d in range(1,n + m + 1):
		if find == 1:
			break
		pre = (pre + 1) % 2
		cur = (cur + 1) % 2
		v[cur].clear()
		# print(d)
		for k in range(d,-d - 1,-2): # k = x - y
			c = [(-1,-1)]
			t = k + 1
			if t < d:
				r = []
				for c2 in v[pre][t]:
					r.append(c2)
				c1 = (r[-1][0],r[-1][1] + 1)
				r.append(c1)
				while c1[0] < n and c1[1] < m and str(l1[c1[0]]) == str(l2[c1[1]]):
					# print(l1[c1[0]], l2[c1[1]])
					c1 = (c1[0] + 1,c1[1] + 1)
					r.append(c1)
				if c1 == (n,m):
					find = 1
					_get_diff(r,ty)
					break
				c = r
				# print(k,c)
			t = k - 1
			if t > -d:
				r = []
				for c2 in v[pre][t]:
					r.append(c2)
				c1 = (r[-1][0] + 1,r[-1][1])
				r.append(c1)
				while c1[0] < n and c1[1] < m and str(l1[c1[0]]) == str(l2[c1[1]]):
					c1 = (c1[0] + 1,c1[1] + 1)
					r.append(c1)
				if c1[0] > c[-1][0]:
					c = r
				if c1 == (n,m):
					find = 1
					_get_diff(r,ty)
					break
				# print(k,r)
			v[cur][k] = c
			# print(k,c)

# 清洁单词吧，大概是
def split_word(line):
	l = jieba.cut(line, cut_all=True)
	line = ' '.join(l)
	while '  ' in line:
		line = line.replace('  ',' ')
	return line




print("start")
nlp = StanfordCoreNLP(r'/data/liyz/CoreNLP/stanford-corenlp-full-2018-02-27')

print("----------One---------")
code_structure = ''
method_list = [[],[]]  
diff_list = [[],[]]  	
snippet_list = [[],[]]  

print("----------Two---------")
modes = ['train','test','eval']
order = ['sort','random']
granularity = ['class','method','snippet']


print("----------Three---------")
for m in modes:
	if os.path.isfile('./d2/' + m + '_story_sort.txt'):
		os.remove('./d2/' + m + '_story_sort.txt')
	if os.path.isfile('./d2/' + m + '_summ.txt'):
		os.remove('./d2/' + m + '_summ.txt')
	for g in granularity:
		if os.path.isfile('./d2/' + m + '_' + g + '_sort.txt'):
			os.remove('./d2/' + m + '_' + g + '_sort.txt')

# for m in modes:
# 	for o in order:
# 		if os.path.isfile('./d1/' + m + '_story_'+ o +'.txt'):
# 			os.remove('./d1/' + m + '_story_'+ o +'.txt')
# 		for g in granularity:
# 			if os.path.isfile('./d1/' + m + '_ast_' + g + '_' + o + '.txt'):
# 				os.remove('./d1/' + m + '_ast_' + g + '_' + o + '.txt')
# 	if os.path.isfile('./d1/' + m + '_summ.txt'):
# 		os.remove('./d1/' + m + '_summ.txt')

print("----------Four---------")
for file_num in range(10):
	
	path = "/data/zhouhj/data"+str(file_num)
	projects = os.listdir(path) 


	decode_list=["ISO-8859-1","utf-8",'gb18030', 'ISO-8859-2','gb2312',"gbk" ]
	

	e = 0
	t = 1
	num_commit = 0
	N = len(projects)
	print("----------Five---------")
	for i, project in enumerate(projects):
		# if i > 5:
		# 	break
		if num_commit > 3000:
			break
		project_path = path+'/'+project
		iterations = os.listdir(project_path)
		# print(project_path)
		# print("进度:{0}%".format(round((i + 1) * 100 / N)), end="\r")

		
		if len(iterations) < 100:
			continue
		################################
		print("----------Six---------")
		for j,iteration in enumerate(iterations):
			# if j > 30:
			# 	break
			if num_commit > 3000:
				break
			if (len(iteration.split('_')) > 1):
				continue
			coreclass_path = project_path+'/'+iteration				# 从 coreclass.txt变成模型预测
			
			if os.path.isfile(coreclass_path+'/'+'new_coreclass.txt'):
				with open(coreclass_path+'/'+'new_coreclass.txt','r',encoding='UTF-8') as f3:
					lines = f3.readlines()
					num_class = len(lines)
					if num_class < 1 or num_class > 1:
						continue
					file_names = {}
					for line in lines:
						line = line.strip('\n')
						file_name, p = line.split(':')
						file_names[file_name] = p
					file_names = sorted(file_names.items(), key=lambda item:item[1], reverse=True)
					file_name = file_names[0][0]
					if file_name == '':
						continue
			
			mode = ''
			if num_commit % 10 == 0:
				e = random.randint(0,9)
				t = random.randint(0,9)
				t = (t + (e == t)) % 10
			if num_commit % 10 == e:
				mode = 'eval_'
			elif num_commit % 10 == t:
				mode = 'test_'
			else:
				mode = 'train_'
			# print(coreclass_path)
			if os.path.isfile(coreclass_path+'/'+'diff_sort.txt') and os.path.isfile(coreclass_path+'/'+'0.txt'):
				with open(coreclass_path+'/'+'diff_sort.txt', 'r', encoding='UTF-8') as ff,open(coreclass_path+'/0.txt','r',encoding='UTF-8') as fc:
					try: 
						linesf = ff.readlines()
						linesc = fc.readlines()
					except:
						with open('./d2'+'/error_file.txt','a+') as fw:
							fw.write(coreclass_path)
							fw.write('\n')
					else:
						# num_commit = num_commit + 1
						is_verb = 1
						is_dobj = 0
						print(coreclass_path)
						version = ['/old/','/new/']
						too_long = 0
						err = 0
						method_list = [[],[]]
						snippet_list = [[],[]]
						for i in range(2):
							# method_list[i].clear()
							if os.path.isfile(coreclass_path+version[i]+file_name+'.java'):
								try:
									code, l = get_code(coreclass_path+version[i]+file_name+'.java')
									
									if l >= 100:
										too_long = 1
										break
									ast = get_ast(code)
									get_method(ast,i)
									get_snippet(ast,i)
									if i == 0:
										code_structure = ''
										get_structure(ast)
										code_structure = code_structure.strip(' ')
										old_list = code_structure.split(' ')
									if i == 1:
										code_structure = ''
										get_structure(ast)
										code_structure = code_structure.strip(' ')
										new_list = code_structure.split(' ')
										get_diff(old_list,new_list,1)
										
										class_structure = code_structure
								except:
									err = 1 #
									break # 可以记录出错路径
						if too_long == 1 or err == 1:
							continue
						diff_list = [[],[]]
						# diff_list[0].clear()
						# diff_list[1].clear()
						get_diff(method_list[0],method_list[1],0)
						code_structure = ''
						for i in diff_list[0]: 
							get_structure(method_list[0][i])
						code_structure = code_structure.strip(' ')
						old_list = code_structure.split(' ')
						code_structure = ''
						for i in diff_list[1]: 
							get_structure(method_list[1][i])
						code_structure = code_structure.strip(' ')
						new_list = code_structure.split(' ')
						
						get_diff(old_list,new_list,1)
						method_structure = code_structure
						diff_list = [[],[]]
						# diff_list[0].clear()
						# diff_list[1].clear()
						get_diff(snippet_list[0],snippet_list[1],0)
						code_structure = ''
						for i in diff_list[0]: 
							get_structure(snippet_list[0][i])
						code_structure = code_structure.strip(' ')
						old_list = code_structure.split(' ')
						code_structure = ''
						for i in diff_list[1]: 
							get_structure(snippet_list[1][i])
						code_structure = code_structure.strip(' ')
						new_list = code_structure.split(' ')
						
						get_diff(old_list,new_list,1)
						snippet_structure = code_structure
						print("----------Seven---------")
						with open('./d2/'+mode+'summ.txt','a+',encoding='UTF-8') as fw:
							for line in linesc:
								line = line.strip('\n')
								if len(line) <= 4:
									continue
								if line[0:5] == '注释信息:':
									line = line[6:]
									line = line.strip(' ')
									line = line.replace('[Java]','')
									line = line.replace('[Java]:','')
									line = line.replace('[Java:]','')
									if ':' in line:
										temp = line.split(':')[0]
										if ' ' not in temp:
											line = line.split(':')[1]
									if ']' in line:
										line = line.split(']')[1]
									line = line.strip(' ')
									if len(line) <= 1:
										#is_verb = 0
										break
									word_num = len(line.split(' '))
									
									if word_num <= 1 or word_num >= 10:
										break

									temp = nlp.dependency_parse(line)
									for i in range(len(temp)):
										if temp[i][0] == 'dobj' and temp[i][1] == 1:
											is_dobj = 1
									if is_dobj == 1:
										line = normalize_word(line)
										line = split_word(line)
										fw.write(line)
									break
							if is_dobj == 1:
								fw.write('\n')
						if is_dobj == 0:
							continue
						num_commit = num_commit + 1
						with open('./d2/'+mode+'story_sort.txt','a+',encoding='UTF-8') as fw,open('./d2/'+mode+'class_sort.txt','a+',encoding='UTF-8') as fclass,open('./d2/'+mode+'method_sort.txt','a+',encoding='UTF-8') as fmethod,open('./d2/'+mode+'snippet_sort.txt','a+',encoding='UTF-8') as fsnippet:
							num = 0
							annotation = 0
							is_new = 0
							is_old = 0
							for line in linesf:
								if num > 300:
									break
								line = line.split('@@')[-1]
								line = line.strip('\n')
								line = line.strip('\r\n')
								line = line.strip(' ')
								line = line.replace('	',' ')
								while '  ' in line:
									line = line.replace('  ',' ')
								if '/*' in line:
									annotation = 1
								if annotation == 1:    
									if '*/' in line:
										annotation = 0
									continue
								if '//' in line:
									continue
								# if 'import' in line:
								# 	continue
								if len(line) <= 1:
									continue
								elif line[0:8] == 'new file':
									is_new = 1
								elif line[0:12] == 'deleted file':
									is_old = 1
								elif line[0:3] == '---' and is_new == 0:
									line = line.replace('---','mmm')
									temp = line.split('/old/')[0]
									temp = temp + '/old/'
									line = line.replace(temp,'')
									line = 'mmm ' + line
								elif line[0:3] == '+++' and is_old == 0:
									line = line.replace('+++','ppp')
									temp = line.split('/new/')[0]
									temp = temp + '/new/'
									line = line.replace(temp,'')
									line = 'ppp ' + line
									is_new = 0
								elif line[0:3] == '+++' and is_old == 1:
									is_old = 0
									continue
								elif line[0] == '+' or line[0] == '-':
									fw.write(line[0])
									fw.write(' ')
									fclass.write(line[0])
									fclass.write(' ')
									fmethod.write(line[0])
									fmethod.write(' ')
									fsnippet.write(line[0])
									fsnippet.write(' ')
									num = num + 2
									line = line[1:]
									line = line.strip(' ')
									line = line.strip('\n')
								# elif 'diff --git' in line or 'index ' in line:
								# 	continue
								else:
									continue
								line = split_word(line)
								fw.write(line)
								fw.write(' <nl> ')
								fclass.write(line)
								fclass.write(' <nl> ')
								fmethod.write(line)
								fmethod.write(' <nl> ')
								fsnippet.write(line)
								fsnippet.write(' <nl> ')
								# if line[0:3] == 'ppp' or line[0:3] == 'mmm':
								# 	astw.write(line)
								# 	astw.write(' <nl> ')
								# else:
								# 	ast = get_ast(line)
								# 	astw.write(ast)
								# 	astw.write(' <nl> ')
								num = num + len(line) + 5
							
							class_structure = class_structure[:900]
							class_structure = class_structure[:class_structure.rfind(' ')]
							snippet_structure = snippet_structure[:900]
							snippet_structure = snippet_structure[:snippet_structure.rfind(' ')]
							method_structure = method_structure[:900]
							method_structure = method_structure[:method_structure.rfind(' ')]
							fclass.write('<ast> ' + class_structure) 
							fclass.write('\n')
							fmethod.write('<ast> ' + method_structure) 
							fmethod.write('\n')
							fsnippet.write('<ast> ' + snippet_structure) 
							fsnippet.write('\n')
							fw.write('\n')
						

