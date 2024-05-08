import random

import pandas as pd
import streamlit as st

import template as t
from utils import load_all_data, get_user

st.set_page_config(layout="wide")

top_k = 8

# select a book to kickstart the interface
if 'ISBN' not in st.session_state:
    st.session_state['ISBN'] = '0385486804'

# select a user to kickstart
if 'User-ID' not in st.session_state:
    # load the dataset with the books
    df_books, df_books_ratings, df_users = load_all_data()
    st.session_state['Books'] = df_books
    st.session_state['Ratings'] = df_books_ratings
    st.session_state['All_Users'] = df_users
    st.session_state['User-ID'] = 2
    st.session_state['User'] = get_user(st.session_state['User-ID'])

df_books = st.session_state['Books']
# # show the consent message only the first time
# if 'Consent' not in st.session_state:
#   st.info('BookCrossing respects your data. Our policy complies with the GDPR. We use pseudonymisation and encryption to collect your personal data and to use them \
#           only for recommendations purposes. By clicking ok you consent to these terms ')
#   data_consent_button = st.button("Ok")
#   placeholder = st.empty()
#   st.session_state['Consent'] = True
#   if data_consent_button:
#     placeholder.empty()

# initializations
friends_list = [277427, 278026, 277523, 276680]
df_book = df_books[df_books['ISBN'] == st.session_state['ISBN']]
dict_isbn_groups = st.session_state['Ratings'].groupby(['ISBN'])['User-ID'].aggregate(lambda x: list(x))


def jaccard_distance(user_ids_isbn_a, user_ids_isbn_b):
    set_isbn_a = set(user_ids_isbn_a)
    set_isbn_b = set(user_ids_isbn_b)

    union = set_isbn_a.union(set_isbn_b)
    intersection = set_isbn_a.intersection(set_isbn_b)

    return len(intersection) / float(len(union))


# create a cover and info column to display the selected book
cover, info = st.columns([2, 3])

with cover:
    # display the image
    st.image(df_book['Image-URL-L'].iloc[0])

with info:
    # display the book information
    st.title(df_book['Book-Title'].iloc[0])
    st.markdown(df_book['Book-Author'].iloc[0])
    st.caption(str(df_book['Year-Of-Publication'].iloc[0]) + ' | ' + df_book['Publisher'].iloc[0])

    button_cols = st.columns(2)
    with button_cols[0]:
        st.button('\U0001F44D', key=random.random(), on_click=t.like_book, args=(st.session_state['ISBN'],))
    with button_cols[1]:
        st.button('\U0001F44E', key=random.random(), on_click=t.like_book, args=(st.session_state['ISBN'], True,))

st.subheader('Keep digging your favorite authors')
userid = st.session_state['User-ID']
df = st.session_state['Ratings'][st.session_state['Ratings']['User-ID'] == userid]
df = df.merge(df_books, on='ISBN')
authors = df['Book-Author'].unique()
titles = df['Book-Title']
rs = df_books[df_books['Book-Author'].isin(authors) & ~df_books['Book-Title'].isin(titles)]
rs = rs.sample(top_k)
print(rs)
t.recommendations(rs)

st.subheader('Trending among your friends')
friends = st.session_state['User']['Friends']
df = st.session_state['Ratings'][st.session_state['Ratings']['User-ID'].isin(friends)]
df = df.merge(df_books, on='ISBN')
rs = df.drop_duplicates(subset=['Book-Title'])
rs = rs.sample(top_k)
print(rs)
t.recommendations(rs)

st.subheader('People with common interests read', st.session_state['ISBN'])
isbn = st.session_state['ISBN']
dict_isbn_groups = st.session_state['Ratings'].groupby(['ISBN'])['User-ID'].aggregate(
    lambda x: list(x))  # create the dictionary
title = df_books[df_books['ISBN'] == isbn]['Book-Title'].values
diff_editions = df_books[((df_books['Book-Title'].isin(title)) & (df_books['ISBN'] != isbn))][
    'ISBN'].values  # find for different editions of the same book
flag = False
if isbn in (dict_isbn_groups.keys()):  # if our isbn is in our dict continue
    pass
else:  # if not try the other editions
    for i in range(len(diff_editions)):
        if diff_editions[i] in (dict_isbn_groups.keys()):
            isbn = diff_editions[i]
            flag = True
    if flag == False:  # if there aren't any other editions, choose a random
        isbn = random.choice(list(dict_isbn_groups.keys()))

lst = []
for book, users in dict_isbn_groups.items():
    d = jaccard_distance(dict_isbn_groups[isbn], users)
    if book != isbn and d > 0.0 and d < 0.8:
        d = jaccard_distance(dict_isbn_groups[isbn], users)
        lst.append([book, d])

jaccard = pd.DataFrame(lst, columns=['ISBN', 'Jaccard Distance'])
jaccard = jaccard.sort_values(by="Jaccard Distance", ascending=False).head(top_k)
rs = df_books[df_books['ISBN'].isin(jaccard['ISBN'])]
df = rs.head(top_k)
print(df)
t.recommendations(df)

st.subheader('About us')
st.write('BookCrossing is an online platform that allows users to share and read books by connecting with other users from the platform. \
          The first set of recommendations that you see are based on your previous books and suggest your favorite authors. If there are no previous readings of yours, random authors are chosen. \
          The second set of recommendations are based on your BookCrossing friends list. If the list is empty, it is initialized by 4 User-IDs: [277427, 278026, 277523, 276680]. \
          Finally, the last set of recommendations are based on users that have rated common books with the ones that you choose, and therefore share your interests.')

# Define the sidebar buttons / text inputs
useremail = st.sidebar.text_input("User Email",
                                  placeholder=f"Currently logged in as user: {st.session_state['User']['Name']}")
log_in_clicked = st.sidebar.button("Log In")
if log_in_clicked:
    if useremail in st.session_state['All_Users']['Email'].unique():
        id = st.session_state['All_Users'].loc[st.session_state['All_Users']['Email'] == useremail, 'User-ID'].iloc[0]
        t.select_user(int(id))
        t.welcome_user()
    else:
        t.wrong_credentials()

st.sidebar.markdown("*Friends*")
with st.sidebar.container(height=100):
    for i, f in enumerate(st.session_state['User']['Friends']):
        friend = get_user(f)
        st.markdown(f"""{i + 1}. {friend['Name']}""")

friendid = st.sidebar.text_input("Let's find your friends!", placeholder="[277427, 278026, 277523, 276680]")
add_clicked = st.sidebar.button("Add")
if add_clicked:
    if friendid.isdigit() and int(friendid) in friends_list:
        t.already_added()
    elif friendid.isdigit() and int(friendid) in st.session_state['Ratings']['User-ID'].unique():
        friends_list.append(friendid)
        t.add_friend(int(friends_list))
    else:
        t.friend_not_found()
