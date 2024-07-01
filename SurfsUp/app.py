# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func

import datetime as dt
import numpy as np 
from flask import Flask, jsonify, request

from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# start homepage and list all available routes
@app.route("/")
def welcome():
    """List available routes"""
    return (
        "Welcome to the Homepage!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start> - Enter Start Date yyyy-mm-dd<br/>"
        "/api/v1.0/<start>/<end> - Enter Start and End Date yyyy-mm-dd/"
    )

# query to convert the last 12 months of precipitation analysis to a dictionary - date and prcp as values 
@app.route("/api/v1.0/precipitation")
def last_precipitation():
    # create session
    session = Session(engine)

    """Return a list of precipitition data of previous 365 days"""
    
    # query for only previous year precipitation - find last 12 months data
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    year_before = most_recent_date - dt.timedelta(days=365)
   
    precipitation_data = session.query(measurement.date, measurement.prcp).\
                         filter(measurement.date >= year_before).all()
    # close local session
    session.close()

    # Convert data to dictionary with date and prcp
    precipitation_dict = {}
    for date, prcp in precipitation_data:
        precipitation_dict[date] = prcp

    
    # Return the JSON representation of dictionary
    return jsonify(precipitation_dict)

# query a list of all stations 
@app.route("/api/v1.0/stations")
def names_of_stations():
    # Create session
    session = Session(engine)

    # Query all station names
    station_results = session.query(station.station).all()

    # close local session
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    # Return the JSON of the station list
    return jsonify(all_stations)

# query previous year temperature and dates for the most active station
@app.route("/api/v1.0/tobs")
def temperature_data():
    # create session
    session = Session(engine)

    # calculate the last 12 months of data from given data
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    year_before = most_recent_date - dt.timedelta(days=365)

    # query for the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
                           group_by(measurement.station).\
                           order_by(func.count(measurement.station).desc()).first()[0]

    # Query for temperature observations of the most active station for the last year
    temperature_results = session.query(measurement.date, measurement.tobs).\
                          filter(measurement.station == most_active_station).\
                          filter(measurement.date >= year_before).all()

    # close local session
    session.close()

    # convert list of tuples into normal list 
    temperature_data = list(np.ravel(temperature_results))

    # Return the JSON representation of the list
    return jsonify(temperature_data)

# Define route for /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temperature_observations():
    # Create session
    session = Session(engine)

    # calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    year_before = most_recent_date - dt.timedelta(days=365)

    # query for the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
                          group_by(measurement.station).\
                          order_by(func.count(measurement.station).desc()).first()[0]

    # query for temperature data of the most active station for the previous year
    temperature_results = session.query(measurement.date, measurement.tobs).\
                          filter(measurement.station == most_active_station).\
                          filter(measurement.date >= year_before).all()

    
    # close local session
    session.close()

    # convert list of tuples into normal list 
    temperature_data = list(np.ravel(temperature_results))


# query for a given start date return the min, max and avg temperature 
@app.route("/api/v1.0/<start>")
def start_tobs_data(start):
    # create session
    session = Session(engine)

    # query for minimum, average, and maximum temperatures for the given start date
    start_temp_data = session.query(func.min(measurement.tobs).label('min_temp'),
                              func.avg(measurement.tobs).label('avg_temp'),
                              func.max(measurement.tobs).label('max_temp')).\
                filter(measurement.date >= start).all()
    
    # close local session
    session.close()
    
    # save results for dictionary
    min_temp = start_temp_data[0].min_temp
    avg_temp = start_temp_data[0].avg_temp
    max_temp = start_temp_data[0].max_temp
    
    # create dictionary to hold the temperature data
    start_temp_dict = {
        "start_date": start,
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }
    
    # return the JSON  of the temperature data
    return jsonify(start_temp_dict)

# query for a given start and end date return the min, max and avg temperature

@app.route("/api/v1.0/<start>/<end>")
def start_end_tobs_data(start, end):
    # create session
    session = Session(engine)
    
    # query for minimum, average, and maximum temperatures for any specified date range
    start_and_end_temp_data = session.query(func.min(measurement.tobs).label('min_temp'),
                              func.avg(measurement.tobs).label('avg_temp'),
                              func.max(measurement.tobs).label('max_temp')).\
                filter(measurement.date >= start).\
                filter(measurement.date <= end).all()
    
    # close local session
    session.close()
    
    # save results for dictionary
    min_temp = start_and_end_temp_data[0].min_temp
    avg_temp = start_and_end_temp_data[0].avg_temp
    max_temp = start_and_end_temp_data[0].max_temp
    
    # create dictionary to hold the temperature data
    start_and_end_temp_dict = {
        "start_date": start,
        "end_date": end,
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }
    
    # return the JSON of the temperature data
    return jsonify(start_and_end_temp_dict)


if __name__ == "__main__":
    app.run(debug=True)