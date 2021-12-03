from sklearn import preprocessing
from sklearn import pipeline
from sklearn import svm
from sklearn import model_selection
import os
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, f1_score, roc_curve, auc
import imblearn
import numpy as np
import photos.model_utils as model_utils


class TrainModel:
    def __init__(self, rds_info):
        raw_data = load_data(rds_info)
        data, data_split = raw_2_sample(raw_data)
        self.x = np.array([each.feature for each in data])
        self.x_sift = np.array([each.sift for each in data_split])
        self.x_color_gist = np.array([each.color_gist for each in data_split])
        self.x_color_moment = np.array([each.color_moment for each in data_split])
        self.y_artist = np.array([each.y_artist for each in data])
        self.y_genre = np.array([each.y_genre for each in data])
        self.y_style = np.array([each.y_style for each in data])
        self.s3_session = S3ModelSession()

    # def train_split_model(self, y, local_model_path, model_name):

    def train_model(self, x, y, local_model_path, model_name):
        clf = pipeline.Pipeline([
            ('scaler', preprocessing.StandardScaler()),
            ('svm', svm.SVC(kernel='rbf'))]
        )
        param = {
            "svm__C": [0.1, 1, 10],
            # "svm__gamma": [0.01, 0.05, 0.1]
        }
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
        # oversample = imblearn.over_sampling.SMOTE()
        # X_train, y_train = oversample.fit_resample(X_train, y_train)
        grid = model_selection.GridSearchCV(clf, param_grid=param, cv=5, scoring="accuracy")
        grid.fit(X_train, y_train)
        print("best_score: %.3f\n" % grid.best_score_)
        best_model = grid.best_estimator_.fit(X_train, y_train)
        pred = best_model.predict(X_test)
        confusion_matrix_ = confusion_matrix(y_test, pred)
        print(confusion_matrix_)
        print(classification_report(y_test, pred))
        self.s3_session.upload_model(best_model, local_model_path, model_name)

    def create_model(self, task="genre", local_model_path=None):
        print("create model for task %s\n" % task)
        model_name = "%s_model.jl" % task
        self.train_model(self.x, eval("self.y_%s" % task), local_model_path, model_name)

    def create_metric_model(self, task="genre", local_model_path=None):
        print("create metric model for task %s\n" % task)
        model_name = "%s_metrix_model.jl" % task
        self.train_model(self.x, eval("self.y_%s" % task), local_model_path, model_name)


class PredictModel(object):
    def __init__(self, rds_info, local_model_path=None):
        self.rds_info = rds_info
        self.local_model_path = local_model_path
        self.tasks = ("genre", "artist", "style")
        self.models = {}
        self.s3_session = model_utils.S3ModelSession()

    def init_model(self, task):
        """task: genre/artist/style"""
        model_name = "%s_model.jl" % task
        self.models[task] = self.s3_session.download_model(model_name, self.local_model_path)

    def predict(self, task, name):
        """task: genre/artist/style"""
        if task not in self.models:
            self.init_model(task)
        model = self.models[task]
        raw_data = model_utils.load_pred_data(self.rds_info, name)
        feature = np.array(model_utils.raw_2_sample(raw_data, train=False)[0].feature).reshape(1, -1)
        pred = model.predict(feature)[0]
        return pred

'''
rds_info = {
            'host': "wikiartdb.cv8worynfzsx.us-west-1.rds.amazonaws.com",
            'user': "admin",
            'password': "wikiartdb",
            'db': "wikiart",
            'port': 3306
}
name = 'Nature_2.jpg'
extract_cmd = '/Users/kw/PycharmProjects/FinalProject2/museum/spark-3.1.2-bin-hadoop3.2/bin/spark-submit /Users/kw/Desktop/Study/2021Fall/DSCI551/Final_Project/project/Codes/spark_feature_extraction_predict/extract_feature.py ' + name
os.system(extract_cmd)
predict_model = PredictModel(rds_info = rds_info)
print(predict_model.predict("genre", name))
'''