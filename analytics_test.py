import configparser
import psycopg2
from sql_queries import analytical_queries
import matplotlib.pyplot as plt
from time import time
import pandas as pd


name_list = ['popular_songs', 'busiest_wday', 'busiest_hour', 'busiest_state_friday', 'avg_songs_per_session']


def query_tables(cur, conn, queries, names):
    """
         Takes pscopyg2 connection and our analytical_queries
         and prints results of each query for testing

         Parameters:
         cur: psycopg2 cursor
         con: psycopg2 connection
         queries: the projects analytical_queries
         names: the names of our queries for identification purposes  during testing

      """
    queryTimes = []
    loading = list(zip(queries, names))
    for query, name in loading:
        print("======= QUERYING: ** {} **  =======".format(name))
        print(query)

        t0 = time()
        cur.execute(query)
        conn.commit()
        result = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        queryTime = time() - t0
        queryTimes.append(queryTime)
        print(result)
    return pd.DataFrame({"query": names, "querytime_": queryTimes}).set_index('query')


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    stats = query_tables(cur, conn, analytical_queries, name_list)
    stats.plot.bar()
    plt.show()
    conn.close()


if __name__ == "__main__":
    main()