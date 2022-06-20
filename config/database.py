import mysql.connector
from mysql.connector import Error

from helper.utilities import get_config


class Session:

    def __init__(self, config: dict):
        self.username = config.get('username')
        self.password = config.get('password')
        self.hostname = config.get('hostname')
        self.database = config.get('database')

    def set_cnx(self):
        cnx = mysql.connector.connect(
            user=self.username, 
            password=self.password, 
            host=self.hostname, 
            database=self.database
        )
        return cnx
    
    def set_cursor_select(self, cnx):
        return cnx.cursor(dictionary=True, buffered=True)
    
    def set_cursor_insert(self, cnx):
        return cnx.cursor(prepared=True)

def init_sess():
    sess = Session(get_config('mysql'))
    sess.cnx = sess.set_cnx()
    sess.cursor_select = sess.set_cursor_select(sess.cnx)
    sess.cursor_insert = sess.set_cursor_insert(sess.cnx)
    return sess