#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:41:56 2019

@author: sharvil
"""

# Importing packages
import json
import re
import collections
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# Loading downloaded instagram data
json_data = {}
data_path = 'Instagram/messages.json'
with open(data_path) as file:
    json_data = json.load(file)

# Obtaining a list of all direct conversations with Jane
participant = 'jane'
conversation = list()
for message in json_data:
    number_of_participants = len(message['participants'])
    if participant in message['participants'] and number_of_participants == 2:
        conversation.extend(message['conversation'])

# Creating a dataframe
df = pd.DataFrame(conversation)
df['created_at'] = pd.to_datetime(df['created_at'])
df['created_at'] = (df['created_at'].dt.tz_convert('Asia/Kolkata'))

# Indexing on 'created_at' attribute
df.set_index('created_at', inplace=True) 
df.sort_index(inplace=True)

# Displaying statistics
print(df.head())
print(df.info())
print(df.describe())

# Dropping redundant columns
unrequired_features = ['hashtag', 'story_share_type', 'video_call_action', 'voice_media',
                       'profile_share_username', 'profile_share_name',
                       'mentioned_username', 'media', 'heart', 'is_random']
df.drop(unrequired_features, inplace=True, axis=1)

# Exploratory analysis of direct messages
plt.figure(figsize=(10, 5))

# Count plot of texts sent by participants
plt.subplot(1, 2, 1)
direct_messages_df = df.loc[df['text'].notnull(), ['sender', 'text']]
print(direct_messages_df['sender'].value_counts())
g = sns.countplot(x='sender', data=direct_messages_df)
g.set_xticklabels(['john', 'jane'])
g.set_ylabel('Count of texts')
g.set_xlabel('Sender')
g.set_title('Total count of texts sent', y=1.05, bbox={'facecolor':'0.8', 'pad':5})

# Monthly text trends of participants  
plt.subplot(1, 2, 2)
pivoted_direct_messages_df = pd.pivot(direct_messages_df, columns='sender', values='text')
resampled_direct_messages_df = pivoted_direct_messages_df.resample('M').count()
g = sns.lineplot(data=resampled_direct_messages_df,  marker="o")
g.set_ylabel('Count of texts')
g.set_xlabel('Monthwise')
g.set_title('Monthly trend of number of texts shared', y=1.05, bbox={'facecolor':'0.8', 'pad':5})
plt.xticks(rotation=45)
plt.legend(labels=['john', 'jane'])
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 5))

# chats - likes, posts shared, stories shared, gifs
plt.subplot(1, 2, 1)
share_stats_df = df.melt(id_vars='sender', var_name='share_stats', 
                         value_vars=['likes','media_share_caption',
                                     'animated_media_images','story_share']).dropna()

g = sns.countplot(y='share_stats', hue='sender', data=share_stats_df, palette="Blues_d")
g.set_ylabel("Media Type")
g.set_xlabel("Count of shares/likes", labelpad=15)
g.set_title("Media Share Statistics", y=1.05, bbox={'facecolor':'0.8', 'pad':5})
g.set_yticklabels(labels=['likes', 'media', 'gifs', 'stories'])

# most hashtags shared in media share caption
df['media_share_caption'] = df['media_share_caption'].astype('str')
media_captions = ' '.join(df.media_share_caption.values)
hastags = re.findall(r"#(\w+)", media_captions)
counter = collections.Counter(hastags)
most_common_hashtags = list(zip(*counter.most_common(25)))
most_common_hashtags_df = pd.DataFrame({'hashtag': list(most_common_hashtags[0]),
                                   'count': list(most_common_hashtags[1])})

plt.subplot(1, 2, 2)
g = sns.barplot(x='count', y='hashtag', data=most_common_hashtags_df, palette='Blues_d')
g.set_title('Most common hashtags mentioned in shared posts', y=1.05, bbox={'facecolor':'0.8', 'pad':5})
g.set_xlabel('Count of occurence of a hashtag', labelpad=15)
g.set_ylabel('Hashtags')
plt.tight_layout()
plt.show()

# Pie chart distribution of chats acc to time
chat_distribution_df = df['text']
chat_distribution_df.index = df.index.hour
chat_distribution_df = chat_distribution_df.groupby(chat_distribution_df.index).count()

fig1, ax1 = plt.subplots(figsize=(9, 7))
fig1.subplots_adjust(0,0,1,0.5)
labels = list(map(lambda x: str(x) + ":00 hrs", list(chat_distribution_df.index.values)))
patches, texts = ax1.pie(chat_distribution_df, labels=labels, 
                         colors=sns.cubehelix_palette(24), startangle=90,
                         counterclock=False, radius=24*100, labeldistance= 1.1)
#draw circle
centre_circle = plt.Circle((0,0),fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
# Equal aspect ratio ensures that pie is drawn as a circle
plt.legend(patches, chat_distribution_df, loc="right")
ax1.axis('equal')
plt.title('Chat distribution during day hours', y=1.05, bbox={'facecolor':'0.8', 'pad':5})
plt.tight_layout()
plt.show()



