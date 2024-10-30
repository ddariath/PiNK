from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Token(db.Model):
    __tablename__ = 'tokens'

    id_sentences = db.Column(db.Integer, db.ForeignKey('sentences.id_sentence'), primary_key=True)
    id_token = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    pos = db.Column(db.Integer, nullable=False)
    id_lemma = db.Column(db.Integer, db.ForeignKey('lemmas.id_lemma'))
    feats = db.Column(db.String)
    lemma = db.Column(db.String, nullable=False)
    # Определение отношений
    sentence = db.relationship('Sentence', back_populates='tokens')




class Lemma(db.Model):
    __tablename__ = 'lemmas'

    id_lemma = db.Column(db.Integer, primary_key=True)
    lemma_name = db.Column(db.String, nullable=False)



class Sentence(db.Model):
    __tablename__ = 'sentences'

    id_sentence = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text, nullable=False)
    name_of_texts = db.Column(db.String, nullable=False)
    url = db.Column(db.String)

    # Определение отношений
    tokens = db.relationship('Token', back_populates='sentence')



