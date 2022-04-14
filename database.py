from flask_sqlalchemy import SQLAlchemy
from datetime import date
db = SQLAlchemy()

class DailyData(db.Model):
    __tablename__ = 'daily_data'

    date = db.Column(db.Date, primary_key=True)
    temp_air = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    temp_biotank = db.Column(db.Float)
    inflow_volume = db.Column(db.Float)
    inflow_ss = db.Column(db.Float)
    inflow_tn = db.Column(db.Float)
    inflow_tp = db.Column(db.Float)
    outflow_ss = db.Column(db.Float)
    outflow_tn = db.Column(db.Float)
    outflow_tp = db.Column(db.Float)
    outflow_nh4 = db.Column(db.Float)
    air_flowrate = db.Column(db.Float)           

    def is_valid(self):
        return None not in self.to_list()

    def to_dict(self):
        return {
            "date" : self.date.isoformat(),
            "temp_air" : self.temp_air,
            "rainfall" : self.rainfall,
            "temp_biotank" : self.temp_biotank,
            "inflow_volume" : self.inflow_volume,
            "inflow_ss" : self.inflow_ss,
            "inflow_tn" : self.inflow_tn,
            "inflow_tp" : self.inflow_tp,
            "outflow_ss" : self.outflow_ss,
            "outflow_tn" : self.outflow_tn,
            "outflow_tp" : self.outflow_tp,
            "outflow_nh4" : self.outflow_nh4,
            "air_flowrate" : self.air_flowrate
        }
    
    def to_list(self):
        return [
            self.temp_air,
            self.rainfall,
            self.temp_biotank,
            self.inflow_volume,
            self.inflow_ss,
            self.inflow_tn,
            self.inflow_tp,
            self.outflow_ss,
            self.outflow_tn,
            self.outflow_tp,
            self.outflow_nh4,
            self.air_flowrate
        ]