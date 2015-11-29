#!/usr/bin/env python

import argparse
import sqlite3
from os import environ
import datetime

KEYPAD_IDS = ['inside', 'outside']

def db_connect():
    db_name = environ.get('DB_BASE_PATH', './') + 'keypad.db'
    return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

def main(cmd_args):
    if cmd_args.command == 'create':
        create_cmd()
    elif cmd_args.command == 'add' and cmd_args.cmdargs[0] and cmd_args.cmdargs[0] == 'user':
        add_user(cmd_args.cmdargs[1], cmd_args.cmdargs[2])
    elif cmd_args.command == 'add' and cmd_args.cmdargs[0] and cmd_args.cmdargs[0] == 'permissions':
        add_permissions(cmd_args.cmdargs[1], cmd_args.cmdargs[2])
    else:
        print 'Unknown command - %s' % cmd_args.command

def create_cmd():
    print 'Creating database at %s...' % (environ.get('DB_BASE_PATH', './') + 'keypad.db')
    conn = None
    try:
        conn = db_connect()
        c = conn.cursor()
        # noinspection SqlNoDataSourceInspection
        c.execute('''
          CREATE TABLE users (
            name TEXT PRIMARY KEY,
            code INTEGER NOT NULL
          )
        ''')
        c.execute('''
          CREATE TABLE permissions (
            name        TEXT NOT NULL,
            keypad_id   TEXT NOT NULL,
            enabled     INTEGER DEFAULT 1,
            use_timeout INTEGER DEFAULT 0,
            not_before  timestamp,
            not_after   timestamp,
            PRIMARY KEY (name, keypad_id)
          )
        ''')
        conn.commit()
    except sqlite3.Error, e:
        print 'Error - %s' % e.args[0]
    finally:
        if conn:
            conn.close()
        print "Done."

def add_user(name, code, force=True):
    name = name.lower()
    code = int(code)
    print 'Adding user %s...' % name
    conn = None
    try:
        conn = db_connect()
        c = conn.cursor()
        if force:
            c.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', (name, code))
        else:
            c.execute('INSERT INTO users VALUES (?, ?)', (name, code))
        conn.commit()
    except sqlite3.Error, e:
        print 'Error - %s' % e.args[0]
    finally:
        if conn:
            conn.close()
    print 'Done.'

def add_permissions(name, keypad_id, not_before=None, not_after=None, force=True):
    name = name.lower()
    keypad_id = keypad_id.lower()
    print 'Adding permissions for %s:' % name
    conn = None
    try:
        conn = db_connect()
        c = conn.cursor()

        c.execute('SELECT COUNT(*) FROM users WHERE name=?', (name,))
        count = c.fetchone()
        if count[0] != 1:
            print 'Error - user %s not known. Permissions not added.' % name
            return

        if keypad_id not in KEYPAD_IDS:
            print "Error - Invalid keypad ID \'%s\'.  Permissions not added." % keypad_id
            return
        record = (name, keypad_id, 1, 0, not_before, not_after)
        if force:
            c.execute('INSERT OR REPLACE INTO permissions VALUES (?, ?, ?, ?, ?)', record)
        else:
            c.execute('INSERT INTO permissions VALUES (?, ?, ?, ?, ?)', record)
        conn.commit()
    except sqlite3.Error, e:
        print 'Error - %s' % e.args[0]
    finally:
        if conn:
            conn.close()
            print 'Done.'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Manage the keypad controller database.'
    )
    parser.add_argument(
        'command',
        choices=['create', 'add'],
        help='The operation to be performed'
    )
    parser.add_argument(
        'cmdargs',
        nargs=argparse.REMAINDER,
        help='The data for the operations'
    )
    args = parser.parse_args()
    main(args)

