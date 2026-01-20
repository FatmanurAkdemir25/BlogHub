import os
from datetime import timedelta

class Config:
    # Güvenlik
    #secret_key flask sessionlarını şifrelemek için kullanılır
    #os.environ.get(): Önce environment variable'dan bak
    #or 'yeni-gizli-anahtar-2024-blog': Yoksa bu varsayılan değeri kullan
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yeni-gizli-anahtar-2025-blog'
    
    # Veritabanı
    #postgresql:// vt tipi
    #postgres kullanıcı adı
    #12345 şifre
    #localhost sunucu adresi
    #blog_db_new vt adı
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:12345@localhost/blog_db_new'
    #sqlalchemy nin değişiklikleri izleme özelliğini kapat ekstra memory kullanır  
    SQLALCHEMY_TRACK_MODIFICATIONS = False #performans iyileştirmesi
    SQLALCHEMY_ENGINE_OPTIONS = { #uzun süre boşta kalan bağlantıların kopmasını önler
        'pool_pre_ping': True, #her connection kullanmadan test et bağlantı kopmuş mu diye
        'pool_recycle': 300, # 300sn yani 5 dk sonra connection u yenile
    }
    
    # Dosya Yükleme
    UPLOAD_FOLDER = 'app/static/uploads' #yüklenen resimlerin kaydedileceği klasör
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # max dosya boyutu 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'} #izin verilen dosya uzantıları
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7) #session süresi 7 gün kullanıcı 7 gün boyunca giriş yapmış kalır 
    SESSION_COOKIE_SECURE = False  # Production'da True yapın --secure http olmadan çalışmaz
    SESSION_COOKIE_HTTPONLY = True #httponly js den erişilemez xss koruması
    SESSION_COOKIE_SAMESITE = 'Lax' #csrf koruması
    
    # Sayfalama
    POSTS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 20
    NOTIFICATIONS_PER_PAGE = 50