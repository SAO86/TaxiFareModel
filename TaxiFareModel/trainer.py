# imports
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from data import get_data, clean_data
from encoders import DistanceTransformer, TimeFeaturesEncoder
from utils import haversine_vectorized, compute_rmse


class Trainer():
    def __init__(self, X, y):
        """
            X: pandas DataFrame
            y: pandas Series
        """
        self.pipeline = None
        self.X = X
        self.y = y

    def set_pipeline(self):
        """defines the pipeline as a class attribute"""
        dist_cols = ['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']
        time_cols = ['pickup_datetime']
        pipe_distance = make_pipeline(DistanceTransformer(), StandardScaler())
        pipe_time = make_pipeline(TimeFeaturesEncoder(time_column='pickup_datetime'), OneHotEncoder(handle_unknown='ignore',sparse=False))
        preproc_pipe = ColumnTransformer([('time', pipe_time, time_cols),
                                        ('distance', pipe_distance, dist_cols)])
        pipe_cols = Pipeline(steps=[('preproc', preproc_pipe),
                                    ('regressor', LinearRegression())])
        self.pipeline = pipe_cols

    def run(self):
        """set and train the pipeline"""
        pipeline = self.set_pipeline()
        self.pipeline.fit(self.X, self.y)

    def evaluate(self, X_test, y_test):
        """evaluates the pipeline on df_test and return the RMSE"""
        y_pred = self.pipeline.predict(X_test)
        rmse = compute_rmse(y_pred, y_test)
        return rmse


if __name__ == "__main__":
    # get data$
    df = get_data(nrows=10_000)
    # clean data
    df = clean_data(df, test=False)
    # set X and y
    X = df.drop(columns='fare_amount')
    y = df['fare_amount']
    # hold out
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # train
    trainer = Trainer(X_train, y_train)
    trainer.run()
    # evaluate
    trainer.evaluate(X_test, y_test)
    print('ok')
