# -*- coding: utf-8 -*-

from PIL import Image
import glob
import numpy as np
import sys
import os
#from skimage.feature import hog
from sklearn.svm import SVC
import cv2
from sklearn.externals import joblib
import math


all_data_set = []  # 原始总数据集，二维矩阵n*m，n个样例，m个属性
all_data_label = []  # 总数据对应的类标签
TRAIN_PICTURE_PATH = "D:\\images_evaluation"

def project(mapp,pjmap,y0,y1,x0,x1):
    pro=[]
    for  i in range(y0,y1+1):
        for j in range(x0,x1+1):
           if mapp[i,j]==0:
               pjmap[i,x0]=0
               pjmap[i,x1]=0
               break
    for j in range(x0,x1+1):
        for i in range(y0,y1+1):
            if  mapp[i,j]==0:
                pjmap[x0,j]=0
                pjmap[x1,j]=0
                break

def fextra(pjmap):
    pj=[]
    s=[0,15,31,47,63]
    for i in s:
        for j  in range(64):
            if pjmap[i,j]==0:
                pj.append(1)
            else :
                pj.append(0)
    for j in s:
        for i in range(64):
            if pjmap[i,j]==0:
                pj.append(1)
            else :
                pj.append(0)
    return pj

def pro(path):
    img = cv2.imread(path,0)
    #cv.imshow('1',img)
    img = cv2.resize(img,(64,64),cv2.INTER_LINEAR)
    pjmap=np.zeros((img.shape[1],img.shape[0]), np.uint8)
    pjmap.fill(255)
    project(img,pjmap,0,15,0,15)
    project(img,pjmap,0,15,15,47)
    project(img,pjmap,0,15,47,63)
    project(img,pjmap,15,47,0,15)
    project(img,pjmap,47,63,0,15)
    project(img,pjmap,15,47,15,47)
    project(img,pjmap,47,63,15,47)
    project(img,pjmap,15,47,47,63)
    project(img,pjmap,47,63,47,63)
    pj=fextra(pjmap)
    p=[]
    for i in range(0,len(pj),4):
        t=pj[i]+pj[i+1]*2+pj[i+2]*4+pj[i+3]*8
        p.append(t)
    pro_c=constraint(min(p),max(p),p)
    return pro_c

def GetCodeFromThin(img_path):
    image=cv2.imread(img_path,0)
    x=image.shape[0]
    y=image.shape[1]
    edges_x=[]
    edges_y=[]
    for i in range(x):
        for j in range(y):
            if image[i][j]==0:
             edges_x.append(i)
             edges_y.append(j)
    left=min(edges_x)               #左边界
    right=max(edges_x)             #右边界
    width=right-left                #宽度
    bottom=min(edges_y)             #底部
    top=max(edges_y)                #顶部
    height=top-bottom               #高度
    pre1_picture=image[left:left+width+1,bottom:bottom+height+1]        #图片截取
    re_image = cv2.resize(pre1_picture,(64,64),interpolation=cv2.INTER_CUBIC)
    #获取改变后图片的大小
    size = re_image.shape
    #获取图片的平均像素值
    avg_pixel = re_image.sum()/(size[0]*size[1])
    #图像二值化
    cv2.threshold(re_image,avg_pixel, 255, cv2.THRESH_BINARY, re_image)
    tan=[]
    s=[]
    im=re_image
    for i in range(im.shape[1]-1,0,-1):
        for j in range(0,int(im.shape[0]/2)):
            if im[i,j] == 0 :
                x=(int(i-im.shape[1]/2))
                y=(int(im.shape[0]/2)-j)
                if x>0:
                    try:
                        t=round(math.degrees(math.atan(y/x)),1)
                        tan.append(t)
                    except:
                        tan.append(0)
                else:
                    try:
                        t=round(90+math.degrees(math.atan(y/x))+90,1)
                        tan.append(t)
                    except:
                        tan.append(0)
                t=round(math.sqrt(x*x+y*y),1)
                s.append(t)
    for i in range(0,im.shape[1]):
        for j in range(int(im.shape[0]/2),im.shape[0]):
            if im[i,j] == 0 :
                x=(int(i-im.shape[1]/2))
                y=(int(im.shape[0]/2)-j)
                if x<0:
                    try:
                        t=round(math.degrees(math.atan(y/x))+180,1)
                        tan.append(t)
                    except:
                        tan.append(0)
                else:
                    try:
                        t=round(math.degrees(math.atan(y/x))+360,1)
                        tan.append(t)
                    except:
                        tan.append(0)
                t=round(math.sqrt(x*x+y*y),1)
                s.append(t)
    l=[]
    for i in range(0,360,1):
        n=0
        for j in range(len(tan)):
            if int(tan[j])==i :
                n=n+1
        # s2='('+str(i)+','+str(n)+')'
        l.append(n)
    # print(l)
    l1=[]
    x=im.shape[1]/2
    y=im.shape[0]/2
    for i in range(0,int(math.sqrt(x*x+y*y))+1):
        n=0
        for j in range(len(s)):
            if i==int(s[j]):
                n=n+1
        # s1='('+str(tan[i])+','+str(n)+')'
        l1.append(n)
    out_Code=l
    for i in range(0,len(l1)):
        out_Code.append(l1[i])
    polar_code=constraint(min(out_Code),max(out_Code),out_Code)
    out=polar_code
    prot=pro(img_path)
    for i in range(0,len(prot)):
        out.append(prot[i])
    return out

def constraint(mi,ma,p):
    q=[]
    for i in range(0,len(p)):
        if (ma-mi)==0:
            t=0
        else:
            t=p[i]-mi/ma-mi
        q.append(t)
    return q

def averagenum(num):
    nsum = 0
    for i in range(len(num)):
        nsum += num[i]
    return nsum / len(num)

pathDir = os.listdir(TRAIN_PICTURE_PATH)
result=[]
for nameDir in pathDir:
    clf=joblib.load("D:\\svm(polar+pro(16))\\" + nameDir  + ".pkl")
    print("svm test starting-------")
    num_sum=0
    num_pos=0
    #pathDir = os.listdir(TEST_PICTURE_PATH)  # 获取文件夹内的所有文件（夹）的名字
    nameDir_abs = os.path.join(TEST_PICTURE_PATH, nameDir)
    Allcharacter = os.listdir(nameDir_abs)
    print("test:",nameDir)
    for character in Allcharacter:
        character_abs = os.path.join(nameDir_abs, character)
        character_img = os.listdir(character_abs)
        for i in range(len(character_img)-5,len(character_img)):
            absPath = os.path.join(character_abs, character_img[i])
            outcode=GetCodeFromThin(absPath)
            out=[]
            out.append(outcode)
            predicts = clf.predict(out)  # 进行svm分类，并返回分类结果
            num_sum= num_sum + 1
            if (predicts == nameDir+"@"+character):
                num_pos = num_pos + 1
    print("Image Total:",num_sum, "Right Rate",num_pos)
    acc= num_pos / num_sum
    print("the acc is:", acc)
    result.append(acc)
print(result)
print(averagenum(result))



