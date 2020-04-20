import requests
import sys
import argparse
import json
import db_utils
import excel_util
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sentiment_analyzer = SentimentIntensityAnalyzer()


def get_groups():
    response = requests.get('https://api.groupme.com/v3/groups?token=' + TOKEN)
    return response.json()['response']


def log_groups(groups):
    if len(groups) == 0:
        print('You are not part of any groups.')
        return
    for i, group in enumerate(groups):
        print('%d. %s' % (i, group['name']))


def new_user(id, name):
    member = {'id': id, 'name': name, 'messages_sent': 0, 'likes_given': 0, 'likes_received': 0, 'words_sent': 0, 'likes_by_member': {}, 'shared_likes': {}, 'self_likes': 0, 'messages': []}
    db_utils.insert_member(member)
    return member


def prepare_user_dictionary(members):
    return {member['user_id']: new_user(member['user_id'], member['name']) for member in members}


def load_cache_file(group_name):
    try:
        with open("{}.txt".format(group_name)) as json_file:
            print("Loading data from cache file.")
            messages = json.load(json_file)
            return messages
    except FileNotFoundError:
        print("No cache file found. Will request data from GroupMe")
        return []


def cache_messages(group_name, messages):
    db_utils.insert_messages(messages)


def download_messages(messages, group, message_count):
    progress_bar_message = ''
    if len(messages) > 0:
        message_id = messages[-1]['id']
        message_number = len(messages)
        progress_bar_message = 'New Messages Found - Downloading From GroupMe'
    else:
        message_id = 0
        message_number = 0
        progress_bar_message = 'Downloading Messages from GroupMe'
        
    while message_number < message_count:
        params = {
            # Get maximum number of messages at a time
            'limit': 100,
        }
        #if message_id:
         #   params['before_id'] = message_id
        #else:
        params['after_id'] = message_id
        response = requests.get('https://api.groupme.com/v3/groups/%s/messages?token=%s' % (group['id'], TOKEN), params=params)
        new_messages = response.json()['response']['messages']
        messages.extend(new_messages)
        message_number = len(messages)
        message_id = new_messages[-1]['id']  # Get last message's ID for next request
        progress_bar(message_number, message_count, progress_bar_message)


def analyze_messages(messages, users):
    message_number = 0
    likesInGivenTimeKru = 0
    likesInGivenTimeShep = 0
    for message in messages:
        message_number += 1

        name = message['name']
        text = message['text'] or ''

        # Word count
        for char in '-.,\n':
            text = text.replace(char, ' ')
        message_word_count = len(text.split())

        sender_id = message['sender_id']
        if sender_id == 'system':
            continue
        likers = message['favorited_by']

        if message['created_at'] >= 1532217600:
            if sender_id == '20930113':
                likesInGivenTimeKru += len(likers)

        if message['created_at'] >= 1532217600:
            if sender_id == '19671512':
                likesInGivenTimeShep += len(likers)

        if sender_id not in users.keys():
            continue
            #users[sender_id] = new_user(sender_id, name)

        # Fill in name if it's not in the dictionary
        if not users[sender_id]['name']:
                users[sender_id]['name'] = name

        users[sender_id]['messages'].append(text)

        for user_id in likers:


            if user_id not in users.keys():
                # Leave name blank for now
                continue
                #users[user_id] = new_user(user_id, '')


            
            if sender_id == user_id:
                users[sender_id]['self_likes'] += 1
                continue
                
            if users[sender_id]['likes_by_member'].get(user_id):
                users[sender_id]['likes_by_member'][user_id] += 1
                users[user_id]['shared_likes'][sender_id] += 1
            else:
                users[sender_id]['likes_by_member'][user_id] = 1
                users[user_id]['shared_likes'][sender_id] = 1
                
            users[user_id]['likes_given'] += 1

        users[sender_id]['messages_sent'] += 1  # add one to sent message count
        users[sender_id]['likes_received'] += len(likers)
        users[sender_id]['words_sent'] += message_word_count

        progress_bar(message_number, message_count, 'Analyzing Data')
    #sentiment_analysis(users)


