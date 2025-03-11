import pymysql.cursors, pprint, json

def exist_db_judge(host, user, password):
    # db(errloctor_db)があるか判定
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "SHOW DATABASES"
            cursor.execute(sql)
            dbs = cursor.fetchall()
            cursor.close()

    x = 0
    for i in dbs:
        if i['Database'] == 'errlocator_db':
            x = 1
            break
    # x = 0：不在，x = 1：存在
    return x

def db_setting(host, user, password):
    # データベース初期設定
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "CREATE DATABASE `errlocator_db`"
            cursor.execute(sql)
            cursor.close()

    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # テーブル作成
            sql = "CREATE TABLE `add_values` (`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,`value` varchar(255),`file` varchar(255),`line` int,`column` int)"
            cursor.execute(sql)
            sql = "CREATE TABLE `constants` (`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,`constant` varchar(255),`file` varchar(255),`line` int,`column` int)"
            cursor.execute(sql)
            sql = "CREATE TABLE `formulas` (`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,`formula` varchar(255),`file` varchar(255),`line` int,`column` int)"
            cursor.execute(sql)
            sql = "CREATE TABLE `values` (`id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,`value` varchar(255),`file` varchar(255),`line` int,`column` int)"
            cursor.execute(sql)

        # コミットしてトランザクション実行
        connection.commit()

def insert_values(host, user, password, value, fi, li, col):
    # データベースに接続
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "INSERT INTO `values` (`value`, `file`, `line`, `column`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (value, fi, li, col))

        # コミットしてトランザクション実行
        connection.commit()

def insert_constants(host, user, password, constant, fi, li, col):
    # データベースに接続
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "INSERT INTO `constants` (`constant`, `file`, `line`, `column`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (constant, fi, li, col))

        # コミットしてトランザクション実行
        connection.commit()

def insert_add_values(host, user, password, value, fi, li, col):
    # データベースに接続
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "INSERT INTO `add_values` (`value`, `file`, `line`, `column`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (value, fi, li, col))

        # コミットしてトランザクション実行
        connection.commit()

def insert_formulas(host, user, password, value, fi, li, col):
    # データベースに接続
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # レコードを挿入
            sql = "INSERT INTO `formulas` (`formula`, `file`, `line`, `column`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (value, fi, li, col))

        # コミットしてトランザクション実行
        connection.commit()

def show(host, user, password, table):
    # データベースに接続
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            # データ読み込み
            if table == 0:
                sql = "SELECT * FROM `values`"
            elif table == 1:
                sql = "SELECT * FROM `constants`"
            elif table == 2:
                sql = "SELECT * FROM `add_values`"
            elif table == 3:
                sql = "SELECT * FROM `formulas`"
            cursor.execute(sql)
            result = cursor.fetchall()
            pprint.pprint(result)

def db_delete(host, user, password, table):
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)
            
    with connection:
        with connection.cursor() as cursor:
            # データ削除
            if table == 0:
                sql = "DELETE FROM `values`"
            elif table == 1:
                sql = "DELETE FROM `constants`"
            elif table == 2:
                sql = "DELETE FROM `add_values`"
            elif table == 3:
                sql = "DELETE FROM `formulas`"
            cursor.execute(sql)
            connection.commit()
    
def db_reset(host, user, password, table):
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "SET @i := 0"
            if table == 0:
                sql = "UPDATE `values` SET `id` = (@i := @i + 1)"
                sql = "ALTER TABLE `values` AUTO_INCREMENT = 1"
            elif table == 1:
                sql = "UPDATE `constants` SET `id` = (@i := @i + 1)"
                sql = "ALTER TABLE `constants` AUTO_INCREMENT = 1"
            elif table == 2:
                sql = "UPDATE `add_values` SET `id` = (@i := @i + 1)"
                sql = "ALTER TABLE `add_values` AUTO_INCREMENT = 1"
            elif table == 3:
                sql = "UPDATE `formulas` SET `id` = (@i := @i + 1)"
                sql = "ALTER TABLE `formulas` AUTO_INCREMENT = 1"
            cursor.execute(sql)
            connection.commit()

