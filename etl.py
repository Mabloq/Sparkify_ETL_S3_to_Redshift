import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn, copies):
    """
       Takes pscopyg2 connection and our copy tables queries
       loads up our staging tables with data from s3

       Parameters:
       cur: psycopg2 cursor
       con: psycopg2 connection
       copies: the projects copy_table_queries

    """
    for query in copies:
        print('=====================================')
        print('load staging', query)
        print('=====================================')
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn, inserts):
    """
         Takes pscopyg2 connection and insert statements
         and inserts data from our staging tables into our final tables

         Parameters:
         cur: psycopg2 cursor
         con: psycopg2 connection
         inserts: the projects insert_table_queries

      """
    for query in inserts:
        print('=====================================')
        print('insert', query)
        print('=====================================')
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    load_staging_tables(cur, conn, copy_table_queries)
    insert_tables(cur, conn, insert_table_queries)

    conn.close()


if __name__ == "__main__":
    main()
