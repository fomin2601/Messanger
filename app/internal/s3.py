import boto3

MAX_FILE_SIZE_MB = 100


class S3Handler:
    def __init__(self):
        self.s3_base_url = 'https://storage.yandexcloud.net/'
        self.bucket = 'messenger-fomin2601'

    def upload_file_to_s3(self, file: bytes, file_id: str) -> bool:
        s3_session = self._get_session()

        if len(file) > MAX_FILE_SIZE_MB * 1024 * 1024:
            return False

        try:
            s3_session.put_object(Body=file, Bucket=self.bucket, Key=f'messenger/{file_id}')
            return True
        except:
            return False

    def download_file_from_s3(self, file_id: str) -> bytes:
        s3_session = self._get_session()
        object_response = s3_session.get_object(Bucket=self.bucket, Key=f'messenger/{file_id}')
        return object_response['Body'].read()

    def _get_session(self):
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            endpoint_url=self.s3_base_url
        )

        return s3


s3_handler = S3Handler()
