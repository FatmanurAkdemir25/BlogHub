#init.py uygulama fabrikası
from flask import Flask #web framework unun ana sınıfı
from flask_login import LoginManager # kullanıcı oturum yönetimi için
from flask_sqlalchemy import SQLAlchemy #veritabanı orm
import markdown #markdown formatını html e çevirmek için
import os #dosya işlemleri için 

# Extensions nesneleri global olarak oluşturuluyor ama henüz uygulamaya bağlanmıyor.
# bu application factory pattern in bir parçası 
# böylece birden fazla uygulama instance ı oluşturulabilir (test,production gibi)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class='config.Config'): #application factory fonksiyonu. flask uygulamasını oluşturup yapılandırır
    app = Flask(__name__) # yeni bir flask uygulaması oluşturur. __name__ flask a modülün konumunu söyler
    app.config.from_object(config_class) # config sınıfından ayarları yükler (vt url i , secret key gibi)
    
    # Initialize extensions
    db.init_app(app) #sqlalchemy yi uygulamaya bağlar
    login_manager.init_app(app) # login manager i başlatır
    login_manager.login_view = 'auth.login' #giriş yapmadan korumalı sayfaya girilince yönlendirilecek sayfa
    login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.' #yönlendirme sırasında gösterilecek mesaj
    login_manager.login_message_category = 'info' #flask mesaj kategorisi (success, info, danger gibi)
    
    # User loader
    from app.models import User
    
    @login_manager.user_loader #flask login in kullanıcıyı session dan yüklemesi için gerekli callback
    def load_user(user_id): # fonksiyon, session daki user_id yi alır ve vt den o kullanıcıyı döndürür. her http request inde otomatik çağrılır böylece current_user her zaman güncel olur
        return User.query.get(int(user_id))
    
    # Template filter
    @app.template_filter('markdown') #Template'lerde kullanılmak üzere özel bir Jinja2 filtresi tanımlanıyor
    def markdown_filter(text): #markdown formatındaki metni html e çevirir 
        return markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'tables']) #extensions kod blokları, syntax highlighting ve tablo desteği ekler
    
    # Create upload folder --- resim yükleme için gerekli klasörü oluşturur.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # exist ok true klasör zaten varsa hata vermez
    
    # Register blueprints --- blueprintler uygulamayı modüler hale getirir ve her biri bir özellik grubunu temsil eder
    from app.routes import auth, main, posts, admin, user
    
    app.register_blueprint(auth.bp) #giriş, çıkış, kayıt
    app.register_blueprint(main.bp) #ana sayfa, hakkında, iletişim
    app.register_blueprint(posts.bp) #yazı crud(create, read, update, delete)
    app.register_blueprint(admin.bp) #admin paneli
    app.register_blueprint(user.bp) # kullanıcı profili,bildirimler
    # register_blueprint blueprintleri uygulamaya kaydeder
    
    # Create database tables
    with app.app_context(): #Flask'ın application context'ini aktif eder
        db.create_all() # tüm model sınıflarına göre vt tablolarını oluşturur(yoksa)
    
    return app #yapılandırılmış flask uygulamasını döndürür