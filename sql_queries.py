import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

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

user_table_create = ("""
  CREATE TABLE IF NOT EXISTS users
        (user_id varchar(20) NOT NULL,
         first_name text NOT NULL,
         last_name text NOT NULL,
         gender text NOT NULL,
         level text NOT NULL
        ) diststyle all;
""")

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

time_table_create = ("""
  CREATE TABLE IF NOT EXISTS time
        (start_time timestamp NOT NULL,
         hour smallint NOT NULL,
         day smallint NOT NULL,
         week smallint NOT NULL,
         month smallint NOT NULL,
         year smallint NOT NULL,
         weekday smallint NOT NULL
        ) diststyle all;

""")

# STAGING TABLES

staging_events_copy = ("""
COPY {} 
FROM 's3://udacity-dend/log_data' 
IAM_ROLE {} 
REGION 'us-west-2' 
FORMAT AS JSON {}
TIMEFORMAT as 'epochmillisecs'
;
""").format('staging_events', config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
COPY {}
FROM 's3://udacity-dend/song_data' 
IAM_ROLE {}
JSON 'auto';
""").format('staging_songs', config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
insert into songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
select e.ts, e.user_id, e.level, s.song_id, s.artist_id, e.session_id, e.location, e.user_agent
from staging_events e
join staging_songs s
on e.song = s.title and e.artist = s.artist_name
where e.page = 'NextSong'
""")

# To ensure most up to date level status of user, we select the staging table on itself, identify duplicates
# and return the row with the higher (identity) event_key indicating it was the last log received with up to date data.
user_table_insert = ("""
insert into users (user_id, first_name, last_name, gender, level)
select user_id, first_name, last_name, gender, level 
from staging_events as t1
where t1.event_key = (select t2.event_key
                      from staging_events as t2
                      where t2.user_id = t1.user_id
                      order by t2.event_key desc
                      limit 1)
and t1.auth = 'Logged In'
""")

song_table_insert = ("""
insert into songs (song_id, title, artist_id, year, duration)
select distinct song_id, title, artist_id, year, duration
from staging_songs
""")

artist_table_insert = ("""
insert into artists (artist_id, name, location, latitude, longitude)
select distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
from staging_songs
""")

time_table_insert = ("""
insert into time (start_time, hour, day, week, month, year, weekday)
select ts as start_time, extract(hour from ts) as hour, extract(day from ts) as day , extract(week from ts) as week, extract(month from ts) as month, extract(year from ts) as year, extract(dow from ts) as weekday
from staging_events
""")

# ANALYTICAL QUERIES

# oneDim
popular_songs = """
set enable_result_cache_for_session to off;
select s.title, count(p.song_id) as plays,s.year
from songs s, songplays p
where s.song_id = p.song_id
group by  s.title, s.year
order by plays desc
limit 5;
"""

busiest_wday = """
set enable_result_cache_for_session to off;
select count(t.weekday) as count_weekday, t.weekday
from songplays s, time t
where s.start_time = t.start_time
group by t.weekday 
limit 3;
"""

# OneDim_Slice
busiest_hour = """
set enable_result_cache_for_session to off;
select count(t.hour) as plays, t.hour as hour
from songplays s, time t
where s.start_time = t.start_time
and t.weekday = 6
group by t.hour
order by plays desc
limit 5;
"""

# No_Dim Slice
busiest_state_friday = """
set enable_result_cache_for_session to off;
select right(location, 2) as state, count(state) as plays
from songplays s, time t
where s.start_time = t.start_time and t.weekday = 5
group by state
order by plays desc
limit 5;
"""

avg_songs_per_session = """
set enable_result_cache_for_session to off;
select avg(songs_played)
from (
select count(session_id) as songs_played
from songplays p, songs s
where s.song_id = p.song_id
group by p.session_id
) as avg_songs_played;
"""

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create,
                        user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop,
                      song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert,
                        time_table_insert]
analytical_queries = [popular_songs, busiest_wday, busiest_hour, busiest_state_friday, avg_songs_per_session]