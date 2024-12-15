# Deploy


Clone project to your machine, create virtual environment

*python -m venv venv*

Install python packages

*pip install -r requrements.txt*

Create bucket on Yandex Cloud

https://console.yandex.cloud/

Replace bucket's name in app/internal/s3.py:

*S3Handler.bucket = "your backet name"*

For Windows:

On your machine, in user's folder %USERPROFILE% create folder ".aws" with two files:

*"config":*

*[default]*

  *region=ru-central1*
  
  *endpoint_url=https://storage.yandexcloud.net*

*"credentials":*
  *aws_access_key_id = "your access secret key id"*
  *aws_secret_access_key = "your access secret key"*