def sentiment_analysis(users):
    for user in users:
        neutral, negative, positive = 0, 0, 0
        for message in users[user]['messages']:
            scores = sentiment_analyzer.polarity_scores(message)
            scores.pop('compound', None)

            max_attribute = max(scores, key=lambda k: scores[k])

            if max_attribute == "neu":
                neutral += 1
            elif max_attribute == "neg":
                negative += 1
            else:
                positive += 1

        total = neutral + negative + positive
        print(total)
        print("Negative: {0}% | Neutral: {1}% | Positive: {2}%".format(
            negative * 100 / total, neutral * 100 / total, positive * 100 / total))

        labels = 'Neutral', 'Negative', 'Positive'
        sizes = [neutral, negative, positive]
        colors = ['#00bcd7', '#F57C00', '#CDDC39']

        # Plot
        plt.pie(sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=140)

        plt.axis('equal')
        plt.title("Sentiment Analysis - Chat with {0}".format(users[user]['name']))

        plt.show()


def analyze_group(group, users, message_count):
    messages = load_cache_file(group['name'])
    download_messages(messages, group, message_count)
    analyze_messages(messages, users)
    print()
    cache_messages(group['name'], messages)
    return users


def progress_bar(value, end_value, text, bar_length=50):
    percent = float(value) / end_value
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write("\r{}: [{}] {}%".format(text, arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def display_data(users, display_likes_given_received_by_and_to_others):
    for user in users:
        try:
            likes_per_message = users[user]['likes_received'] / users[user]['messages_sent']
        except ZeroDivisionError:
            likes_per_message = 0
        print(('{name} | Messages sent: {messages}, Likes given: {likes}, Self-likes: {self_likes}, Likes received: {likes_received}, ' +
            'Avg. Likes per message: {likes_per_message:.2f}, Words sent: {words_sent}'
                ).format(name=users[user]['name'],
                        messages=users[user]['messages_sent'],
                        likes=users[user]['likes_given'],
                        self_likes=users[user]['self_likes'],
                        likes_received=users[user]['likes_received'],
                        likes_per_message=likes_per_message,
                        words_sent=users[user]['words_sent']))

        if display_likes_given_received_by_and_to_others:
            print('Portion of total likes received by other members:')
            likes_received_sorted = sorted(users[user]['likes_by_member'].items(), key=lambda x: x[1], reverse=True)
            for likes_received_by_other_members_map in likes_received_sorted:
                try:
                    percent = (likes_received_by_other_members_map[1] / users[user]['likes_received']) * 100
                except ZeroDivisionError:
                    percent = 0
                print('{}: {} - {}%'.format(users[likes_received_by_other_members_map[0]]['name'],likes_received_by_other_members_map[1], round(percent, 2)))
                
            print()
            
            print('Portion of total likes given to other members:')
            likes_given_sorted = sorted(users[user]['shared_likes'].items(), key=lambda x: x[1], reverse=True)
            for likes_given_to_other_members_map in likes_given_sorted:
                try:
                    percent = (likes_given_to_other_members_map[1] / users[user]['likes_given']) * 100
                except ZeroDivisionError:
                    percent = 0
                print('{}: {} - {}%'.format(users[likes_given_to_other_members_map[0]]['name'],likes_given_to_other_members_map[1], round(percent, 2)))
            print()
        print()


def save(users, group_name):
    for user in users:
        db_utils.update_member(users[user])

    db_utils.update_individual_member_table(users)
    workbook = excel_util.xlsxwriter.Workbook('{}.xlsx'.format(group_name))

    excel_util.create_summary_data_sheet(workbook, users)
    excel_util.create_likes_given_and_received_charts(workbook, users)

    workbook.close()

parser = argparse.ArgumentParser(description='Analyze a GroupMe chat')
parser.add_argument('token', help='Your GroupMe developer token')
args = parser.parse_args()

TOKEN = args.token
if not TOKEN:
    from getpass import getpass
    print('If you have not done so already, go to the following website to receive your API token: ' +
          'https://dev.groupme.com/. When signing up, it does not matter what you put for the callback URL. ' +
          'Alternately, click "Access Token" to use your account for authentication.')
    TOKEN = getpass('Enter your developer access token (hidden): ')

groups = get_groups()
log_groups(groups)

try:
    group_number = int(input('Enter the number of the group you would like to analyze: '))
except ValueError:
    print('Not a number')

group = groups[group_number]

# Display basic group data before analysis
group_name = group['name']
message_count = group['messages']['count']

print()
print('Analyzing %d messages from %s' % (message_count, group_name))
db_utils.create_summary_table()
# Put all the members currently in group into a dict
members = group['members']
db_utils.create_members_table()
users = prepare_user_dictionary(members)

# create tables
db_utils.create_messages_table()
db_utils.create_individual_member_tables(users)

# Iterate through messages to collect data
users = analyze_group(group, users, message_count)

# Show data
display_data(users, True)
save(users, group_name)

