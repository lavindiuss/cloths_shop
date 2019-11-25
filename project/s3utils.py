# import os
from storages.backends.s3boto import S3BotoStorage
# os.environ['S3_USE_SIGV4'] = 'True'
#from IKproject.settings import *




class S3Storage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        #kwargs['custom_domain'] = settings.AWS_CLOUDFRONT_DOMAIN
        super(MediaStorage, self).__init__(*args, **kwargs)

    @property
    def connection(self):
        if self._connection is None:
            self._connection = self.connection_class(
                self.access_key, self.secret_key,
                calling_format=self.calling_format, host='s3.eu-central-1.amazonaws.com')
        return self._connection


StaticS3BotoStorage = lambda: S3BotoStorage(location='daresny/static')
MediaS3BotoStorage = lambda: S3BotoStorage(location='Swapit/media')
