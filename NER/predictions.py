#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import cv2
import pytesseract
from glob import glob
import spacy
import re
import string
import warnings
warnings.filterwarnings('ignore')
from spacy import displacy

# 1.load model
model_ner = spacy.load('./output/model-best/')


def cleanText(txt):
    whiteSpace = string.whitespace
    specCharacters = '!#$%&\'()*+:;<=>?[\\]^`{|}~'
    tableWhiteSpace = str.maketrans('','', whiteSpace)
    tableSpecCharacters = str.maketrans('','',specCharacters)
    
    text = str(txt)
    text = text.lower()
    removeWhiteSpace = text.translate(tableWhiteSpace)
    removespecCharacters = removeWhiteSpace.translate(tableSpecCharacters)
    
    return str(removespecCharacters)

class groupgenerator():
    def __init__(self):
        self.id= 0
        self.text=''
    def getgroup(self, text):
        if self.text == text:
            return self.id
        else:
            self.id += 1
            self.text = text
            return self.id

def parser(text, label):
    if label in ('PHONE','CELL_PHONE','FAX'):
        text = text.lower()
        text = re.sub(r'\D', '', text)
        
    elif label == 'EMAIL':
        text = text.lower()
        special_char = '@_.\-'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(special_char), '', text)
        
    elif label == 'WEBSITE':
        text = text.lower()
        special_char = ':/.%#\-'
        text = re.sub(r'[^A-Za-z0-9{} ]'.format(special_char), '', text)
        
    elif label in ('COMPANY', 'STREET', 'COUNTRY'):
        text = text.lower()
        text = text.title()
    
    return text


group_gen = groupgenerator()

def getPredictions(image):
    # 2.Extract data using Pytesseract
    tessData = pytesseract.image_to_data(image, lang='hrv')

    # 3.Convert data into dataframe
    tessList = list(map(lambda x:x.split('\t'), tessData.split('\n')))
    df = pd.DataFrame(tessList[1:], columns=tessList[0])
    df.dropna(inplace=True) #drop missing values
    df['text'] = df['text'].apply(cleanText) #text cleaning

    # 4.Convert data into content
    df_clean = df.query('text != "" ')  #selecting all the text with value
    content = " ".join([w for w in df_clean['text']])  #joining all the words with space

    # 5.Get prediction from model
    doc = model_ner(content)

    # 6.Convertin doc into json
    docjson = doc.to_json()
    doc_text = docjson['text']

    # 7.Creating tokens
    dataframe_tokens = pd.DataFrame(docjson['tokens'])
    dataframe_tokens['token'] = dataframe_tokens[['start', 'end']].apply(
        lambda x:doc_text[x[0]:x[1]], axis = 1) #joining text to start and end - dataframe

    # 8.Merging tables
    right_table = pd.DataFrame(docjson['ents'])[['start', 'label']]
    dataframe_tokens = pd.merge(dataframe_tokens, right_table, how='left', on='start')

    # 9.Filling NaN val with 'O'
    dataframe_tokens.fillna('O', inplace=True)

    # 10.Join table to df_clean dataframe
    df_clean['end'] = df_clean['text'].apply(lambda x: len(x) + 1).cumsum() - 1
    df_clean['start'] = df_clean[['text', 'end']].apply(lambda x: x[1] - len(x[0]), axis=1)
    df_clean.head(8)

    # 11.Inner join 'df_clean' and 'dataframe_tokens'
    dataframe_info = pd.merge(df_clean, dataframe_tokens[['start', 'token', 'label']], how='inner', on='start')

    # 12.Bounding box
    box_df = dataframe_info.query("label != 'O' ")

    # 13.Grouping tags
    box_df['label'] = box_df['label'].apply(lambda x: x[2:]) #cutting out first two letters from tags

    # 14.Group the labels
    box_df['group'] = box_df['label'].apply(group_gen.getgroup)

    # 15.Right and bottom of bounding box
    box_df[['left','top','width','height']] = box_df[['left','top','width','height']].astype(int)
    box_df['right'] = box_df['left'] + box_df['width']
    box_df['bottom'] = box_df['top'] + box_df['height']

    # 16.Tagging: groupby group
    col_group = ['left','top','right','bottom', 'label', 'token', 'group']
    group_tag_img = box_df[col_group].groupby(by='group')
    img_tagging = group_tag_img.agg({
        'left':min,
        'right': max,
        'top': min,
        'bottom': max,
        'label': np.unique,
        'token': lambda x: " ".join(x)
    })

    # 17.Converting object into string and cutting first two and last two letters
    img_tagging['label'] = img_tagging['label'].astype(str) 
    img_tagging['label'] = img_tagging['label'].apply(lambda x: x[2:]) #cut first two char ['COMPANY']
    img_tagging['label'] = img_tagging['label'].apply(lambda x: x[:len(x)-2])#cut last two char['COMPANY']

    # 18.Drawing rectangle
    img_bb=image.copy()

    for l,r,t,b,label,token in img_tagging.values:
        cv2.rectangle(img_bb, (l,t), (r,b), (0,255,0), 2)
        cv2.putText(img_bb, label, (l,t), cv2.FONT_HERSHEY_PLAIN, 1.2, (255,0,255),2)

    # 19.Entities
    info_array = dataframe_info[['token','label']].values
    entities = dict(
        COMPANY=[], 
        STREET=[], 
        CITY=[], 
        COUNTRY=[], 
        PHONE=[], 
        FAX=[],
        CELL_PHONE=[], 
        POST_NUMBER=[], 
        EMAIL=[], 
        WEBSITE=[],
        MBS=[], 
        IBAN=[], 
        OIB=[])
    
    previous = 'O'

    for token, label in info_array:
        bio_tag = label[:1]
        label_tag = label[2:]

        # 1.parse the token
        text = parser(token, label_tag)

        if bio_tag in ('B', 'I'):
            if previous != label_tag:
                entities[label_tag].append(text)
            else:
                if bio_tag == 'B':
                    entities[label_tag].append(text)
                else:
                    if label_tag in ('COMPANY', 'STREET', 'CITY', 'COUNTRY'): # join with space
                        entities[label_tag][-1] = entities[label_tag][-1] + " " + text
                    else:
                        entities[label_tag][-1] = entities[label_tag][-1] + text
        previous = label_tag

    return img_bb, entities