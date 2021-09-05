import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&#60;start&#62;<br/>"
        f"/api/v1.0/&#60;start&#62;/&#60;end&#62;<br/>"
        f"&#60;start&#62; and &#60;end&#62; dates should be in numeric YYYY-MM-DD format"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    station_list = []
    for station, name in results:
        station_dict = {station:name}
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    log_counter = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).first()
    most_active = log_counter[0]
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == most_active).all()
    session.close()
    
    station_data = []
    for date, temp in results:
        data_dict = {date:temp}
        station_data.append(data_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/<start>")
#@app.route("/api/v1.0/<start>/<end>")
def stats(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    session = Session(engine)
    log_counter = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).first()
    most_active = log_counter[0]
    max_temp = session.query(Measurement.date,func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.station == most_active).all()
    min_temp = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.station == most_active).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.station == most_active).all()
    session.close()

    tobs_data = [{"TMIN": (max_temp[0][0], max_temp[0][1])},{"TAVG": avg_temp[0][0]},{"TMIN": (min_temp[0][0], min_temp[0][1])}]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>/<end>")
def stats2(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    session = Session(engine)
    log_counter = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).first()
    most_active = log_counter[0]
    max_temp = session.query(Measurement.date,func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).filter(Measurement.station == most_active).all()
    min_temp = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.station == most_active).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).filter(Measurement.station == most_active).all()
    session.close()

    tobs_data = [{"TMIN": (max_temp[0][0], max_temp[0][1])},{"TAVG": avg_temp[0][0]},{"TMIN": (min_temp[0][0], min_temp[0][1])}]

    return jsonify(tobs_data)

if __name__ == "__main__":
    app.run(debug=True)