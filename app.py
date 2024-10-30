from flask import Flask, render_template, request
from pymorphy3 import MorphAnalyzer
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import func
from models import Token, Lemma, Sentence
import os
from sqlalchemy.orm import aliased
from funcs import process_input, get_lemma


morph = MorphAnalyzer(lang='ru')

db = SQLAlchemy()

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'corpus.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

pos = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'GRND', 'INTJ', 'NOUN', 'NUM',
       'PART', 'PRON', 'PROPN', 'PRT', 'SCONJ', 'VERB']
translate = {'NOUN': ['NOUN'], 'ADJF': ['ADJF', 'DET'], 'ADJS': ['ADJ'], 'COMP': ['ADJ'], 'VERB': ['VERB', 'AUX'],
                 'INFN': ['INFN'], 'PRTF': ['PRT'], 'PRTS': ['PRT'], 'GRND': ['GRND'], 'NUMR': ['NUM'], 'ADVB': ['ADV'],
                 'NPRO': ['PRON'], 'PRED': ['ADV'], 'PREP': ['ADP'], 'CONJ': ['CCONJ', 'SCONJ'], 'PRCL': ['PART'],
                 'INTJ': ['INTJ']}


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/search')
def search():
    return render_template('single_search.html')


@app.route('/bigrams')
def bi_search():
    return render_template('bigrams_search.html')


@app.route('/trigrams')
def tri_search():
    return render_template('trigrams_search.html')


@app.route('/single_results')
def results():

    if request.values:

        full_inp = request.values.get('text', str)
        res = process_input(full_inp, pos)
        if res == 0:
            return render_template('error.html')
        inp, inp_pos = res[0], res[1]
        num = request.values.get('num', int)
        req_type = request.values.get('type', str)

        # случай когда мы ищем по тегу
        if req_type == 'pos':
            inp = inp.upper()
            search_result = db.session.query(Token.token, Sentence.sentence, Sentence.name_of_texts, Sentence.url, Token.feats)\
                .join(Token, Sentence.id_sentence == Token.id_sentences) \
                .filter(Token.pos == inp) \
                .order_by(func.random()) \
                .limit(num) \
                .all()

        # ищем по лемме. если есть указание на часть речи от пользователя - надо найти среди разборов pymorphy тот,
        # который относится к соответствующей части речи
        elif req_type == 'lemma':
            inp_lemms = get_lemma(inp, inp_pos, translate)
            if inp_lemms == 0:
                return render_template('error.html')

            search_result = db.session.query(Token.token, Sentence.sentence, Sentence.name_of_texts, Sentence.url, Token.feats) \
                .join(Token, Sentence.id_sentence == Token.id_sentences) \
                .filter(Token.lemma == inp_lemms) \
                .filter(Token.pos.in_(inp_pos)) \
                .limit(num) \
                .all()

        # ищем по токену
        else:
            inp = inp.lower()
            search_result = db.session.query(Token.token, Sentence.sentence, Sentence.name_of_texts, Sentence.url, Token.feats) \
                .join(Token, Sentence.id_sentence == Token.id_sentences) \
                .filter(Token.token == inp) \
                .filter(Token.pos.in_(inp_pos)) \
                .limit(num) \
                .all()

        search_result = search_result

    else:
        search_result = []

    if search_result:
        return render_template('single_results.html', results=search_result)

    else:
        return render_template('error.html')


@app.route('/bigrams_results')
def bi_results():
    if request.values:

        full_inp1 = request.values.get('text1', str)
        full_inp2 = request.values.get('text2', str)
        res1 = process_input(full_inp1, pos)
        res2 = process_input(full_inp2, pos)
        if res1 == 0 or res2 == 0:
            return render_template('error.html')
        inp1, inp_pos1, inp2, inp_pos2 = res1[0], res1[1], res2[0], res2[1]
        num = request.values.get('num', type=int)
        req_type1 = request.values.get('type1', type=str)
        req_type2 = request.values.get('type2', type=str)

        Token1 = aliased(Token)
        Token2 = aliased(Token)

        # базовый запрос
        query = db.session.query(Token1.token, Token2.token, Sentence.sentence, Sentence.name_of_texts, Sentence.url,
                                 Token1.feats, Token2.feats)\
            .join(Token1, Sentence.id_sentence == Token1.id_sentences)\
            .join(Token2, Sentence.id_sentence == Token2.id_sentences)\

        filters = []

        if req_type1 == 'pos1':
            inp1 = inp1.upper()
            filters.append(Token1.pos == inp1)
        elif req_type1 == 'lemma1':

            inp_lemms1 = get_lemma(inp1, inp_pos1, translate)
            if inp_lemms1 == 0:
                return render_template('error.html')

            filters.append(Token1.lemma == inp_lemms1)
            filters.append(Token1.pos.in_(inp_pos1))
        elif req_type1 == 'token1':
            inp1 = inp1.lower()
            filters.append(Token1.token == inp1)
            filters.append(Token1.pos.in_(inp_pos1))

        if req_type2 == 'pos2':
            inp2 = inp2.upper()
            filters.append(Token2.pos == inp2)
        elif req_type2 == 'lemma2':

            inp_lemms2 = get_lemma(inp2, inp_pos2, translate)
            if inp_lemms2 == 0:
                return render_template('error.html')

            filters.append(Token2.lemma == inp_lemms2)
            filters.append(Token2.pos.in_(inp_pos2))
        elif req_type2 == 'token2':
            inp2 = inp2.lower()
            filters.append(Token2.token == inp2)
            filters.append(Token2.pos.in_(inp_pos2))

        # условие для последовательности токенов
        filters.append(Token2.id_token == Token1.id_token + 1)

        # применение фильтров к запросу
        if filters:
            query = query.filter(*filters)
            print(query)

        search_result = query.distinct()\
            .order_by(func.random())\
            .limit(num)\
            .all()

    if search_result:
        return render_template('bigrams_results.html', results=search_result)

    else:
        return render_template('error.html')


