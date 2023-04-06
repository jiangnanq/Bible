import sqlite3
from datetime import datetime
import openai
import pandas as pd
import numpy as np
from Datamanager import *
from openai.embeddings_utils import distances_from_embeddings

def query(question):
    q = translate(question)
    print(question, q)
    q_embedding = openai.Embedding.create(input=q, engine='text-embedding-ada-002')['data'][0]['embedding']
    df = pd.read_csv('bible_embedding.csv', quotechar='"')
    df['embedding'] = df['embedding'].apply(eval).apply(np.array)
    df['distance'] = distances_from_embeddings(q_embedding, df['embedding'].values, distance_metric='cosine')
    chapters = df.sort_values('distance', ascending=True).head(10)
    chapters = zip(chapters.b, chapters.c)
    return [(x[0], x[1]) for x in chapters]

def savequestion(question):
    db = sqlite3.connect('bible_chn.db')
    curr = db.cursor()
    sql = 'insert into sample_question (question) values (?)'
    curr.execute(sql, (question,))
    lastid = curr.lastrowid
    db.commit()
    return lastid

def saveanswer(question_id, gpt, verses):
    db = sqlite3.connect('bible_chn.db')
    curr = db.cursor()
    sql = 'insert into sample_answer (qid, b, c) values (?, ?, ?)'
    for oneverse in verses:
        curr.execute(sql, (question_id, oneverse[0], oneverse[1]))
    sql = 'insert into sample_gpt (qid, gpt) values (?, ?)'
    curr.execute(sql, (question_id, gpt))
    db.commit()
    

def readquestion():
    db = sqlite3.connect('bible_chn.db')
    curr = db.cursor()
    sql = 'select id, question from sample_question'
    curr.execute(sql)
    return curr.fetchall()

if __name__ == '__main__':
    print(f'{datetime.now().strftime("%X")}: Start working')
    q = '文士和法利赛人为什么要试探耶稣？'
    id = savequestion(q)
    print(id)
    gpt = ask_openai(q)
    print(gpt)
    verses = query(q)
    print(verses)
    saveanswer(id, gpt, verses)
    print(f'{datetime.now().strftime("%X")}: job completed.')

