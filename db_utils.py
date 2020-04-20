import sqlite3
import os


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_summary_table():
    con = db_connect()
    cur = con.cursor()
    group_members_sql = ("""
        CREATE TABLE IF NOT EXISTS members (
            id text PRIMARY KEY,
            name text,
            messages_sent integer,
            likes_given integer,
            likes_received integer,
            words_sent integer,
            self_likes integer)""")
    cur.execute(group_members_sql)


def create_members_table():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    group_members_sql = """
    CREATE TABLE IF NOT EXISTS members (
        id text PRIMARY KEY,
        name text,
        messages_sent integer,
        likes_given integer,
        likes_received integer,
        words_sent integer,
        likes_by_members integer,
        shared_likes integer,
        self_likes integer)"""
    cur.execute(group_members_sql)


def create_individual_member_tables(users):
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    for user in users:
        table_name = users[user]['name'].replace(' ', '_')
        group_members_sql = ("""
        CREATE TABLE IF NOT EXISTS {} (
            id text PRIMARY KEY,
            name text,
            likes_given_to integer,
            likes_received_from integer)""").format(table_name)
        cur.execute(group_members_sql)
        group_members_data_sql = ("""
            INSERT OR IGNORE INTO {} (id, name, likes_given_to, likes_received_from) 
            VALUES (?, ?, ?, ?)""").format(table_name)
        for user_inner in users:
            cur.execute(group_members_data_sql, (users[user_inner]['id'], users[user_inner]['name'], 0, 0))
    con.commit()


def create_messages_table():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    messages_sql = """
    CREATE TABLE IF NOT EXISTS messages (
    id test PRIMARY KEY,
    created_at integer,
    user_id integer,
    group_id integer,
    name text NOT NULL,
    text text,
    system integer,
    favorited_by text )"""
    cur.execute(messages_sql)


def insert_member(member):
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    member_sql = "INSERT OR IGNORE INTO members (id, name, messages_sent, likes_given, likes_received, words_sent, self_likes) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cur.execute(member_sql, (member['id'], member['name'], member['messages_sent'], member['likes_given'], member['likes_received'], member['words_sent'], member['self_likes']))
    con.commit()


def update_member(member):
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    member_sql = "UPDATE members SET name = ?, messages_sent = ?, likes_given = ?, likes_received = ?, words_sent = ?, self_likes = ? WHERE id = ?"
    cur.execute(member_sql, (member['name'], member['messages_sent'], member['likes_given'], member['likes_received'], member['words_sent'], member['self_likes'], member['id']))
    con.commit()


def insert_messages(messages):
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    for message in messages:
        message_sql = "INSERT OR IGNORE INTO messages (id, created_at, user_id, group_id, name, text, system, favorited_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(message_sql, (message['id'], message['created_at'], message['user_id'], message['group_id'], message['name'], message['text'], message['system'], ','.join(message['favorited_by'])))
    con.commit()


def update_individual_member_table(users):
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    for user in users:
        table_name = users[user]['name'].replace(' ', '_')
        likes_given = users[user]['shared_likes'].items()
        likes_received = users[user]['likes_by_member'].items()
        for given in likes_given:
            member_sql = "UPDATE {} SET likes_given_to = ? WHERE id = ?".format(table_name)
            cur.execute(member_sql, (given[1], given[0]))

        for received in likes_received:
            member_sql = "UPDATE {} SET likes_received_from = ? WHERE id = ?".format(table_name)
            cur.execute(member_sql, (received[1], received[0]))

    con.commit()


