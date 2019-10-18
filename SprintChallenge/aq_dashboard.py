"""OpenAQ Air Quality Dashboard with Flask"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)

api = openaq.OpenAQ()
status, body = api.measurements(city="Los Angeles", parameter="pm25")

@app.route("/")
def root():
    """Base View"""
    return str(Record.query.filter(Record.value >10).all())
    
def get_data():
    """pulling results into a list of tuples and returning as a string"""
    data = []
    for i in list(range(len(body['results']))):
        data.append((body['results'][i]['date']['utc'], body['results'][i]['value']))
    return data

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Integer, nullable=False)

    def __repr__(self):
        return '< Time: {} , Particulate matter: {} >'.format(self.datetime, self.value)

@app.route("/refresh")
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    results = get_data()
    id = 0

    for i in list(range(len(results))):
        id = id + 1
        data1 = Record(id=id,
                    datetime = results[i][0],
                    value = results[i][1])
        DB.session.add(data1)
        DB.session.commit()

    return 'Data Refreshed!'