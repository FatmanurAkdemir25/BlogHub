from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users' #postgresql de tablo adı
    
    #tablonun sütunları
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True) # nullable false boş olamaz index true hızlı arama için index oluştur
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text) #text sınırsız uzunlukta genelde indexlenmez string sabit sınırlı uzunlukta indexlenebilir
    avatar = db.Column(db.String(255), default='default-avatar.jpg')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', 
                                   backref='recipient', lazy='dynamic', cascade='all, delete-orphan')
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True)
    
    following = db.relationship('Follow', foreign_keys='Follow.follower_id',
                               backref='follower', lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id',
                               backref='followed', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password): 
        self.password_hash = generate_password_hash(password) #şifreyi hashle
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password) #şifre kontrol
    
    def get_unread_notifications_count(self): #okunmamış bildirim sayısı
        return self.notifications.filter_by(is_read=False).count()
    
    def follow(self, user): # kullanıcı takip etme
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
    
    def unfollow(self, user): #takibi bırakma
        follow = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() #follow kaydını bul
        if follow: #varsa
            db.session.delete(follow) #session dan sil
    
    def is_following(self, user): #bu kullanıcıyı takip ediyor muyum
        if not user or user.id == self.id: #user  nesnesi not olamaz veya kendini takip edemezsin
            return False
        return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None #first kayıt varsa döner yoksa none is not none boolean a çevir
    
    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.following.count()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False) #içerik sınırsız
    summary = db.Column(db.String(300)) #özet
    image = db.Column(db.String(255))
    category = db.Column(db.String(50), index=True)
    views = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True, index=True) #yayınlanmış mı
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) #foreign key users tablosunun id kolonuna referans
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def get_likes_count(self): #beğeni sayısı
        return len(self.likes) #like listesinin uzunluğu
    
    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None
    
    def is_bookmarked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return Bookmark.query.filter_by(user_id=user.id, post_id=self.id).first() is not None
    
    def reading_time(self):
        """Yazının okunma süresini hesapla (dakika)"""
        import re
    
        # Markdown/HTML etiketlerini temizle
        text = re.sub(r'<[^>]+>', '', self.content)  # HTML etiketleri [^>]: > hariç her karakter +: Bir veya daha fazla
        text = re.sub(r'```[\s\S]*?```', '', text)   # Kod blokları [\s\S]: Her karakter (whitespace dahil) *?: Non-greedy (açgözlü olmayan)
        text = re.sub(r'`[^`]+`', '', text)          # Inline kod
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Resimler ![alt](url)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)   # Linkler [text](url)
        text = re.sub(r'[#*_~`]', '', text)          # Markdown karakterleri
    
        # Kelimeleri say (boş kelimeleri filtrele)
        words = len([word for word in text.split() if word.strip()])
    
        # Ortalama okuma hızı: dakikada 150 kelime
        minutes = max(1, round(words / 100))
    
        return minutes
    
        #text.split boşlukları ayır, kelime listesi oluştur
        #word.strip kelimenin başındaki ve sonundaki boşlukları sil
        #if word.strip boş stringleri filtrele
        #len liste uzunluğu=kelime sayısı
        #words/100 100 kelime/dk hızı
        #round yuvarlama
        #max(1 ...) en az 1 dk


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    #parent id comment id ye referans (kendi tablosuna) yorumlara cevap için nullable=true ana yorumlar için null
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    #comment kendi modeline referans
    #backref parent alt yorumdan ana yoruma erişim
    #remote side id hangi taraf parent sqlalchemy ye söylemek için


    def __repr__(self):
        return f'<Comment by {self.author.username}>'


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    #tablo seviyesi kısıtlamalar
    #post id ve user id benzersiz olmalı
    #bir kullanıcı yazıyı sadece bir kez beğenir

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follower_followed'),)


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) #bildirim tipi
    message = db.Column(db.String(255), nullable=False) #bildirim metni
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) #bildirim alan
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id')) #bildirim gönderen


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_bookmark'),)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True) #pending - read - replied
    admin_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    replied_at = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Kayıtlı kullanıcıysa (misafirler için NULL)




    ### Örnek 1: Kullanıcı Bir Yazıyı Beğenir

    #1. Kullanıcı beğen butonuna tıklar
    #2. JavaScript fetch() ile /post/5/like POST request gönderir
    #3. posts.like() fonksiyonu çalışır
    #4. Like.query.filter_by() ile beğeni var mı kontrol edilir
    #5. Yoksa: Yeni Like nesnesi oluşturulur → DB'ye eklenir
    #6. Yazı sahibine Notification oluşturulur
    #7. JSON response döner: {"liked": true, "likes_count": 15}
    #8. JavaScript badge'i günceller: 15


    ### Örnek 2: Takip Sistemi

    #1. A kullanıcısı B'yi takip eder
    #2. /follow/B_username POST request
    #3. user.follow() fonksiyonu çalışır
    #4. Follow tablosuna kayıt: {follower_id: A, followed_id: B}
    #5. B'ye bildirim: "A sizi takip etti"
    #6. JSON döner: {"following": true, "followers_count": 42}
    #7. Buton güncellenir: "Takip Ediliyor"


    ### Örnek 3: Bildirim Sistemi

    #1. Bir olay olur (beğeni, yorum vb.)
    #2. create_notification() çağrılır
    #3. Notification tablosuna kayıt: {user_id, type, message, is_read: false}
    #4. Kullanıcı sayfada geziniyor
    #5. JavaScript her 30sn'de /notifications/unread-count çağırır
    #6. Backend: Notification.query.filter_by(is_read=False).count()
    #7. JSON: {"count": 3}8. Badge güncellenir:  3
    #9. Kullanıcı bildirimler sayfasına girer
    #10. Tüm bildirimler is_read=True yapılır
    #11. Badge kaybolur