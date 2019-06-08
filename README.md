# Sparkify ETL , S3 to Redshift

This is just me practicing copying data from s3 files into my redshift tables. I try to choose
a clever distribution strategy and I test it against redshifts default distribution strategy. 
You can test it yourself with the python notebook included.

## Getting Started

Fill in the dwh.cfg file with you aws and redshift credentials the IAM role needs to be role that allows 
redshift read access to S3. The S3 buckets are as is. The database credentials shoildbe changed to match your
instance.

```ini
[CLUSTER]
HOST=cluster.endpoint.us-west-2.redshift.amazonaws.com
DB_NAME=dbname
DB_USER=dbhuser
DB_PASSWORD=password
DB_PORT=5439


[IAM_ROLE]
ARN='arn:aws:iam::0000000000:role/rolename'

[S3]
LOG_DATA='s3://udacity-dend/log_data/'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data/'

[AWS]
KEY=key
SECRET=secret key

[DWH]
DWH_CLUSTER_TYPE=multi-node
DWH_NUM_NODES=4
DWH_NODE_TYPE=dc2.large
DWH_IAM_ROLE_NAME=dwhRole
DWH_CLUSTER_IDENTIFIER=dwhCluster
DWH_DB=dbname
DWH_DB_USER=dbhuser
DWH_DB_PASSWORD=password
DWH_PORT=5439
```

# Run the Data Pipeline
Make sure you are in the project directory and run the following commands in terminal
```python 
python setup.py
python etl.py
python create_tables.py
python analytics_test.py
```

# Schema Justifications
So the schema for this tables.

### staging_events
So this is the staging table that we use to copy the event log data into redshift.
Even though this is just a staging table, I thought it would be good to use to distribute
the data on artist name key.

I did this because later on when inserting from staging tables into songplays table, we have to join staging_events on
staging_songs so it would be good if we can store relevant data of staging events and staging songs on the same nodes. 

```python
staging_events_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_events
        (event_key    int identity(0,1),
         artist       varchar distkey sortkey,
         auth            varchar,
         first_name      varchar,
         gender          varchar,
         session_item    int,
         last_name       varchar,
         length          numeric(10,5),
         level           varchar,
         location        varchar,
         method          varchar,
         page            varchar,
         registration    varchar,
         session_id      int,
         song            varchar,
         status          int,
         ts              timestamp,
         user_agent      varchar,
         user_id         varchar
        ) diststyle key;
""")
```

### staging_songs
This is another staging table that we use to copy song data from s3. I use the distribution by key method on artist name
to keep the relevant data of staging tables on the same node.

```python 
staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs
        (artist_id           varchar,
         artist_latitude    numeric(10,5),
         artist_location     varchar,
         artist_longitude    numeric(10,5),
         artist_name         varchar  distkey sortkey,
         duration            numeric(10,5),
         num_songs            int,
         song_id             varchar,
         title               varchar,
         year smallint
        ) diststyle key;
""")
````
### songplays
There were only around 300 mathces between event log data and our song data from s3. Therefore the best
thing to do here would be to just distribute the data across all nodes as the storage cost would be low
and the effeciency for wuerying would be high.


```python
songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays 
        (
         start_time       timestamp NOT NULL          ,
         user_id          varchar(20) NOT NULL,
         level            text NOT NULL,
         song_id          varchar(20) NOT NULL,
         artist_id        varchar(20) NOT NULL,
         session_id       integer NOT NULL,
         location         text NOT NULL,
         user_agent       text NOT NULL
         ) diststyle all;
""")
```

### user
There were only 97 users or something like that so same reasonging as above for distribution style all.

```python
user_table_create = ("""
  CREATE TABLE IF NOT EXISTS users
        (user_id varchar(20) NOT NULL,
         first_name text NOT NULL,
         last_name text NOT NULL,
         gender text NOT NULL,
         level text NOT NULL
        ) diststyle all;
""")
```

### songs and artists
There were many songs that we imported into our table to many for diststyle all. So I looked at what other 
tables I would likey be joining with and saw what keys they might have in common. I noticed that artist_id was 
present in the songs table and artist table and a lot of analytical queries might want to
just join artists on song table. 

However I must note that it doesnt really matter since we are using diststyle all on the fact table, due to its
small size most queries will just be joining the fact tables on our dimension tables and our fact table exists on
all nodes...

```python
song_table_create = ("""
  CREATE TABLE IF NOT EXISTS songs
        (song_id varchar(20),
         title text,
         artist_id varchar(20) distkey sortkey,
         year smallint,
         duration numeric(10,5)
        )diststyle key;
""")

artist_table_create = ("""
   CREATE TABLE IF NOT EXISTS artists
        (artist_id varchar(20) NOT NULL distkey sortkey,
         name text NOT NULL,
         location text ,
         latitude numeric(10,5),
         longitude numeric(10,5)
        ) diststyle key;
""")

```



