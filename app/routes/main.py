from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Post, ContactMessage, Notification, User
from app.utils.helpers import create_notification
#blueprint modüler route yapısı için
#render_template html template leri render etmek için
#request http request verilerine erişim
#redirect, url_for sayfa yönlendirmeleri
#flash kullanıcıya mesaj gönderme 
#login_required route koruma decorator ı 
#current_user şu anki giriş yapmış kullanıcı

bp = Blueprint('main', __name__) #blueprint nesnesi oluşturuluyor. isin main - url oluşturulurken kullanılır (url_for('main.index'))

@bp.route('/') #bu fonksiyon ana sayfa (/) için çalışır
def index():
    """Ana sayfa"""
    page = request.args.get('page', 1, type=int) #url den sayfa numarasını alır varsayılan 1
    category = request.args.get('category', None) #kategori filtresi
    search = request.args.get('search', None) #arama sorgusu
    
    query = Post.query.filter_by(is_published=True)
    #Post.query sqlalchemy sorgusu başlatılıyor
    #filter_by(is_published=True) sadece yayınlanmış yazıları getir
    
    if category: #kategori varsa ona göre filtrele
        query = query.filter_by(category=category)
    
    if search: #arama varsa --ilike büyük küçük harf duyarsızlığı --%{search}% başında sonunda veya ortasında search kelimesi geçenler
        query = query.filter(
            (Post.title.ilike(f'%{search}%')) | # başlıkta veya içerikte ara
            (Post.content.ilike(f'%{search}%'))
        )
    
    posts = query.order_by(Post.created_at.desc()).paginate( #order_by(Post.created_at.desc()): En yeni yazılar önce gelsin paginate() sayfalama ekler
        page=page, #hangi sayfa
        per_page=6, #sayfada 6 yazı göster
        error_out=False #geçersiz sayfa numarasında hata verme, boş sayfa döndür
    )
    
    categories = db.session.query(Post.category).filter_by(
        is_published=True
    ).distinct().all() #tüm kategorileri çek tekrarsız -- distinct aynı kategoriyi bir kez getir
    categories = [cat[0] for cat in categories if cat[0]] # [cat[0] for cat in categories if cat[0]] her turple ın ilk elemanını al none olanları filtrele
    
    popular_posts = Post.query.filter_by(
        is_published=True
    ).order_by(Post.views.desc()).limit(5).all() 
    #Post.views.desc() görüntüleme sayısına göre azalan sırada sadece 5 yani en çok görüntülenen 5 yazıyı getir
    
    return render_template('index.html', #html template ini render et ve döndür
                         posts=posts, #parametreler template de kullanılabilir
                         categories=categories, 
                         popular_posts=popular_posts, 
                         current_category=category)

@bp.route('/about') #/about url i için basit bir sayfa
def about(): # sadece template render edip döndürüyor
    """Hakkında sayfası"""
    return render_template('about.html')

@bp.route('/contact', methods=['GET', 'POST']) #hem form göster get hem de form gönder post
def contact():
    """İletişim sayfası"""
    if request.method == 'POST': # form gönderildi mi kontrol et
        name = request.form.get('name') # request.form.get() post edilen form verilerini al
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        contact_msg = ContactMessage( #yeni contactmessage nesnesi oluştur
            name=name,
            email=email,
            subject=subject,
            message=message,
            user_id=current_user.id if current_user.is_authenticated else None #eğer kullanıcı giriş yapmışsa id sini kaydet yoksa none
        )
        db.session.add(contact_msg) #vt session ına ekle
        db.session.commit() #değişiklikleri kaydet(insert sql çalışır)
        
        # Admin'lere bildirim
        admins = User.query.filter_by(is_admin=True).all()
        for admin in admins: #tüm admin kullanıcıları bul her admin için bildirim oluştur
            notification = Notification(
                user_id=admin.id,
                sender_id=current_user.id if current_user.is_authenticated else None,
                type='contact', #bildirim tipi (icon göstermek için)
                message=f'Yeni iletişim mesajı: {subject}', #f string ile mesaj oluştur
                link=url_for('admin.admin_messages') #admin mesajlar sayfasının url i
            )
            db.session.add(notification)
        
        db.session.commit() #bildirimleri kaydet
        flash('Mesajınız gönderildi! En kısa sürede dönüş yapılacaktır.', 'success') #kullanıcıya başarı mesajı göster (bir sonraki sayfada görünür)
        
        if current_user.is_authenticated:
            return redirect(url_for('user.my_messages')) #giriş yapmışsa mesajlarım sayfasına yönlendir
        return redirect(url_for('main.contact')) # giriş yapmamışsa iletişim sayfasına geri dön
    
    return render_template('contact.html') # get request ise (sayfa ilk açıldığında) formu göster

@bp.route('/privacy') #/privacy url i için basit bir sayfa
def privacy():# sadece template render edip döndürüyor
    """Gizlilik politikası"""
    return render_template('privacy.html')