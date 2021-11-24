from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List of all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns precipitation data from the most recent 12 months"""
    session= Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    one_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measurement.date, func.avg(measurement.prcp)).filter(measurement.date >= one_year).\
    group_by(measurement.date).all()
    previous_year=[]
    for date, prcp in results:
        base_dict={}
        base_dict['date'] = date
        base_dict['prcp'] = prcp
        previous_year.append(base_dict)
    session.close()
    
    return jsonify(previous_year)

@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of all stations in the Station table"""
    session= Session(engine)
    result2 = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    station_list=[]
    for station, count in result2:
        station_list.append(station)
    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a dictionary of all temperatures from the last year from the most active station"""
    session= Session(engine)

    result2 = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    topstation = result2[0][0]

    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    one_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    bestresults = session.query(measurement.date, measurement.tobs).filter(measurement.station == topstation).\
    filter(measurement.date >= one_year).all()

    stationtemps=[]
    for date, temp in bestresults:
        base_dict={}
        base_dict['date']=date
        base_dict['temp']=temp
        stationtemps.append(base_dict)
    session.close()

    return jsonify(stationtemps)

@app.route('/api/v1.0/<start>')
def temp_start(start):
    session=Session(engine)
    result = session.query(func.avg(measurement.tobs),func.max(measurement.tobs),func.min(measurement.tobs).\
        filter(measurement.date >= start))
    tobs_list= []
    for avg, max, min in result:
        base_dict = {}
        base_dict['TAVG'] = float(avg)
        base_dict['TMAX'] = float(max)
        base_dict['TMIN'] = float(min)
        tobs_list.append(base_dict)
    
    session.close()

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>/<end>')
def temp_startend(start, end):
    session=Session(engine)
    
    result = session.query(func.avg(measurement.tobs),func.max(measurement.tobs),func.min(measurement.tobs).\
        filter(measurement.date >= start).filter(measurement.date <= end))
    tobs_list= []
    for avg, max, min in result:
        base_dict = {}
        base_dict['TAVG'] = float(avg)
        base_dict['TMAX'] = float(max)
        base_dict['TMIN'] = float(min)
        tobs_list.append(base_dict)
    session.close()

    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)