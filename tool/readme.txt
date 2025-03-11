~~ SQLのメモ ~~

サービス開始
$ sudo service mysql start

サービス停止
$ sudo service mysql stop

状態確認
$ sudo service mysql status

SQL接続
$ sudo mysql -u root -ppassword

SQL切断
mysql> exit

参考：
https://moewe-net.com/database/mysql-install-on-ubuntu

【errlocatorを動作させるために必要なもの】
pandas numpy pymysql
mysql
setup.pyにsqlの情報入力

起動
$ python3 ./errlocator path/to/file.py

プロジェクトの実行に引数が必要な場合，引数の前に"-a"を追加
$ python3 ./errlocator path/to/file.py -a arg
引数が複数の場合
$ python3 ./errlocator path/to/file.py -a arg1 arg2