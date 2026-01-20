from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Admin yetkisi kontrolü decorator"""
    @wraps(f) #orijinal fonksiyonun metadatasını koru
    def decorated_function(*args, **kwargs): #herhangi sayıda argüman al
        if not current_user.is_authenticated or not current_user.is_admin: #giriş yapılmış mı admin mi ikisi de true olmalı
            flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs) #evetse fonksiyonu çalıştır
    return decorated_function