# -*- coding: utf-8 -*-
import csv
import math
from math import sqrt
movierating=open('smallmoviedata.csv','r')
#print type(movierating)
ratinglist=csv.DictReader(movierating)
#print type(ratinglist)
#把csv文件的数据整理成{'userId1':{'movie1':rating1，'movie2':rating2,...},'userId2':{...}...}这种结构
m=0
ratingdict={}
for u in ratinglist:
	if u['userId'] in ratingdict:
		ratingdict[u['userId']].update({u['movieId']:u['rating']})
	else:
		ratingdict.update({u['userId']:{u['movieId']:u['rating']}})


def commonprefs(ratingdictname,userId1,userId2):
#找出两个人共同评分的电影，整理成｛'movieId1':{'userId1':'4','userId2':'4.2'},...｝这种数据结构,并计算其相似度（皮尔逊相关系数）
#	commonlist={}
#	for iterm in ratingdictname[userId1].keys():
#		if iterm in ratingdict[userId2].keys():
#			commonlist.update({iterm:{userId1:ratingdict[userId1][iterm],userId2:ratingdict[userId2][iterm]}})
#		else:
#			continue

	commonlist={movieid:{userId1:ratingdictname[userId1][movieid],userId2:ratingdictname[userId2][movieid]} for movieid in ratingdictname[userId1].keys() if movieid in ratingdictname[userId2].keys()}
	movielens=len(commonlist)
	if movielens==0:
#如果二者没有共同评分过的电影则相关系数为０
		return 0
	else:
		sumId1=sum(float(commonmovie[userId1]) for commonmovie in commonlist.values())
		sumId2=sum(float(commonmovie[userId2]) for commonmovie in commonlist.values())		
		sumId1powsum=sum(pow(float(commonmovie[userId1]),2) for commonmovie in commonlist.values())
		sumId2powsum=sum(pow(float(commonmovie[userId2]),2) for commonmovie in commonlist.values())
		sumId1Id2=sum(float(commonmovie[userId1])*float(commonmovie[userId2]) for commonmovie in commonlist.values())
		fenzi=sumId1Id2-(sumId1*sumId2)/movielens
		fenmu=sqrt((sumId1powsum-pow(sumId1,2)/movielens)*(sumId2powsum-pow(sumId2,2)/movielens))
		if fenmu==0:
			return 0
		else:
			r=fenzi/fenmu
#经初步计算发现很多用户之间皮尔逊相关系数都为１，这里将皮尔逊指数乘以Jaccard系数作为指标来衡量两个用户之间电影品味的相似度
			return r*len(set(ratingdictname[userId1].keys())&set(ratingdictname[userId2].keys()))/len(set(ratingdictname[userId1].keys())|set(ratingdictname[userId2].keys()))

#r*pow(len(commonlist),2)/(len(ratingdictname[userId1].keys())*len(ratingdictname[userId2].keys()))


def toptenmatches(ratingdict,userId,n=10,correlation=commonprefs):
#根据给定的userId，算出所有其他userId与给定Id之间的相似度,返回[{'userId2':rating2},{'userId3':rating3},{'userId3':rating3}...]这样的结果
	correlationdict=[{other:correlation(ratingdict,userId,other)} for other in ratingdict.keys() if other!=userId]
	correlationdict.sort(key=lambda x:float(x.values()[0]),reverse=True) #将类似于[{userId2:correlation2},{userId3:correlation3},{..},{..}...]这个数据结构按元素字典的键值降序排列
	return correlationdict[0:n]

def getrecommandbyid(ratingdictname,userId,n=10,correlation=commonprefs):
#根据提供的id获得推荐列表，返回[{'movieId2':tuijianzhishu2},{'movieId3':tuijianzhishu3},{..},{..}...]这样的结果，列表中元素按各字典的键值降序排列
#先获得给定Id用户没看过的电影列表，并设置初始推荐指数为０,数据结构为{'movieid':tuijianzhishu,...}
	sumratings=0
	sumcorrelations=0
	a=[]
	allmovieset=set(a)
	for user in ratingdictname.values():
		for movie in user.keys():
			allmovieset.add(movie)
	unratedmovie=allmovieset-set(ratingdictname[userId].keys())
	toberatemovielist=list(unratedmovie)
#对给定id用户未评价过的电影计算推荐指数，并赋值到toberatemovielist字典中，按降序排列
	unratemovielist=[]
	for unratedmovie in toberatemovielist:
		for otheruser in ratingdictname.keys():
			if otheruser!=userId and unratedmovie in ratingdictname[otheruser].keys():
				sumratings+=correlation(ratingdictname,userId,otheruser)*float(ratingdictname[otheruser][unratedmovie])					
				sumcorrelations+=correlation(ratingdictname,userId,otheruser)
			else:
				continue
		toberate=sumratings/sumcorrelations				
		unratemovielist.append({unratedmovie:toberate})
		unratemovielist.sort(key=lambda x:x.values(),reverse=True)
	return toberatemovielist[0:n]	

def getmoviename(movieidlist):
#给定电影id,输出电影名
	moviefile=open('movies.csv','r')
	moviedictfile=csv.DictReader(moviefile)
	moviedict={}
	for i in moviedictfile:
		moviedict.update({i['movieId']:i['title']})
	movienamelist=[]
	for i in movieidlist:
		movienamelist.append(moviedict[i])
	return movienamelist


inputid=raw_input("请输入id(1-1200之间)，系统将推荐10个与其品味最相似的用户，并给该id用户推荐10部其最可能喜欢的电影:")
movierecoid=getrecommandbyid(ratingdict,inputid)
idreco=toptenmatches(ratingdict,inputid)
print "与该id用户电影品味最相近的10个用户是:\n"
for i in idreco:
	print i.keys()[0],'\n'
print "*********************************************************************\n"
moviereco=getmoviename(movierecoid)
print "该id用户最可能喜欢的10部电影是:\n"
for i in moviereco:
	print i,'\n'
