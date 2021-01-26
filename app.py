import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
        f"Available Routes:<br/><br/>"
        f"Query to retrieve a JSON list of the last 12 months of precipitation:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Query to retrieve a JSON list of stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Query to retrieve a JSON list of temperature observations (TOBS) for the previous year:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Query to retrieve a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date:<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/><br/>"
        f"Query to retrieve a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start/end date range:<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON list of the last 12 months of precipitation data available"""
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    # Starting from the last data point in the database.
    last_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year from the last date in data set.
    last_date_year_ago = dt.datetime.strptime(
        last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    last_date_year_ago = last_date_year_ago.strftime('%Y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_date_year_ago).all()

    session.close()

    # Create a dictionary
    all_precipitation = []
    for date, prcp in query:
        data = {}
        data['date'] = date
        data['prcp'] = prcp
        all_precipitation.append(data)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return the la JSON list of stations from the dataset"""
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    # Perform a query to retrieve all stations
    station_data = session.query(Station.station, Station.
                                name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary
    all_stations = []
    for station, name, latitude, longitude, elevation in (station_data):
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature observation data available"""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Perform a query to retrieve the dates and temperature observations for the last year of data
    # Starting from the last data point in the database.
    last_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year from the last date in data set.
    last_date_year_ago = dt.datetime.strptime(
        last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    last_date_year_ago = last_date_year_ago.strftime('%Y-%m-%d')
    # Perform a query to retrieve tobs
    tobs_data = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date.between(last_date_year_ago, last_date)).all()

    session.close()

    # Create a dictionary
    temp = []
    for name, date, tobs in (tobs_data):
        temp_dict = {}
        temp_dict["Station"] = name
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temp.append(temp_dict)

    return jsonify(temp)


@app.route("/api/v1.0/<start>")
def start(start):
    """Return min tem, avg temp, and max temp for a given start"""
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    # Perform a query to retrieve tobs for given start date and calculate calculate `TMIN`, `TAVG`, and `TMAX`
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.
                            avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()

    # Create a dictionary
    start = []
    for row in from_start:
        start_dict = {}
        start_dict["Date"] = row[0]
        start_dict["TMIN"] = row[1]
        start_dict["TAVG"] = row[2]
        start_dict["TMAX"] = row[3]
        start.append(start_dict)

    return jsonify(start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return min tem, avg temp, and max temp for a given start-end date range """
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    # Perform a query to retrieve tobs for given start-end date range and calculate calculate `TMIN`, `TAVG`, and `TMAX`
    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.
                            avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date.between(start, end)).group_by(Measurement.date).all()

    session.close()

    # Create a dictionary
    startend=[]
    for row in start_end:
        startend_dict={}
        startend_dict["Date"]=row[0]
        startend_dict["TMIN"]=row[1]
        startend_dict["TAVG"]=row[2]
        startend_dict["TMAX"]=row[3]
        startend.append(startend_dict)

    return jsonify(startend)


if __name__ == "__main__":
    app.run(debug=True)