@app.route('/trigrams_results')
def tri_results():
    if request.values:
        num = request.values.get('num', type=int)
        req_type1 = request.values.get('type1', type=str)
        req_type2 = request.values.get('type2', type=str)
        req_type3 = request.values.get('type3', type=str)
        full_inp1 = request.values.get('text1', type=str)
        full_inp2 = request.values.get('text2', type=str)
        full_inp3 = request.values.get('text3', type=str)
        res1 = process_input(full_inp1, pos)
        res2 = process_input(full_inp2, pos)
        res3 = process_input(full_inp3, pos)
        if res1 == 0 or res2 == 0 or res3 == 0:
            return render_template('error.html')
        inp1, inp_pos1, inp2, inp_pos2, inp3, inp_pos3 = res1[0], res1[1], res2[0], res2[1], res3[0], res3[1]
        print(inp1, inp_pos1, inp2, inp_pos2, inp3, inp_pos3)

        Token1 = aliased(Token)
        Token2 = aliased(Token)
        Token3 = aliased(Token)

        # базовый запрос
        query = db.session.query(Token1.token, Token2.token, Token3.token, Sentence.sentence, Sentence.name_of_texts,
                                 Sentence.url, Token1.feats, Token2.feats, Token3.feats)\
            .join(Token1, Sentence.id_sentence == Token1.id_sentences)\
            .join(Token2, Sentence.id_sentence == Token2.id_sentences) \
            .join(Token3, Sentence.id_sentence == Token3.id_sentences)
        filters = []

        if req_type1 == 'pos1':
            inp1 = inp1.upper()
            filters.append(Token1.pos == inp1)
        elif req_type1 == 'lemma1':
            inp_lemms1 = get_lemma(inp1, inp_pos1, translate)
            if inp_lemms1 == 0:
                return render_template('error.html')

            filters.append(Token1.lemma == inp_lemms1)
            filters.append(Token1.pos.in_(inp_pos1))
        elif req_type1 == 'token1':
            inp1 = inp1.lower()
            filters.append(Token1.token == inp1)
            filters.append(Token1.pos.in_(inp_pos1))

        if req_type2 == 'pos2':
            inp2 = inp2.upper()
            filters.append(Token2.pos == inp2)
        elif req_type2 == 'lemma2':
            inp_lemms2 = get_lemma(inp2, inp_pos2, translate)
            if inp_lemms2 == 0:
                return render_template('error.html')

            filters.append(Token2.lemma == inp_lemms2)
            filters.append(Token2.pos.in_(inp_pos2))
        elif req_type2 == 'token2':
            inp2 = inp2.lower()
            filters.append(Token2.token == inp2)
            filters.append(Token2.pos.in_(inp_pos2))

        if req_type3 == 'pos3':
            inp3 = inp3.upper()
            filters.append(Token3.pos == inp3)
        elif req_type3 == 'lemma3':
            inp_lemms3 = get_lemma(inp3, inp_pos3, translate)
            if inp_lemms3 == 0:
                return render_template('error.html')

            filters.append(Token3.lemma == inp_lemms3)
            filters.append(Token3.pos.in_(inp_pos3))
        elif req_type3 == 'token3':
            inp3 = inp3.lower()
            filters.append(Token3.token == inp3)
            filters.append(Token3.pos.in_(inp_pos3))

        # условие для последовательности токенов
        filters.append(Token2.id_token == Token1.id_token + 1)
        filters.append(Token3.id_token == Token2.id_token + 1)
        # применение фильтров к запросу
        if filters:
            query = query.filter(*filters)
            print(query)

        search_result = query.distinct()\
            .order_by(func.random())\
            .limit(num)\
            .all()

    if search_result:
        return render_template('trigrams_results.html', results=search_result)

    else:
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
