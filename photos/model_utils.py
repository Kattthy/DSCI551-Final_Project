import os
import joblib
import tempfile
import pymysql
import json
from collections import namedtuple
from boto3.session import Session

Sample = namedtuple("Sample", "feature y_artist y_genre y_style")
Sample_split = namedtuple("Sample", "sift color_moment color_gist y_artist y_genre y_style")
def raw_2_sample(raw_data, train=True):

    def record_2_sample(record):
        feature = []
        feature1 = json.loads(record[0])
        feature2 = json.loads(record[1])
        feature3 = json.loads(record[2])
        feature = feature1 + feature2 + feature3
        print('length of feature:',len(feature))
        if len(feature) == 5065:
            if train:
                sample = Sample(feature, record[3], record[4], record[5])
            else:
                sample = Sample(feature, None, None, None)
            return sample
        else:
            return

    data = []
    for record in raw_data:
        sample = record_2_sample(record)
        if sample:
            data.append(sample)
    print('length of data:',len(data))
    return data


def load_pred_data(rds_info, name):
    db = pymysql.connect(**rds_info)
    cur = db.cursor()
    sql = "select " \
          "sift, color_moments, color_gist " \
          "from photos_predict_features " \
          "where image_id='%s';" % name
    try:
        cur.execute(sql)
        results = cur.fetchall()
        return results
    except Exception as e:
        print(e)
    finally:
        db.close()


def load_data(rds_info):
    db = pymysql.connect(**rds_info)
    cur = db.cursor()
    sql = """
            select
            f.sift, f.color_moments, f.color_gist,
            p.artist_id, p.genre_id, p.style_id from photos_features as f
            left join photos_picture as p on f.image_id = p.name
        """
    try:
        cur.execute(sql)
        results = cur.fetchall()
        return results
    except Exception as e:
        print(e)
    finally:
        db.close()


class S3ModelSession:
    def __init__(self):
        AWSAccessKeyId="AKIA3UZI2QOSQSCCDTM4"
        AWSSecretKey="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"
        self.session = Session(
            aws_access_key_id=AWSAccessKeyId,
            aws_secret_access_key=AWSSecretKey,
            region_name='us-east-2')
        self.s3 = self.session.resource('s3')
        self.client = self.session.client('s3')
        self.bucket = "acrawdata"

    def upload_model(self, model, local_model_path, model_name):
        model_name = os.path.join("models", model_name)
        f = open(local_model_path, "wb") if local_model_path else tempfile.TemporaryFile()
        joblib.dump(model, f)
        f.seek(0)
        self.client.put_object(Body=f.read(), Bucket=self.bucket, Key=model_name)
        f.close()

    def download_model(self, model_name, local_model_path):
        model_name = os.path.join("models", model_name)
        f = open(local_model_path, "wb") if local_model_path else tempfile.TemporaryFile()
        self.client.download_fileobj(Fileobj=f, Bucket=self.bucket, Key=model_name)
        f.seek(0)
        model = joblib.load(f)
        f.close()
        return model