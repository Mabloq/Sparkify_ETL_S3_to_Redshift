from setuptools import setup, find_packages

setup(
    name='Sparkify_ETL_S3_TO_REDSHIFT',
    version='1.0',
    packages=find_packages,
    url='https://github.com/Mabloq/Sparkify_ETL_S3_to_Redshift.git',
    license='MIT',
    author='matthewarcila',
    author_email='',
    description='ETL from s3 to Redshift with performance testing on distribution strategies'
)
