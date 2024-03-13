from flask import Flask, Response,request
import cv2
import json 
from datetime import date, datetime
from db import connection
from flask_cors import CORS, cross_origin

# Tespit modelini içeren dosyanın ve modelin çalışmasını kontrol eden change fonksiyonu eklenmesi
from YOLO_Video import video_detection, change
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#app.config['SECRET_KEY'] = 'roll'

#Generate_frames function takes path of input video file and  gives us the output with bounding boxes
# around detected objects


#x SQL sorgusu için, şuanda lazım mı emin değilim
x = None

#veri tabanı bağlantısı, y SQL sorgusu z sorgu içindeki değişken
def dbconn(y,z=None):
    try:
        c, conn =connection()
        print("Bağlandi")
    except Exception as e:
        print(str(e))
    print(y)
    if z ==None:
        c.execute(y)
    else:
        c.execute(y,[z])
    conn.commit()
    data= c.fetchall()
    print(data)
    for x in data:
        print(x)
    return data


#veri tabanından gelen verinin json formatına çevrilmesi
def json_serial(obj):

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


#Modeli çağıran ve sonuç olarak gelen imgeleri jpeg formatında işleyip sunuma hazır eden fonksiyon
def generate_frames(path_x = ''):
    #path_x modelin işleyeceği görüntünün adresi


    #yolo output her bir görüntü karesinin tespit sonucunu döndüren modeli içeriyor
    #video_detection modelin fonksiyonu
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)
        # imgeler byte'a çevrilip Yield keyword ile generator şeklinde her bir imge teker teker  sunuluyor
        # Content-Type ile sunulan verinin jpeg fromatında imge olduğunu cliente sunuyoruz ki html tagı işleyebilsin
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')
        
#Cors hatasını engellemek için
@cross_origin()

#imgeyi sunan adres 
@app.route('/video')
def video():
    return Response(generate_frames(path_x='DEU-NET-SCRATCH.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')


#modeli durduran adres
@app.route('/pause', methods=['GET'])
def pau():
    return str(change(1))

#modeli devam ettiren adres
@app.route('/continue', methods=['GET'])
def cont():
    return str(change(0))

#işlemde olan modelin sonucunu sunan adres
@app.route('/curr', methods=['GET'])
def curr():
    x = "SELECT Id FROM rolls ORDER BY Id DESC LIMIT 1"
    Id = dbconn(x)
    y = "SELECT det.DetSec, def.Defect, img.Image from detections as det LEFT JOIN defects as def ON det.DefectId = def.Id LEFT JOIN image as img ON det.ImageId = img.Id WHERE det.Id = %s"  
        #print("SON ID:   "+ str(Id))
        #Id = Id.get["Id"]
        #print("SON ID:   "+ str(Id))
    Id = "".join([ele for ele in str(Id) if ele.isdigit()])
    print("SON ID:   "+Id)
        #input("devam?")
    data = dbconn(y,Id)
    return json.dumps(data, default=json_serial)

@app.route('/rolls', methods=['GET'])
def rolls():
    x = "SELECT Id, DateTime FROM rolls"
    data = dbconn(x)
    return json.dumps(data, default=json_serial)

@app.route('/roll', methods=['GET'])
def roll():
    Id = request.args.get('Id')
    x = "SELECT det.DetSec, def.Defect, img.Image from detections as det LEFT JOIN defects as def ON det.DefectId = def.Id LEFT JOIN image as img ON det.ImageId = img.Id WHERE det.Id = %s"
    data = dbconn(x,Id)
    return json.dumps(data, default=json_serial)


if __name__ == "__main__":
    app.run(debug=True)