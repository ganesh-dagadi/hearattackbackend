from flask import Flask,request,jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import pickle
import numpy as np
import copy
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:haptreflu@localhost:5432/HeartAttack"
db= SQLAlchemy()
db.init_app(app)
model = pickle.load(open('model.pkl','rb'))
print(model)
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(25))
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol= db.Column(db.Integer)
    fbs=db.Column(db.Integer)
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Integer)
    oldpeak = db.Column(db.Integer)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Integer)
    thal = db.Column(db.Integer)
    inRisk = db.Column(db.Boolean)



@app.route('/patient' , methods=["POST"])
def index():
    data = request.get_json()
    datacopy = copy.copy(data)
    # age , trestbps,chol,thalach,oldpeak
    data['age'] = data['age'] ** (1/1.2)
    data['trestbps'] = data['trestbps'] ** (1/1.2)
    data['chol'] = data['chol'] ** (1/1.2)
    data['thalach'] = data['thalach'] ** (1/1.2)
    data['oldpeak'] = data['oldpeak'] ** (1/1.2)

    data['restecg'] = int(data['restecg'])
    data['thal'] = int(data['thal'])
    datacopy['restecg'] = int(datacopy['restecg'])
    datacopy['thal'] = int(datacopy['thal'])

    if(data['sex'] == 'Male'):
        data['sex'] = 1
    else:
        data['sex'] = 0

    keys = data.keys()
    float_features = []
    for key in keys:
        float_features.append(data[key])
    float_features.pop(0)
    features = [np.array(float_features)]
    prediction = model.predict(features)
    datacopy['inRisk'] = prediction[0]
    if(datacopy['inRisk'] == 1):
        datacopy['inRisk'] = True
    else:
        datacopy['inRisk'] = False
    print(datacopy)
    patient = Patient(
        name = datacopy['name'],
        age = datacopy['age'],
        sex = datacopy['sex'],
        cp = datacopy['cp'],
        trestbps = datacopy['trestbps'],
        chol= datacopy['chol'],
        fbs=datacopy['fbs'],
        restecg = datacopy['restecg'],
        thalach = datacopy['thalach'],
        exang = datacopy['exang'],
        oldpeak = datacopy['oldpeak'],
        slope = datacopy['slope'],
        ca = datacopy['ca'],
        thal = datacopy['thal'],
        inRisk = datacopy['inRisk']
    )

    db.session.add(patient)
    db.session.commit()
    return "Patient Added"
    
@app.route('/patient' , methods=['GET'])
def getPatients():
    print('hit')
    patients = Patient.query.all()
    out = []
    for patient in patients:
        out.append(
            {   'name' : patient.name,
                'age' : patient.age,
                'sex' :  patient.sex,
                'cp' :  patient.cp,
                'trestbps' :  patient.trestbps,
                'chol':  patient.chol,
                'fbs': patient.fbs,
                'restecg' :  patient.restecg,
                'thalach' :  patient.thalach,
                'exang' :  patient.exang,
                'oldpeak' :  patient.oldpeak,
                'slope' :  patient.slope,
                'ca' :  patient.ca,
                'thal' :  patient.thal,
                'inRisk' :  patient.inRisk
            }
        )
    
    response = {'data' : out}
    return make_response(jsonify(response), 200)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)