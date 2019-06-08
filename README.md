#Sparkify ETL , S3 to Redshift

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
