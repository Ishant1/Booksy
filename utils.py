import json

import pandas as pd
import streamlit as st

USER_FILE = 'data/BX-Users1.csv'
RATING_FILE ='data/BX-Book-Ratings-Subset.csv'
BOOKS_FILE = 'data/BX-Books.csv'

def load_csv(filename):
    csv = pd.read_csv(filename,sep=';', encoding='latin-1')
    if 'Friends' in csv.columns:
        csv['Friends'] = csv['Friends'].apply(lambda x: json.loads(x))
    return csv


def load_all_data():
    df_books = load_csv(BOOKS_FILE)
    df_books_ratings = load_csv(RATING_FILE)
    df_users = load_csv(USER_FILE)
    return df_books, df_books_ratings, df_users


def get_user(id):
    return st.session_state['All_Users'].loc[id-1,:].to_dict()