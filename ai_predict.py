import tensorflow.keras
from pickle import load
import numpy as np


# model and scalars
second_ann_model = tensorflow.keras.models.load_model("models/2nd_ANN")
second_scaler1 = load(open('models/2nd_scaler1.pkl','rb'))
second_scaler2 = load(open('models/2nd_scaler2.pkl','rb'))
bod_model = tensorflow.keras.models.load_model("models/BOD_ANN")
bod_scaler1 = load(open('models/BOD_scaler1.pkl','rb'))
bod_scaler2 = load(open('models/BOD_scaler2.pkl','rb'))
air_ann_model = tensorflow.keras.models.load_model("models/Air_ANN")
air_scaler1 = load(open('models/Air_scaler1.pkl','rb'))
air_scaler2 = load(open('models/Air_scaler2.pkl','rb'))
air_rnn_model = tensorflow.keras.models.load_model("models/Air_RNN")
air_rnn_scaler1 = load(open('models/Air_rnn_scaler1.pkl','rb'))
air_rnn_scaler2 = load(open('models/Air_rnn_scaler2.pkl','rb'))

def round3(i):
    return round(i, 3)

def predict_second_water_quality(today: list):
    #TODO check today is valid
    
    # second processed water quality prediction.
    front = today[:2]
    middle = today[7:11]
    back = [today[3], today[2], today[-1]]
    input = front + middle + back
    basic = second_scaler1.transform([input])
    k = second_ann_model.predict(np.array(basic).astype(np.float32))
    [predict] = second_scaler2.inverse_transform(k)

    # bod and cn-raito,
    input = today[:-1]
    basic = bod_scaler1.transform([input])
    k = bod_model.predict(np.array(basic).astype(np.float32))

    bod = bod_scaler2.inverse_transform(k).tolist()[0][0]
    cn_raito = bod / today[-4]

    return {
        'bod': round3(bod),
        'cn-raito': round3(cn_raito),
        'predict': list(map(round3, predict.tolist()))
    }

def predict_airflow_rnn(last_five_data: list):
    #rnn airflow
    last_five_data.reverse()    
    input = list(map(lambda l : l[2:4] + l[-5:], last_five_data))
    print(input)
    
    basic = input
    basic = air_rnn_scaler1.transform(basic)
    k = air_rnn_model.predict(np.array([basic]).astype(np.float32))
    rnn = air_rnn_scaler2.inverse_transform(k).tolist()
    
    return rnn

def predict_airflow(last_five_data: list, target: list):

    #필요 송풍량 예측값
    today = last_five_data[0]
    front = today[:2]
    middle1 = today[7:-1]
    middle2 = [today[3], today[2]]
    delta = [middle1[0]-target[0],middle1[1]-target[1],middle1[2]-target[2]]
    input = front + middle1 + middle2 + delta
    basic = air_scaler1.transform([input])
    k = air_ann_model.predict(np.array(basic).astype(np.float32))    
    require_airflow = air_scaler2.inverse_transform(k).tolist()

    rnn = predict_airflow_rnn(last_five_data)

    return {
        'rnn': round(rnn[0][0]),
        'require': round(require_airflow[0][0]),
    }

def predict_final(today: list, decision_airflow: float):
    print(type(second_scaler1))
    front = today[:2]
    middle = today[7:11]
    back = [today[3],today[2],decision_airflow]
    input = front + middle + back
    basic = [input]
    basic = second_scaler1.transform(basic)
    k = second_ann_model.predict(np.array(basic).astype(np.float32))

    #마지막 2차처리수 예측값#
    [final] = second_scaler2.inverse_transform(k)

    return list(map(round3, final.tolist()))