def delete1_values(host, user, password, value):
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `values` WHERE `value` = %s"
            cursor.execute(sql, (value))
            connection.commit()

def delete1_add_values(host, user, password, value):
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `add_values` WHERE `value` = %s"
            cursor.execute(sql, (value))
            connection.commit()

def exist_values(host, user, password):
# valuesの中にデータが存在するか判定
# x = 1のとき要素あり， x = 0のとき要素なし
    x = 0
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT EXISTS(SELECT * FROM `values` WHERE `id` = %s)"
            n = 0
            for i in range(1, 20):
                n = n + 1
                cursor.execute(sql, (n, ))
                result = cursor.fetchall()
                if 1 in result[0].values():
                    x = 1
                    break
            sql = "SELECT EXISTS(SELECT * FROM `constants` WHERE `id` = %s)"
            n = 0
            for i in range(1, 20):
                n = n + 1
                cursor.execute(sql, (n, ))
                result = cursor.fetchall()
                if 1 in result[0].values():
                    x = 1
                    break
    return x

def exist_add_values(host, user, password):
# valuesの中にデータが存在するか判定
# x = 1のとき要素あり， x = 0のとき要素なし
    x = 0
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                database='errlocator_db',
                                cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT EXISTS(SELECT * FROM `add_values` WHERE `id` = %s)"
            n = 0
            for i in range(1, 20):
                n = n + 1
                cursor.execute(sql, (n, ))
                result = cursor.fetchall()
                if 1 in result[0].values():
                    x = 1
                    break
    return x

def dupli_values(host, user, password):
# 重複要素削除
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `values` WHERE id NOT IN (SELECT min_id from (SELECT MIN(id) AS min_id FROM `values` GROUP BY value) AS tmp);"
            cursor.execute(sql)
            connection.commit()

def dupli_add_values(host, user, password):
# 重複要素削除
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `add_values` WHERE id NOT IN (SELECT min_id from (SELECT MIN(id) AS min_id FROM `add_values` GROUP BY value) AS tmp);"
            cursor.execute(sql)
            connection.commit()

def dupli_formulas(host, user, password):
# 重複要素削除
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)
 
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `formulas` WHERE id NOT IN (SELECT min_id from (SELECT MIN(id) AS min_id FROM `formulas` GROUP BY formula) AS tmp);"
            cursor.execute(sql)
            connection.commit()

# DBの中身をファイルへ変換
def db_to_file(host, user, password, table):
    connection = pymysql.connect(host=host,
                       user=user,
                       password=password,
                       database='errlocator_db',
                       cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            if table == 0:
                sql = "SELECT * FROM `values`"
                cursor.execute(sql)
                result = cursor.fetchall()
                f = open('opt/list/var_list.json', 'w')
                json.dump(result, f, indent = 2)
                f.close()
            elif table == 1:
                sql = "SELECT * FROM `constants`"
                cursor.execute(sql)
                result = cursor.fetchall()
                f = open('opt/list/const_list.json', 'w')
                json.dump(result, f, indent = 2)
                f.close()

# Tableの中身をリストへ格納
def db_to_list(host, user, password, table):
    connection = pymysql.connect(host=host,
                    user=user,
                    password=password,
                    database='errlocator_db',
                    cursorclass=pymysql.cursors.DictCursor)

    lis = []
    with connection:
        with connection.cursor() as cursor:
            if table == 0:
                sql = "SELECT * FROM `values`"
            elif table == 1:
                sql = "SELECT * FROM `constants`"
            elif table == 2:
                sql = "SELECT * FROM `add_values`"
            elif table == 3:
                sql = "SELECT * FROM `formulas`"
            cursor.execute(sql)
            for i in cursor:
                lis.append(str(i))
    
    return lis