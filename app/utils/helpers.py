import os
from datetime import datetime
from werkzeug.utils import secure_filename #dosya adını güvenli hale getirir türkçe karakterleri temizler
from PIL import Image #resim işleme(pillow)
from flask import current_app 
from app import db
from app.models import Notification

def allowed_file(filename):
    """Dosya uzantısının izin verilen türde olup olmadığını kontrol et"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    #'.' in filename: Uzantı var mı?
    #filename.rsplit('.', 1): Sağdan ilk noktadan böl
    #'photo.jpg' → ['photo', 'jpg']
    #'my.photo.png' → ['my.photo', 'png']
    #[1]: İkinci parçayı al (uzantı)
    #lower(): Küçük harfe çevir (JPG → jpg)
    #in ALLOWED_EXTENSIONS: İzin verilen mi?


def save_image(file, folder='uploads'):
    """Resmi kaydet ve optimize et"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) #secure_filename(): Güvenli dosya adı
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_') #timestamp benzersiz dosya adı için
        filename = timestamp + filename
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename) #path birleştirme app/static/upload , photo.png -- app/ststic/uploads/photo.png
        
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True) #os.makedirs klasör oluştur exist_ok true varsa hata  verme
        
        #PIL ile resim işleme
        img = Image.open(file) #dosyayı aç
        img.thumbnail((1200, 1200)) #küçült
        img.save(filepath, quality=85, optimize=True) #kalite 85 dosya boyutunu optimize et
        
        return filename #başarılıysa filename döndür
    return None #başarısız none döndür

def create_notification(user_id, sender_id, notif_type, message, link=None):
    """Bildirim oluştur""" #--tek yerde oluşturduk buradan çağırabiliriz
    notification = Notification(
        user_id=user_id,
        sender_id=sender_id,
        type=notif_type,
        message=message,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification