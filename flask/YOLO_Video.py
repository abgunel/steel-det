from ultralytics import YOLO
import cv2
import math
import numpy as np
from db import connection
import base64
import time

#modelin çalışmasını kontrol eden değişken
pause =1

# değişkeni ana dosyadan değiştirmek için fonksiyon
def change(p):
    global pause
    pause= p
    return pause

#modelin fonksiyonu

def video_detection(path_x):

    #fonksiyon ilk çağırıldığında yani site ilk açıldıp imgeye erişilmek istediğinde
    #modeli hemen başlatmayan başlatma komutunu bekleyen döngü
    while pause ==1:
        
        print(str(pause))
        #çalışma değişkeninin birer saniye arayla kontrol edilmesi için sleep fonksiyonu
        time.sleep(1)
        continue
    else:
        #model ilk başlatıldığında veri tabanı bağlantısının kurulması ve yeni girdinin yapılması
        try:
            c, conn =connection()
            print("Bağlandi")
        except Exception as e:
            print(str(e))
        x= c.execute("INSERT INTO rolls (DateTime) VALUES(DEFAULT)")
        conn.commit()
        roll_id= c.lastrowid
        roll_id = str(roll_id)
        print("ROLL ID :       "+roll_id)
        #input("devam?")




    video_capture = path_x
    #Video görüntüsünün cv2'ye yüklenmesi
    cap=cv2.VideoCapture(video_capture)
    frame_width=int(cap.get(3))
    frame_height=int(cap.get(4))

    #her bir tespit edilen ayrı tespitin saklanması için bir değişken
    tracker_list=[]
    #model değişkenine model fonksiyonun modelin konumuyla birlikte verilmesi
    model=YOLO("best2k.pt")
    #modelde tespit edilen tespitlerin numaralarıyla aynı sırada kusur isimleri
    classNames = ["roll_mark", "deformation", "scratch", "oxide_scale"]
    while True:
        #her bir frame işlenmeden önce modelin çalışma komutunun kontrolü
        if pause == 0:
            pass
        else:
            continue
        #cv2'ye yüklenen imgenin iki defa ayrı ayrı okunup kaydedilmesi
        #birincisi modele vermek için, ikincisi ise aynı imgeden tespit edilen kusurların imgelerinin alınabilmesi için
        success, img = cap.read()
        success, img2=cap.read()
        #modelin çalışmasının başlatılması ve tespitlerin takibinin yapılması
        results=model.track(img,stream=True, persist=True, show=False)
        #her bir tespit sonucunun konumlarının içeren box'lara döngü yardımıyla teker teker ulaşılması
        for r in results:
            boxes=r.boxes
            #her bir tespitin konum versinin işlenmesi
            for box in boxes:
                x1,y1,x2,y2=box.xyxy[0]
                x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
                print(x1,y1,x2,y2)
                #tespit konumunun ve bilgisinin hazırlanması
                cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255),3)

                conf=math.ceil((box.conf[0]*100))/100
                cls=int(box.cls[0])
                class_name=classNames[cls]
                if box.id is None:
                    label=f'{class_name}{conf}'
                else:
                    tracker_id = box.id.cpu().numpy().astype(int)
                   #Check wheter it's first detection of uniqe defect and it's confidance treshold
                    if tracker_id not in tracker_list and conf>=0.60:
                        tracker_list.append(tracker_id)

                        #crop the detected image
                        crop_img = img2[int(y1):int(y2),int(x1):int(x2)]
                        #cv2.imshow("cropped", crop_img)
                        #image to jpeg
                        retval, buffer = cv2.imencode('.jpg', crop_img)

                        #get sec of detection time
                        sec= "{:.2f}".format(cap.get(cv2.CAP_PROP_POS_MSEC)/1000.0)
                        print(sec)


                        #image'lerin base64'e çevrilip veritabanına görüntüleriyle beraber kaydedilmesi
                        
                        try:
                            ready_img = base64.b64encode(buffer).decode('ascii')
                            print("Id: ", tracker_id)
                            print("Class name: ", class_name)
                            print("base64: ",ready_img)
                            x= c.execute("INSERT INTO detections (Id, DefectId, DetSec) VALUES(%s, %s, %s)", (roll_id, int(cls), sec))
                            conn.commit()
                            img_id = c.lastrowid
                            x = c.execute("INSERT INTO image (Id, Image) VALUES(%s, %s)", (img_id, ready_img))
                            conn.commit()
                            #input("devam?")
                        except Exception as e:
                            print(str(e))
                            #input("devam?")

                    #tespit verilerinin imge üzerine işlenmesi 
                    
                    label=f'#{tracker_id}{class_name}{conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                cv2.rectangle(img, (x1,y1), c2, [255,0,255], -1, cv2.LINE_AA)  # filled
                cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=1,lineType=cv2.LINE_AA)

        yield img
cv2.destroyAllWindows()
