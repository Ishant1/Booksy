from random import random

import streamlit as st

from utils import get_user


# set episode session state
def select_book(isbn):
  st.session_state['ISBN'] = isbn

def like_book(isbn, dislike=False):
  st.session_state['Ratings'] = st.session_state['Ratings']._append({
    'User-ID':st.session_state['User-ID'],
    'ISBN': isbn,
    'Book-Rating': 10 if not dislike else 0,
  }, ignore_index=True)

def select_user(userid):
  st.session_state['User-ID'] = userid
  st.session_state['User'] = get_user(userid)

def add_friend(friends_list):
  st.session_state['Friends'] = friends_list

def tile_item(column, item):
  with column:
    st.button('📖', key=random(), on_click=select_book, args=(item['ISBN'], ))
    with st.container(height=200, border=False):
      st.image(item['Image-URL-M'], use_column_width='always')
      st.caption(item['Book-Title'])

    button_cols = st.columns(2)
    with button_cols[0]:
      st.button('\U0001F44D', key=random(), on_click=like_book, args=(item['ISBN'], ))
    with button_cols[1]:
      st.button('\U0001F44E', key=random(), on_click=like_book, args=(item['ISBN'], True, ))

def recommendations(df):

  # check the number of items
  nbr_items = df.shape[0]

  if nbr_items != 0:    

    # create columns with the corresponding number of items
    columns = st.columns(nbr_items, gap="medium")

    # convert df rows to dict lists
    items = df.to_dict(orient='records')

    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1]) for x in zip(columns, items))

def wrong_credentials():
  st.sidebar.write('Wrong User-ID 😢')

def welcome_user():
  st.sidebar.write(f'Welcome {st.session_state["User"]["Name"]} to BookCrossing! 🥳 ')
  st.sidebar.write('Start reading books to get more personalised recommendations 🧐')
  
def already_added():
    st.sidebar.write('The user is already on your list!')
    st.sidebar.write('Let\'s find another one! 😎')

def friend_not_found():
  st.sidebar.write('We couldn\'t find your friend!')
  st.sidebar.write('Please insert only one User-ID, so that you can add him/her to your friend list') 

