from db import *
import openai
import pandas as pd
import numpy as np
from openai.embeddings_utils import distances_from_embeddings
from flask import session


def ask_openai(question):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"请以一个基督徒的角度回答以下问题，{question}"}
        ]
    )
    return completion.choices[0].message['content']

def translate(t):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"翻译成英文：在圣经里，{t}"}
        ]
    )
    t1 = completion.choices[0].message['content']
    return t1.replace('\n', '')


class Bible:
    def __int__(self):
        self.df = pd.read_csv('genesis_embedding.csv', quotechar='"')
        self.df['embedding'] = self.df['embedding'].apply(eval).apply(np.array)

    def getBookName(self, b):
        return get_db().execute(f'select fullname from BibleID where SN={b}').fetchone()['FullName']

    def getChapter(self, b, c):
        sql = f'select t from t_chn where b={b} and c={c}'
        r = get_db().execute(sql).fetchall()
        r = [(i + 1, x['t']) for i, x in enumerate(r)]
        return {'name': f'{self.getBookName(b)} {c}',
                'verse': r}

    def accurateSearch(self, q):
        sql = f'select b, c, v, t from t_chn where t like "%{q}%" limit 10'
        r = get_db().execute(sql).fetchall()
        r = [{'name': f'{self.getBookName(x["b"])} {x["c"]}:{x["v"]}',
              'verse': [(x["v"], f'{x["t"]}')]} for x in r]
        return r

    def query(self, question=None):
        if question is None:
            return ['']
        q = translate(question)
        q_embedding = openai.Embedding.create(input=q, engine='text-embedding-ada-002')['data'][0]['embedding']
        df = pd.read_csv('bible_embedding.csv', quotechar='"')
        df['embedding'] = df['embedding'].apply(eval).apply(np.array)
        df['distance'] = distances_from_embeddings(q_embedding, df['embedding'].values, distance_metric='cosine')
        chapters = df.sort_values('distance', ascending=True).head(10)
        chapters = zip(chapters.b, chapters.c)
        results = self.accurateSearch(question) + [self.getChapter(x[0], x[1]) for x in chapters]
        return results
