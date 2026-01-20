from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint('auth', __name__) #auth için blueprint

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt"""
    if current_user.is_authenticated: #eğer zaten giriş yapmışsa ana sayfaya yönlendir kayıt yapamaz
        return redirect(url_for('main.index'))
    
    if request.method == 'POST': #form gönderildiyse verileri al
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Validasyon: Kullanıcı adı ve email benzersiz olmalı
        if User.query.filter_by(username=username).first(): #bu kullanıcı adı var mı
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'danger') # varsa hata mesajı göster ve kayıt sayfasına geri dön
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first(): # bu email var mı
            flash('Bu e-posta zaten kullanılıyor!', 'danger') # varsa hata mesajı göster ve kayıt sayfasına geri dön
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email) #yeni kullanıcı oluştur
        user.set_password(password) #set_password şifreyi hashleyerek kaydet güvenlik için
        db.session.add(user) #vt ekle
        db.session.commit() #vt kaydet
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success') # başarı mesajı göster
        return redirect(url_for('auth.login')) #login sayfasına yönlendir
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı girişi"""
    if current_user.is_authenticated: #zaten giriş yapmışsa ana sayfaya yönlendir
        return redirect(url_for('main.index'))
    
    if request.method == 'POST': #form gönderildiyse verileri al
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first() #kullanıcı adına göre kullanıcıyı bul
        
        if user and user.check_password(password): #hashlenmiş şifreyi kontrol et
            login_user(user) #flask login ile oturumu başlat session a kullanıcı id si kaydedilir
            next_page = request.args.get('next') #korumalı sayfaya giriş yapılmadan girilmeye çalışıldıysa giriş sonrası oraya yönlendir
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(next_page if next_page else url_for('main.index')) #yoksa ana sayfaya git
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'danger') # yanlış bilgi girildiyse hata mesajı
    
    return render_template('login.html')

@bp.route('/logout')
@login_required #bu route a sadece giriş yapmış kullanıcılar erişebilir
def logout():
    """Kullanıcı çıkışı"""
    logout_user() #session ı temizle oturumu kapat
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('main.index')) #ana sayfaya yönlendir

#uygulama başlatma
#run.py - create_app() - blueprints kaydedilir - db oluşturulur - uygulama hazır

#kullanıcı kaydı
#/register get - form göster - /register post - validasyon - şifre hashle - db ye kaydet - login e yönlendir

#giriş
#/login get - form göster - /login post - kullanıcı bul - şifre kontrol - session oluştur - ana sayfaya yönlendir

#ana sayfa 
#/ - yazıları filtrele(kategori, arama) - sayfalama - kategorileri listele - popüler yazılar - template render et

#iletişim 
#/contact post - form verilerini al - db ye kaydet - adminlere bildirim oluştur - flash mesaj - yönlendir