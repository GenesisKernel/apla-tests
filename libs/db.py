import random
import string
import requests
import psycopg2
import json
import time

from collections import Counter
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


class Db(object):
        
    def compare_keys_cout(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT key_id FROM block_chain Order by id DESC LIMIT 10")
        keys = cursor.fetchall()
        firstKey = keys[1]
        secondKey = ""
        for key in keys:
            if key != firstKey:
                secondKey = key
        if secondKey == "":
            return False
        else:
            keysCounter = Counter(keys)
            firstKeyCount = keysCounter[firstKey]
            secondKeyCount = keysCounter[secondKey]
            compare = firstKeyCount - secondKeyCount
            if (compare > 1) | (compare < -1):
                return False
            else:
                return True

    def compare_node_positions(dbHost, dbName, login, password, maxBlockId, nodes):
        count_rec = nodes * 3 + nodes
        minBlock = maxBlockId - count_rec + 1
        request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
            minBlock) + " AND id<" + str(maxBlockId) + "GROUP BY node_position"
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        positions = cursor.fetchall()
        countBlocks = round(count_rec / nodes / 10 * 7)
        if len(positions) < nodes:
            print("One of nodes doesn't generate blocks" + str(positions))
            return False
        i = 0
        while i < len(positions):
            if positions[i][1] < countBlocks - 1:
                print("Node " + str(i) + " generated " + str(positions[i][1]) + " blocks:" + str(positions))
                return False
            i = i + 1
        return True

    def check_for_missing_node(dbHost, dbName, login, password, minBlockId, maxBlockId):
        request = "SELECT node_position FROM block_chain WHERE id>=" + str(minBlockId) + " AND id<=" + str(maxBlockId)
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        positions = cursor.fetchall()
        i = 0
        while i < len(positions):
            if positions[i][0] == 2:
                return False
            i = i + 1
        return True

    def isCountTxInBlock(dbHost, dbName, login, password, maxBlockId, countTx):
        minBlock = maxBlockId - 3
        request = "SELECT id, tx FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        tx = cursor.fetchall()
        i = 0
        while i < len(tx):
            if tx[i][1] > countTx:
                print("Block " + str(tx[i][0]) + " contains " + \
                      str(tx[i][1]) + " transactions")
                return False
            i = i + 1
        return True
    
    def get_count_records_block_chain(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT count(*) FROM \"block_chain\"")
        return cursor.fetchall()

    def get_ten_items(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM block_chain Order by id DESC LIMIT 10")
        keys = cursor.fetchall()
        return keys

    def getEcosysTables(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(
            "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'")
        tables = cursor.fetchall()
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getEcosysTablesById(dbHost, dbName, login, password, ecosystemID):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(
            "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '" + str(
                ecosystemID) + "_%'")
        tables = cursor.fetchall()
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getCountTable(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT count(*) FROM \"" + table + "\"")
        return cursor.fetchall()[0][0]

    def getMaxIdFromTable(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT MAX(id) FROM \"" + table + "\"")
        return cursor.fetchall()[0][0]

    def executeSQL(dbHost, dbName, login, password, query):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def getObjectIdByName(dbHost, dbName, login, password, table, name):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT id FROM \"" + table + "\" WHERE name = '" + str(name) + "'")
        print(cursor.fetchall())
        return cursor.fetchall()[0][0]

    def getFounderId(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'")
        return cursor.fetchall()[0][0]

    def getSystemParameterValue(dbHost, dbName, login, password, name):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_system_parameters\" WHERE name = '" + name + "'")
        return cursor.fetchall()[0][0]

    def getExportAppData(dbHost, dbName, login, password, app_id, member_id):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
            app_id) + " AND member_id = " + str(member_id))
        return cursor.fetchall()[0][0]

    def getImportAppData(dbHost, dbName, login, password, member_id):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id))
        return cursor.fetchall()[0][0]

    def getCountDBObjects(dbHost, dbName, login, password):
        tablesCount = {}
        tables = self.getEcosysTables(dbHost, dbName, login, password)
        for table in tables:
            tablesCount[table[2:]] = self.getCountTable(dbHost, dbName, login, password, table)
        return tablesCount

    def getTableColumnNames(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
                table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
        cursor.execute(query)
        col = {}
        col = cursor.fetchall()
        return col

    def getUserTableState(dbHost, dbName, login, password, userTable):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM \"" + userTable + "\"")
        res = cursor.fetchall()
        col = self.getTableColumnNames(dbHost, dbName, login, password, userTable)
        table = {}
        for i in range(len(col)):
            table[col[i][0]] = res[0][i]
        return table

    def getUserTokenAmounts(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" ORDER BY amount")
        amounts = cursor.fetchall()
        return amounts

    def get_blockchain_hash(dbHost, dbName, login, password, maxBlockId):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
            maxBlockId) + " ORDER BY id) AS t"
        cursor.execute(request)
        hash = cursor.fetchall()
        return hash

    def get_system_parameter(dbHost, dbName, login, password, parameter):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select value from \"1_system_parameters\" WHERE name='" + parameter + "'")
        value = cursor.fetchall()
        return value[0][0]

    def get_commission_wallet(dbHost, dbName, login, password, ecosId):
        request = "select value from \"1_system_parameters\" where name='commission_wallet'"
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        wallets = cursor.fetchall()
        wallet = json.loads(wallets[0][0])[0][1]
        return wallet

    def get_balance_from_db(dbHost, dbName, login, password, keyId):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE id=" + keyId)
        amount = cursor.fetchall()
        balance = amount[0][0]
        return balance

    def get_balance_from_db_by_pub(dbHost, dbName, login, password, pub):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE pub='\\x" + pub + "'")
        amount = cursor.fetchall()
        return amount[0][0]

    def is_wallet_created(dbHost, dbName, login, password, pub):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE id='" + pub + "'")
        wallet = cursor.fetchall()
        if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
            return True
        else:
            return False

    def get_block_gen_node(dbHost, dbName, login, password, block):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select node_position from \"block_chain\" WHERE id=" + block)
        nodes = cursor.fetchall()
        return nodes[0][0]

    def isCommissionInHistory(dbHost, dbName, login, password, idFrom, idTo, summ):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select * from \"1_history\" WHERE sender_id=" + idFrom + \
                       " AND recipient_id=" + str(idTo) + " AND amount=" + str(summ))
        rec = cursor.fetchall()
        if len(rec) > 0:
            return True
        else:
            return False