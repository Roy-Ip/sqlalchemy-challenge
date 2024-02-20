# Import the dependencies.
from datetime import datetime, date

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify
import datetime as dt




#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temperatures/yyyy-mm-dd (start date only between 2010-01-01 and 2017-08-23)<br/>"
        f"/api/v1.0/temperatures/yyyy-mm-dd/yyyy-mm-dd (start date and end date between 2010-01-01 and 2017-08-23)"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    last_day = session.query(Measurement.date).order_by(desc(Measurement.date)).first()[0]
    last_day = dt.datetime.strptime(last_day, '%Y-%m-%d').date()
    one_year_ago = last_day - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
   
    precipitation_list = []
    for result in results:
        precipitation_dict = {
            "date": result.date,
            "prcp": result.prcp,
        }
        precipitation_list.append(precipitation_dict)

    session.close()

    return jsonify(precipitation_list)



@app.route("/api/v1.0/stations")
def stations():

    stations_data = session.query(Station).all()

    stations_list = []
    for station in stations_data:
        station_dict = {
            "station": station.station,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation,
        }
        stations_list.append(station_dict)

    session.close()

    return jsonify(stations_list)



@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = 'USC00519281'

    most_recent_date = session.query(Measurement.date).\
        filter(Measurement.station == most_active_station_id).\
        order_by(desc(Measurement.date)).first()

    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()

    twelve_month_ago = most_recent_date - dt.timedelta(days=365)

    temperature_observation = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station_id).\
            filter(Measurement.date >= twelve_month_ago).all()

    tobs_list = []
    for result in temperature_observation:
        tobs_dict = {
                "date": result.date,
                "tobs": result.tobs,
            }
        tobs_list.append(tobs_dict)

    session.close()

    return jsonify(tobs_list)
   


@app.route("/api/v1.0/temperatures/<start>")
def temperature_stats_start(start):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()

    except ValueError:
        return jsonify({"error": "Invalid date format. Please use the 'YYYY-MM-DD' format."}), 400

    allowed_start_date = datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    allowed_end_date = datetime.strptime('2017-08-23', '%Y-%m-%d').date()

    if not (allowed_start_date <= start_date <= allowed_end_date):
        return jsonify({"error": "Date should be between '2010-01-01' and '2017-08-23'."}), 400

    session = Session(engine)

    temperature_stats = session.query(func.min(Measurement.tobs).label("TMIN"),
                                      func.max(Measurement.tobs).label("TMAX"),
                                      func.avg(Measurement.tobs).label("TAVG")).\
                                      filter(Measurement.date >= start_date).all()

    session.close()

    if temperature_stats:
        temperature_stats_dict = {
            "TMIN": temperature_stats[0].TMIN,
            "TMAX": temperature_stats[0].TMAX,
            "TAVG": temperature_stats[0].TAVG,
        }
        return jsonify(temperature_stats_dict)



@app.route("/api/v1.0/temperatures/<start>/<end>")
def temperature_stats_start_end(start, end):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use the 'YYYY-MM-DD' format."}), 400

    allowed_start_date = datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    allowed_end_date = datetime.strptime('2017-08-23', '%Y-%m-%d').date()

    if not (allowed_start_date <= start_date <= allowed_end_date):
        return jsonify({"error": "Date should be between '2010-01-01' and '2017-08-23'."}), 400

    if not (allowed_start_date <= end_date <= allowed_end_date):
        return jsonify({"error": "Date should be between '2010-01-01' and '2017-08-23'."}), 400

    session = Session(engine)

    temperature_stats = session.query(func.min(Measurement.tobs).label("TMIN"),
                                      func.max(Measurement.tobs).label("TMAX"),
                                      func.avg(Measurement.tobs).label("TAVG")).\
                                      filter(Measurement.date >= start_date).\
                                      filter(Measurement.date <= end_date).all()

    session.close()

    if temperature_stats:
        temperature_stats_dict = {
            "TMIN": temperature_stats[0].TMIN,
            "TMAX": temperature_stats[0].TMAX,
            "TAVG": temperature_stats[0].TAVG,
        }
        return jsonify(temperature_stats_dict)
 


if __name__ == '__main__':
    app.run(debug=True)





