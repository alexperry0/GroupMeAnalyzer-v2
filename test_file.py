from db_utils import db_connect


def create_members_table():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    group_members_sql = """
    CREATE TABLE members (
        id text PRIMARY KEY,
        messages_sent integer,
        likes_given integer,
        likes_received integer,
        words_sent integer,
        likes_by_members integer,
        shared_likes integer,
        self_likes integer)"""
    cur.execute(group_members_sql)


def create_messages_table():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    messages_sql = """
    CREATE TABLE messages (
    id test PRIMARY KEY,
    created_at integer,
    user_id integer,
    group_id integer,
    name text NOT NULL,
    text text NOT NULL,
    system integer,
    favorited_by text )"""
    cur.execute(messages_sql)


def insert_member():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    member_sql = "INSERT INTO members (id, messages_sent, likes_given, likes_received, words_sent, likes_by_members, shared_likes, self_likes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(member_sql, ('1234', 1, 2, 3, 4, 5, 6, 7))
    con.commit()


def insert_message():
    con = db_connect('db_files/test.sqlite3')
    cur = con.cursor()
    message_sql = "INSERT INTO messages (id, created_at, user_id, group_id, name, text, system, favorited_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(message_sql, ('45678', 1410202583, "141020258341304315", "9951046", "GroupMe", 'Aidan Smith added Max Rash, Riley Anderson, and Logan Deyo to the group', 0, '18803415,6517949'))
    con.commit()


create_members_table()
insert_member()

create_messages_table()
insert_message()
