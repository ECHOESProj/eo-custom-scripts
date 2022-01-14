#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from os.path import join
import boto3
from botocore.exceptions import ClientError

class ObjectStoreInterface:
    """Read and write to S3"""

    def __init__(self, platform):
        self.platform = platform
        self.bucketname = platform.bucket
        self.endpoints = {'external': self.platform.endpoint_url_local,
                          'local': self.platform.endpoint_url_ext}
        self.credentials = dict(region_name=self.platform.region_name,
                                aws_access_key_id=self.platform.aws_access_key_id,
                                aws_secret_access_key=self.platform.aws_secret_access_key,
                                config=self.platform.config)
        self.resource_loc = self.resource(loc_ext='local')
        self.resource_ext = self.resource(loc_ext='external')
        self.client_loc = self.client(loc_ext='local')
        self.client_ext = self.client(loc_ext='external')

    def resource(self, loc_ext='local'):
        return boto3.resource('s3', endpoint_url=self.endpoints[loc_ext], **self.credentials)

    def client(self, loc_ext='local'):
        return boto3.client('s3', endpoint_url=self.endpoints[loc_ext], **self.credentials)


class ReadWriteData(ObjectStoreInterface):
    """"Read and write to Zarr on S3"""

    def __init__(self, platform, key_name):
        super().__init__(platform)
        self.s3 = platform
        self.key_name = key_name
        self.obj_name = join(self.bucketname, self.key_name)

    def upload_file(self, local_fname, store_name):
        try:
            try:
                self.client_loc.upload_file(local_fname, self.bucketname, store_name)
            except TypeError:
                self.client_loc.upload_fileobj(local_fname, self.bucketname, store_name)
            return self.bucketname, store_name
        except ClientError as e:
            print(e)

    def check_exists(self, object_name):
        return self.client_loc.list_objects_v2(Bucket=self.bucketname, Prefix=object_name)['Contents'][0]['Key'] == object_name

    def remove_temp(self):
        """Remove temporary object directory"""
        bucket = self.resource_loc.Bucket(self.bucketname)
        bucket.objects.filter(Prefix="_test").delete()


