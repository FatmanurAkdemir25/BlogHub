from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Post, Follow, Bookmark, ContactMessage, Notification
from app.utils.helpers import save_image, create_notification

bp = Blueprint('user', __name__)

@bp.route('/profile/<username>') #/profile/fatmanur gibi url ler
def profile(username):
    """Kullanıcı profili"""
    user = User.query.filter_by(username=username).first_or_404() #kullanıcı adına göre kullanıcıyı bul bulamazsa 404
    
    if current_user.is_authenticated and current_user.id == user.id: #eğer kendi profiline bakıyorsa tüm yazıları göster (taslaklar dahil)
        posts = Post.query.filter_by(user_id=user.id).order_by(
            Post.created_at.desc()
        ).all()
    else: #başka birinin profiline bakıyorsa sadece yayınlanmış yazıları göster
        posts = Post.query.filter_by(
            user_id=user.id, 
            is_published=True
        ).order_by(Post.created_at.desc()).all()
    
    return render_template('profile.html', user=user, posts=posts)

@bp.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    """Profil düzenle"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if user.id != current_user.id: #sadece kendi profilini düzenleyebilir
        flash('Bu profili düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST': #bio (hakkımda) güncelle
        user.bio = request.form.get('bio')
        
        avatar = request.files.get('avatar')
        if avatar: #profil resmi yüklendiyse kaydet
            avatar_filename = save_image(avatar)
            if avatar_filename:
                user.avatar = avatar_filename
        
        db.session.commit() #değişiklikleri kaydet
        flash('Profiliniz güncellendi!', 'success')
        return redirect(url_for('user.profile', username=user.username)) #profil sayfasına geri dön
    
    return render_template('edit_profile.html', user=user) #sayfanın son halini göster

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """Kullanıcıyı takip et/takipten çık"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if user.id == current_user.id: #validasyon kendini takip edemezsin
        return jsonify({'error': 'Kendinizi takip edemezsiniz!'}), 400 #400 bad request http status kodu
    
    if current_user.is_following(user): #zaten takip ediyorsa
        current_user.unfollow(user) #unfollow metodu follow kaydını siler
        db.session.commit()
        return jsonify({ #json döndür : artık takip edilmiyor, güncel takipçi sayısı
            'following': False, 
            'followers_count': user.get_followers_count()
        })
    else: #takip etmiyorsa
        current_user.follow(user) #follow metodu yeni follow kaydı oluşturur
        db.session.commit()
        
        create_notification(
            user_id=user.id,
            sender_id=current_user.id,
            notif_type='follow',
            message=f'{current_user.username} sizi takip etmeye başladı',
            link=url_for('user.profile', username=current_user.username)
        )
        
        return jsonify({ #json döndür: takip ediliyor , güncel takipçi sayısı
            'following': True, 
            'followers_count': user.get_followers_count()
        })

@bp.route('/profile/<username>/followers')
def followers(username):
    """Kullanıcının takipçileri""" #kullanıcıların takipçilerini listele
    user = User.query.filter_by(username=username).first_or_404()
    followers_list = [Follow.query.get(f.id).follower for f in user.followers.all()] #user.followers.all() bu kullanıcıyı takip eden follow kayıtları
    return render_template('followers.html', user=user, followers=followers_list) #List comprehension ile Follow nesnelerinden User nesnelerine çevir

@bp.route('/profile/<username>/following')
def following_list(username):
    """Kullanıcının takip ettikleri"""
    user = User.query.filter_by(username=username).first_or_404()
    following = [Follow.query.get(f.id).followed for f in user.following.all()]
    return render_template('user_following.html', user=user, following=following)

@bp.route('/following')
@login_required
def following_posts():
    """Takip edilen yazarların yazıları"""
    following_ids = [f.followed_id for f in current_user.following.all()] #takip edilen kullanıcı id lerini al
    
    if not following_ids: #takip edilen kimse yoksa
        posts = []
    else:
        page = request.args.get('page', 1, type=int) #takip edilen varsa sayfa varsayılanı 1
        posts_query = Post.query.filter(
            Post.user_id.in_(following_ids), #sql in operatörü takip edilen kullanıcıların id lerini al
            Post.is_published == True #yayınlanmış
        ).order_by(Post.created_at.desc()) #en yeniler en üstte
        posts = posts_query.paginate(page=page, per_page=6, error_out=False) #yazıları sayfalandır ve göster
    
    return render_template('following.html', posts=posts)

@bp.route('/drafts')
@login_required
def drafts():
    """Taslak yazılar"""
    drafts = Post.query.filter_by(
        user_id=current_user.id, 
        is_published=False #yayınlanmamış
    ).order_by(Post.updated_at.desc()).all() # updated_at en son güncellenen önce 
    return render_template('drafts.html', drafts=drafts)

@bp.route('/bookmarks')
@login_required
def bookmarks():
    """Yer imleri""" #kullanıcının yer imlerine eklediği yazılar
    #bookmark nesnelerinden post nesnelerine çevir
    #yayınlanmış olanları filtrele
    bookmarks = Bookmark.query.filter_by(
        user_id=current_user.id
    ).order_by(Bookmark.created_at.desc()).all()
    posts = [b.post for b in bookmarks if b.post.is_published]
    return render_template('bookmarks.html', posts=posts)

@bp.route('/notifications')
@login_required
def notifications():
    """Bildirimler"""
    notifications = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).limit(50).all() #kullanıcının bildirimleri son 50 tane
    
    for notif in notifications: #tüm bildirimleri okundu işaretle. for döngüsü ile her bildirimin is_read flag ini true yap
        if not notif.is_read:
            notif.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@bp.route('/notifications/unread-count')
@login_required
def unread_notifications_count():
    """Okunmamış bildirim sayısı""" #api endpoint bedge için kullanılıyor. js her 30 sn de bir bu endpoint i çağırıyor
    count = current_user.get_unread_notifications_count()
    return jsonify({'count': count}) #sadece sayıyı döndür(json)

@bp.route('/my-messages')
@login_required
def my_messages():
    """Kullanıcının mesajları"""
    messages = ContactMessage.query.filter_by(
        user_id=current_user.id
    ).order_by(ContactMessage.created_at.desc()).all()
    return render_template('my_messages.html', messages=messages)