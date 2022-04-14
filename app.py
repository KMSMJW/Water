from logging import debug
from flask import Flask, Blueprint, request
from flask.helpers import send_from_directory
from flask_restx import Api, Resource
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null

from database import db, DailyData
from ai_predict import *

from sqlalchemy import func

import datetime


def create_app() -> Flask:
    #init flask and restx
    app = Flask(__name__)
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api = Api(api_bp,
        base_url='/api')

    app.register_blueprint(api_bp)

    #init databse (SQLAlchemy)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)

    @api.route('/data')
    class Data(Resource):
        def get(self):
            #오늘 등록된 데이터를 찾는다.
            data = DailyData.query.filter(func.DATE(DailyData.date) == datetime.date.today()).one_or_none()
            if not data:
                data = DailyData()
                data.date = datetime.date.today()

            if data.is_valid():
                predict = predict_second_water_quality(data.to_list())
            else:
                predict = None

            return {
                "error": 0,
                "message": "success",
                "data" : data.to_dict(),
                "result" : predict,
            }, 200

        def post(self):
            payload = request.json.get('data')
            #validate date
            if payload.get('date') != datetime.date.today().isoformat() :
                return {
                    "error": 1,
                    "message": "can upload only today data",
                }

            #check today data is already exist
            today = DailyData.query.filter(func.DATE(DailyData.date) == datetime.date.today()).one_or_none()
            if not today:
                #if not exist, create new one
                today = DailyData()
                today.date = datetime.date.today()
                db.session.add(today)
            
            #update today
            today.temp_air = payload.get('temp_air', None)
            today.rainfall = payload.get('rainfall', None)
            today.temp_biotank = payload.get('temp_biotank', None)
            today.inflow_volume = payload.get('inflow_volume', None)
            today.inflow_ss = payload.get('inflow_ss', None)
            today.inflow_tn = payload.get('inflow_tn', None)
            today.inflow_tp = payload.get('inflow_tp', None)
            today.outflow_ss = payload.get('outflow_ss', None)
            today.outflow_tn = payload.get('outflow_tn', None)
            today.outflow_tp = payload.get('outflow_tp', None)
            today.outflow_nh4 = payload.get('outflow_nh4', None)
            today.air_flowrate = payload.get('air_flowrate', None)
            db.session.commit()

            #predict second water quality
            if today.is_valid():
                predict = predict_second_water_quality(today.to_list())
                return {
                    "error": 0,
                    "message": "success",
                    "data" : today.to_dict(),
                    "result" : predict,
                }
            else:
                return {
                    "error": 1,
                    "message": "데이터 부족",
                    "data" : today.to_dict(),
                    "result": None
                }
            
    @api.route('/airflow')
    class Airflow(Resource):
        def get(self):
            #parse args
            args = request.args
            
            try:
                target = [
                    float(args['ss']),
                    float(args['tn']),
                    float(args['tp']),
                ]
            except:
                return {
                    "error": 1,
                    "message": "목표 수질값을 확인해주세요.",
                    "data" : args,
                    "result" : None,
                }


            #get data from db
            fiveday_daily_data = DailyData.query.order_by(DailyData.date.desc()).limit(5).all()

            if fiveday_daily_data[0].is_valid():
                fiveday_data_list = list(map(lambda e : e.to_list(), fiveday_daily_data))

                #run ai                
                result = predict_airflow(fiveday_data_list, target)

                return {
                    "error": 0,
                    "message": "success",
                    "data" : args,
                    "result" : result,
                }
                    
            else:
                return {
                    "error": 1,
                    "message": "오늘 데이터가 완전히 입력되지 않았습니다.",
                    "data" : args,
                    "result": None
                }

    @api.route('/final')
    class Fianl(Resource):
        def get(self):
            decision_airflow = request.args['d_air']

            today = DailyData.query.filter(func.DATE(DailyData.date) == datetime.date.today()).one_or_none()

            if today and today.is_valid():
                result = predict_final(today.to_list(), decision_airflow)

                return {
                    "error": 0,
                    "message": "success",
                    "data" : decision_airflow,
                    "result" : result,
                }
            else:
                return {
                    "error": 1,
                    "message": "오늘 데이터가 완전히 입력되지 않았습니다.",
                    "data" : decision_airflow,
                    "result": None
                }

    @app.route('/', methods=["GET"])
    def default_page():
        return send_from_directory('static', 'index.html')

    @app.route('/<path:path>', methods=["GET"])
    def static_file(path):
        return send_from_directory('static', path)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)         