from flask import Flask, render_template, redirect, request, session, jsonify
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import pymongo
import re
from bs4 import BeautifulSoup
from lxml import etree
import pickle
import requests
import json



app = Flask(__name__)
app.secret_key = 'asdgfiyascilasli'
API_KEY = open('./keys/twitter_key').readline().rstrip('\n')

mongo_url = "mongodb+srv://rishab:1234@cluster0.u3qbc.mongodb.net/"
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient["twitter_personality"]
mycol = mydb['mbti_uname']

descriptions = {
    "INTJ" : "Architect: Imaginative and strategic thinkers, with a plan for everything.",
    "INTP" : "Logician: Innovative inventors with an unquenchable thirst for knowledge.",
    "ENTJ" : "Commander: Bold, imaginative and strong-willed leaders, always finding a way - or making one.",
    "ENTP" : "Debater: Smart and curious thinkers who cannot resist an intellectual challenge." ,
    "INFJ" : "Advocate: Quiet and mystical, yet very inspiring and tireless idealists.",
    "INFP" : "Mediator: Poetic, kind and altruistic people, always eager to help a good cause.",
    "ENFJ" : "Protagonist: Charismatic and inspiring leaders, able to mesmerize their listeners.",
    "ENFP" : "Campaigner: Enthusiastic, creative and sociable free spirits, who can always find a reason to smile.",
    "ISTJ" : "Logistician: Practical and fact-minded individuals, whose reliability cannot be doubted.",
    "ISFJ" : "Defender: Very dedicated and warm protectors, always ready to defend their loved ones.",
    "ESTF" : "Executive: Excellent administrators, unsurpassed at managing things - or people.",
    "ESFJ" : "Consul: Extraordinarily caring, social, and popular people, always eager to help.",
    "ISTP" : "Virtuoso: Bold and practical experimenters, masters of all kinds of tools.",
    "ISFP" : "Adventurer: Flexible and charming artists, always ready to explore and experience something new.",
    "ESTP" : "Entrepreneur: Smart, energetic and very perceptive people, who truly enjoy living on the edge.",
    "ESFP" : "Entertainer: Spontaneous, energetic and enthusiastic people - life is never boring around them."
}

def cleanText(text):
    text = BeautifulSoup(text, "lxml").text
    text = re.sub(r'\|\|\|', r' ', text)
    text = re.sub(r'http\S+', r'<URL>', text)
    return text


def get_tweets(uname):
    uname = request.form.get('uname')
    h = {"Authorization": API_KEY}
    result = requests.get(f"https://api.twitter.com/1.1/search/tweets.json?q=from:{uname}", headers=h)
    return (result.json()["statuses"])


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', message=(session.pop('message') if 'message' in session else ''))


@app.route('/show_result', methods=['POST'])
def show_result():
    if request.method == 'POST':
        if not request.form.get('uname'):
            session['message'] = 'Error. Invalid Username Provided'
            return redirect('/')
        uname = request.form.get('uname')
        tweets = get_tweets(uname)
        if not tweets:
            session['message'] = 'Error. Invalid Username Provided'
            return redirect('/')
        else:
            with open('./model/model_IE', 'rb') as IE_file:
                IE_model = pickle.load(IE_file)
            with open('./model/model_JP', 'rb') as JP_file:
                JP_model = pickle.load(JP_file)
            with open('./model/model_NS', 'rb') as NS_file:
                NS_model = pickle.load(NS_file)
            with open('./model/model_TF', 'rb') as TF_file:
                TF_model = pickle.load(TF_file)
            data = [' '.join([tweet['text'] for tweet in tweets])]
            IE = IE_model.predict(data)
            JP = JP_model.predict(data)
            NS = NS_model.predict(data)
            TF = TF_model.predict(data)
            mbti_type = IE[0]+NS[0]+TF[0]+JP[0]
            mycol.replace_one({'uname':uname}, {'uname':uname, 'mbti':mbti_type}, upsert=True)
            return render_template('show_result.html', mbti_type = mbti_type, uname = uname, message = descriptions[mbti_type])

@app.route('/explore', methods = ['GET'])
def explore():
    return render_template('explore.html')

@app.route('/explore-data', methods = ['POST'])
def explore_data():
    all_data = mycol.find({})
    return jsonify([{'uname': person['uname'], 'mbti': person['mbti']} for person in all_data])


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
