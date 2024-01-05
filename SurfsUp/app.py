# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
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
def home():
    print("Server recieved request for 'Home' page...")
    return (
        f"Welcome to the 'Home' page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start'<br/>"
        f"(NOTE: Replace 'start' with a date in format yyyy-mm-dd <br/>"
        f"This will return the min, average and max temperature starting from the specified date)<br/>"
        f"/api/v1.0/'start/end'<br/>"
        f"(NOTE: Replace 'start/end' with a date in format yyyy-mm-dd/yyyy-mm-dd <br/>"
        f"This will return the min, average and max temperature for the date range specified)"
    )


# Query the dates and precipitation data for the previous year of data
# Return a JSON dictionary with the date as the key and precipitation as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= '2016-08-23').order_by((measurement.date)).all()

    prcp_analysis = []
    for date, prcp in results:
        prcp_dict = {date:prcp}
        prcp_analysis.append(prcp_dict)
    
    return jsonify(prcp_analysis)


# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)
    

# Query the dates and temperature observations of the most-active station for the previous year of data
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def temp():
    results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= '2016-08-23').\
    filter(measurement.station == "USC00519281").all()

    tobs_analysis = []
    for date, tobs in results:
        tobs_list = tobs
        tobs_analysis.append(tobs_list)
    
    return jsonify(tobs_analysis)


# Return a JSON list of the minimum, average and maximum temperature for a specified start or start-end range
@app.route("/api/v1.0/<start>")
def summary_temp(start):
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start).all()

    summary_list = []
    for min, avg, max in results:
        summary_dict = {}
        summary_dict["TMIN"] = min
        summary_dict["TAVG"] = avg
        summary_dict["TMAX"] = max 
        summary_list.append(summary_dict)
    
    return jsonify(summary_list)


@app.route("/api/v1.0/<start>/<end>")
def summary_temp_range(start,end):
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start).\
    filter(measurement.date <= end).all()

    summary_list = []
    for min, avg, max in results:
        summary_dict = {}
        summary_dict["TMIN"] = min
        summary_dict["TAVG"] = avg
        summary_dict["TMAX"] = max 
        summary_list.append(summary_dict)
    
    return jsonify(summary_list)

# Close session
session.close()


# app.run
if __name__ == "__main__":
    app.run(debug=True)

