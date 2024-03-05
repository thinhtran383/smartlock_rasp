from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

import paho.mqtt.client as mqtt

app = Flask(__name__)
CORS(app)
# Cấu hình cơ sở dữ liệu SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/thinhtran/smartlock/flask/smart_lock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cau hinh ket noi mqtt
mqtt_broker_address = '0.tcp.ap.ngrok.io'
mqtt_client = mqtt.Client()

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy(app)

# Định nghĩa model cho bảng Users
class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)

# Định nghĩa model cho bảng History
class History(db.Model):
    historyId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=True)
    time = db.Column(db.DateTime, nullable=False)

# Định nghĩa model cho bảng secures
class Secure(db.Model):
    secureId = db.Column(db.Integer, primary_key=True)
    passcode = db.Column(db.String(50), nullable=False)
    positionFinger = db.Column(db.String(50))
    userId = db.Column(db.Integer)
    temporaryPasscode = db.Column(db.Boolean,default=False)
    accessCount = db.Column(db.Integer, default=False, nullable=True)
    root = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()


#Route xoa user, secure thong qua passcode
@app.route('/api/v1/secure/deleteUser/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_to_delete = User.query.get(user_id)
        if user_to_delete is None:
            return jsonify({
                'status': False,
                'message': 'User not found',
                'data': None
            }), 404
        update_user_id_to_null(user_id)
        #Xoa entry trong bang secure (neu co)
        secure_to_delete = Secure.query.filter_by(userId=user_id).first()
        if secure_to_delete:
            db.session.delete(secure_to_delete)
           
        #Xoa user
        db.session.delete(user_to_delete)
        db.session.commit()
        
        return jsonify({
            'status': 'OK',
            'message': 'User and associated secure entry deleted successfully',
            'data': None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test/<user_id>', methods=['GET'])
def update_user_id_to_null(user_id):
    print(user_id)
    try:
        # Lấy danh sách bản ghi trong bảng History có userId bằng với tham số truyền vào
        history_entries = History.query.filter_by(userId=user_id).all()

        # Cập nhật userId thành null cho từng bản ghi và commit
        for entry in history_entries:
            entry.userId = None
       

        print("Successfully updated userId to null for all records with userId =", user_id)

    except Exception as e:
        print("Error:", str(e))
        
#Route gui message qua mqtt
@app.route('/sendMessage/<message>', methods=['POST'])
def send_message(message):
    try:
        # Ket noi mqtt broker
        mqtt_client.connect(mqtt_broker_address, 11194, 60)
        
        # Send message
        mqtt_client.publish('test', message)
        
       
        
        return jsonify({
            'status': 'Ok',
            'message': 'successfully',
            'data': None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Route get lich su ra vao
@app.route('/api/v1/history', methods=['GET'])
def get_history():
    try:
        # Lay danh sach lich su tu db
        history_entries = History.query.all()
        
        # Xay dung danh sach tra ve ket qua
        result = []
        for entry in history_entries:
            user = User.query.get(entry.userId)
            
            entry_data = {
                'id': entry.historyId,
                'user': {
                    'id': None if user is None else user.userId,
                    'username': None if user is None else user.username
                },
                'time': entry.time.isoformat()
            }
            result.append(entry_data)
        return jsonify({
                'status': 'Ok',
                'message': 'successfully',
                'data': result
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route de kiem tra passcode
@app.route('/api/v1/secure/<passcode>', methods=['POST'])
def check_passcode(passcode):
    try:
        # Kiem tra passcode
        passcode_exists = Secure.query.filter_by(passcode=passcode).first()
        
        
        # Neu temporaryPasscode = True, giam accesscount va xoa neu accesscount = 0  
        if passcode_exists:
            if passcode_exists.temporaryPasscode:
                passcode_exists.accessCount -= 1
                if passcode_exists.accessCount <= 0:
                    db.session.delete(passcode_exists)
                else:
                    db.session.commit()
        
            new_history_entry = History(userId=passcode_exists.userId, time=datetime.now())
            db.session.add(new_history_entry)
            db.session.commit()
        
        return jsonify({
            'status' : 'Ok',
            'message' : 'Unlocked' if passcode_exists is not None else 'Passcode wrong',
            'data' : passcode_exists is not None
        }), 200
    except Exception as e:
        return jsonify({'error':str(e)}), 500


# Route để tạo mới người dùng và secures
@app.route('/api/v1/user/create', methods=['POST'])
def create_user():
    try:
        guest_param = request.args.get('guest')
        data = request.get_json()
        
        if guest_param and guest_param.lower() == 'true':
            print('True')

        # Kiểm tra xem "user" và "passcode" có trong JSON hay không
        if "user" not in data or "passcode" not in data:
            return jsonify({"error": "Invalid JSON format"}), 400
        
        passcode = data['passcode']
        
        if Secure.query.filter_by(passcode=passcode).first():
            return jsonify({
                'message': 'User is existed',
                'status' : 'False',
                'data' : None
                }), 409

        # Tạo mới người dùng
        new_user = User(username=data["user"]["username"])
        db.session.add(new_user)
        db.session.commit()

        # Lấy userId mới tạo
        user_id = new_user.userId

        # Tạo mới secure
        if guest_param and guest_param.lower() == 'true':
            new_secure = Secure(passcode=data['passcode'], accessCount=data['accessCount'],temporaryPasscode=True, userId=user_id)
        else:
            new_secure = Secure(passcode=data["passcode"], userId=user_id)
            
        db.session.add(new_secure)
        db.session.commit()

        return jsonify({
            "status": "Ok",
            "message": "User created successfully",
            "data": None
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v2/secure/getAllUser', methods=['GET'])
def get_all_users_v2():
    try:
        # Lấy danh sách người dùng và secures từ cơ sở dữ liệu
        users = User.query.all()
        secures = Secure.query.all()

        # Xây dựng danh sách kết quả theo định dạng yêu cầu
        result = []
        for secure in secures:
            user_data = {
                'userId': None,
                "username": None,
                'accessCount': secure.accessCount,
                "passcode": secure.passcode,
                "fingerPosition": secure.positionFinger,
                'temporaryCode': secure.temporaryPasscode
            }

            # Tìm thông tin người dùng tương ứng (nếu có)
        
            user = next((user for user in users if user.userId == secure.userId), None)
            if user:
                user_data["username"] = user.username
                user_data['userId'] = user.userId
                
            result.append(user_data)

        return jsonify({
            "data": result,
            "status": "Ok",
            "message": "success"
            
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/secure/getAllUser', methods=['GET'])
def get_all_users():
    try:
        # Lấy toàn bộ người dùng và secures từ cơ sở dữ liệu
        users = User.query.all()
        secures = Secure.query.all()

        # Xây dựng danh sách kết quả theo định dạng yêu cầu
        result = []
        for user in users:
            user_data = {
                'userId': user.userId,
                'username': user.username,
                'accessCount': 0,  # Khởi tạo giá trị cho trường accessCount, bạn có thể điều chỉnh nếu cần
                'passcode': None,
                'fingerPosition': None,
                'temporaryCode': None
            }

            # Tìm thông tin secure tương ứng (nếu có)
            secure = next((secure for secure in secures if secure.userId == user.userId), None)
            if secure:
                user_data['accessCount'] = secure.accessCount
                user_data['passcode'] = secure.passcode
                user_data['fingerPosition'] = secure.positionFinger
                user_data['temporaryCode'] = secure.temporaryPasscode

            result.append(user_data)

        return jsonify({
            "data": result,
            "status": "Ok",
            "message": "success"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/history', methods=['GET'])
def getHistory():
     
        # Sử dụng hàm json của SQLAlchemy để trả về JSON trực tiếp
        history_entries = db.session.query(History.historyId, History.userId, History.time).all()

        # Định dạng kết quả theo yêu cầu
        result = [{"id": entry[0], "userId": entry[1], "time": entry[2].isoformat()} for entry in history_entries]

        return jsonify({
            "status": "Ok",
            "message": "success",
            "data": result
        }), 200

   
@app.route('/users', methods=['GET'])
def getUser():
    try:
        # Sử dụng hàm json của SQLAlchemy để trả về JSON trực tiếp
        user_entries = db.session.query(User.userId, User.username).all()

        # Định dạng kết quả theo yêu cầu
        result = [{"userId": entry[0], "username": entry[1]} for entry in user_entries]

        return jsonify({
            "status": "Ok",
            "message": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/secures', methods=['GET'])
def get_all_secures():
    try:
        # Sử dụng hàm json của SQLAlchemy để trả về JSON trực tiếp
        secure_entries = db.session.query(Secure.secureId, Secure.passcode, Secure.positionFinger, Secure.userId, Secure.root, Secure.accessCount, Secure.temporaryPasscode).all()

        # Định dạng kết quả theo yêu cầu
        result = [
            {"secureId": entry[0], "passcode": entry[1], "positionFinger": entry[2], "userId": entry[3], "root": entry[4], 'accessCount': entry[5], 'temporaryPasscode': entry[6]}
            for entry in secure_entries
        ]

        return jsonify({
            "status": "Ok",
            "message": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def change_useId_to_null(user_id):
    history_entries = History.query.filter_by(userId=user_id).all()
    
    #Kiem tra xem co ban ghi nao khong
    
    if not history_entries:
        return;
    
    for entry in history_entries:
        entry.userId = None
    db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)
