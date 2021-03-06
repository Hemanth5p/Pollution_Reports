# Copyright (c) 2021 CodeOps Technologies LLP. All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#   - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   - Neither the name of CodeOps or the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from io import BytesIO

import boto3
import pandas as pd


class S3Connector:

    def __init__(self, region='ap-south-1'):
        """
        this is constructor which creates a client for s3
        :param region: string representing location code for s3 bucket by default it is mumbai 'ap-south-1'
        """
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)

    def get_existing_buckets_list(self):
        """
        this method get the existing buckets present in the s3
        :return: list representing the names of the s3 buckets
        """
        details_of_buckets = self.s3.list_buckets()['Buckets']
        list_of_buckets = [bucket["Name"] for bucket in details_of_buckets]
        return list_of_buckets

    def create_s3_bucket(self, bucket_name):
        """
        this method creates the new bucket in the s3
        :param bucket_name: string representing the new bucket name
        """
        location = {'LocationConstraint': self.region}
        self.s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

    def upload_file_to_bucket(self, filename, bucket_name, object_name=None):
        """
        this method uploads the files to the s3 bucket
        :param filename: string represents file path or name which to upload
        :param bucket_name: string represents bucket name in which going to store
        :param object_name: string represents name with which going to store in bucket
        """
        if object_name is None:
            object_name = os.path.basename(filename)

        with open(filename, "rb") as file:
            self.s3.upload_fileobj(file, bucket_name, object_name)

    def get_list_of_bucket_objects(self, bucket_name):
        """
        this method gets objects present in the s3 bucket
        :param bucket_name: string representing the bucket name in s3
        :return: list representing the objects present in the bucket
        """
        bucket_objs = [obj['Key'] for obj in self.s3.list_objects(Bucket=bucket_name)['Contents']]
        return bucket_objs

    def download_file_from_bucket(self, object_name, bucket_name, filename):
        """
        this method downloads the objects from the bucket
        :param object_name: string representing the name of the object in the bucket
        :param bucket_name: string representing the bucket name
        :param filename: string representing the file name with which to save
        """
        with open(filename, 'wb') as file:
            self.s3.download_fileobj(bucket_name, object_name, file)

    def read_bucket_object(self, bucket_name, object_name):
        """
        this method reads the excel object of the buckets and creates dataframe
        :param bucket_name: string representing the name of the bucket
        :param object_name: string representing the object name in the bucket
        :return: dataframe created by read the excel object
        """
        obj = self.s3.get_object(Bucket=bucket_name, Key=object_name)
        file = BytesIO(obj['Body'].read())
        df = pd.read_excel(file)
        return df


if __name__ == '__main__':
    s3 = S3Connector()
    x = s3.read_bucket_object(bucket_name='pollutionreport', object_name='AirQuality-India-Realtime.xlsx')
    print(x)
