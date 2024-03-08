# Import dependencies
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
# Import NumPy library
import numpy as np


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    # Calculate the date one year ago from the last date in dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).all()
    
    # Convert the results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations
    results = session.query(Measurement.station).all()
    
    # Convert the results to a list
    stations_list = list(np.ravel(results))
    
    # Extract the most active station ID
    most_active_station_id = stations_list[0]  # Assuming the first station is the most active
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the last year."""
    # Calculate the date one year ago from the last date in dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Query to find the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()
    
    # Check if there are active stations
    if active_stations:
        # Extract the most active station ID
        most_active_station_id = active_stations[0][0]

        # Query temperature observations for the most active station for the last year
        results = session.query(Measurement.tobs).\
                    filter(Measurement.station == most_active_station_id).\
                    filter(Measurement.date >= one_year_ago).all()

        # Convert the results to a list
        temperatures = list(np.ravel(results))

        return jsonify(temperatures)
    else:
        return "No active stations found."



@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return the minimum, average, and maximum temperatures from a start date."""
    # Query temperatures for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    
    # Convert the results to a list
    temp_stats = list(np.ravel(results))
    
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    """Return the minimum, average, and maximum temperatures for a date range."""
    # Query temperatures for dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert the results to a list
    temp_stats = list(np.ravel(results))
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
