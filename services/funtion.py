from flask import Flask
from db import db_connection

def getAllPosts():
    conn = db_connection()
    cur = conn.cursor()
    sql = "SELECT id, title, body, username, users_id FROM posts ORDER BY id"
    cur.execute(sql)
    forum = cur.fetchall()
    cur.close()
    conn.close()
    return forum

def get_username_by_id(id):
    conn = db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM posts ps WHERE ps.id IN (SELECT pt.post_id FROM put_posts pt WHERE pt.topic_id='%d')" % (int(id))
    cur.execute(sql)
    forum_id = cur.fetchone()
    cur.close()
    conn.close()
    return forum_id

def get_all_comments(id):
    conn = db_connection()
    cur = conn.cursor()
    sql = "SELECT body,username FROM comments WHERE FK_post_id = '%d' " % (int(id))
    cur.execute(sql)
    comments = cur.fetchone()
    cur.close()
    conn.close()
    return comments
    
    