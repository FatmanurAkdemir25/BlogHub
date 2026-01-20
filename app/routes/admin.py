from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import User, Post, Comment, Like, Follow, ContactMessage, Notification
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin') #admin blueprint i -- tüm route lar /admin ile başlayacak(/admin/posts)

@bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin ana panel""" #her tablodan sayıları çek count ile
    total_users = User.query.count() 
    total_posts = Post.query.filter_by(is_published=True).count()
    total_comments = Comment.query.count()
    total_drafts = Post.query.filter_by(is_published=False).count()
    total_likes = Like.query.count()
    total_follows = Follow.query.count()
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(status='pending').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all() #en son 5 kullanıcı
    recent_posts = Post.query.filter_by(is_published=True).order_by(
        Post.created_at.desc()
    ).limit(5).all() #en son 5 yazı
    popular_posts = Post.query.filter_by(is_published=True).order_by(
        Post.views.desc()
    ).limit(5).all() # en popüler 5 yazı
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all() 
    recent_messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).limit(5).all()  
    
    return render_template('admin/dashboard.html', #admine bu bilgilerin hazır olduğu sayfa gösterilir
                         total_users=total_users,
                         total_posts=total_posts,
                         total_comments=total_comments,
                         total_drafts=total_drafts,
                         total_likes=total_likes,
                         total_follows=total_follows,
                         total_messages=total_messages,
                         unread_messages=unread_messages,
                         recent_users=recent_users,
                         recent_posts=recent_posts,
                         popular_posts=popular_posts,
                         recent_comments=recent_comments,
                         recent_messages=recent_messages)

@bp.route('/users')
@login_required
@admin_required
def admin_users():
    """Kullanıcı yönetimi"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/posts')
@login_required
@admin_required
def admin_posts():
    """Yazı yönetimi"""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@bp.route('/comments')
@login_required
@admin_required
def admin_comments():
    """Yorum yönetimi"""
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

@bp.route('/messages')
@login_required
@admin_required
def admin_messages():
    """Mesaj yönetimi"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    unread_count = ContactMessage.query.filter_by(status='pending').count()
    return render_template('admin/messages.html', 
                         messages=messages, 
                         unread_count=unread_count)

@bp.route('/message/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_message_detail(id):
    """Mesaj detayı ve cevaplama"""
    message = ContactMessage.query.get_or_404(id)
    
    if message.status == 'pending': #mesaj açıldığında status u read yap yani okundu
        message.status = 'read'
        db.session.commit()
    
    if request.method == 'POST': #admin cevap yazıyorsa
        reply = request.form.get('reply')
        
        if reply:
            message.admin_reply = reply #cevabı kaydet
            message.status = 'replied' #status u replied yap
            message.replied_at = datetime.utcnow() #cevap tarihini kaydet
            db.session.commit()
            
            if message.user_id: #eğer mesajı gönderen kayıtlı kullanıcıysa ona bildirim gönder
                notification = Notification(
                    user_id=message.user_id,
                    sender_id=current_user.id,
                    type='reply',
                    message=f'Mesajınıza cevap verildi: {message.subject}',
                    link=url_for('user.my_messages') #mesajlarım sayfasına link
                )
                db.session.add(notification)
                db.session.commit()
            
            flash('Cevabınız gönderildi!', 'success')
            return redirect(url_for('admin.admin_messages'))
    
    return render_template('admin/message_detail.html', message=message, User=User)

@bp.route('/message/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_message(id):
    """Mesaj sil"""
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Mesaj silindi!', 'success')
    return redirect(url_for('admin.admin_messages'))

@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_comment(id):
    """Yorum sil (admin)"""
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Yorum silindi!', 'success')
    return redirect(request.referrer or url_for('admin.admin_comments'))

@bp.route('/user/<int:id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    """Admin yetkisi ver/kaldır"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:#güvenlik için kendi yetkisini kaldıramaz
        flash('Kendi admin durumunuzu değiştiremezsiniz!', 'danger')
        return redirect(url_for('admin.admin_users'))
    
    user.is_admin = not user.is_admin #boolean değerini ters çevir
    db.session.commit()
    
    status = 'Admin yapıldı' if user.is_admin else 'Admin yetkisi kaldırıldı' # yeni duruma göre mesaj
    flash(f'{user.username} {status}!', 'success')
    return redirect(url_for('admin.admin_users'))

@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(id):
    """Kullanıcı sil"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:#güvenlik için kendini silemez
        flash('Kendi hesabınızı silemezsiniz!', 'danger')
        return redirect(url_for('admin.admin_users'))
    
    username = user.username #username değişkeninde tut çünkü delete() sonrası user nesnesi yok olur
    db.session.delete(user)
    db.session.commit()
    flash(f'{username} kullanıcısı silindi!', 'success')
    return redirect(url_for('admin.admin_users'))

@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_post(id):
    """Yazı sil (admin)"""
    post = Post.query.get_or_404(id)
    title = post.title
    db.session.delete(post)
    db.session.commit()
    flash(f'"{title}" yazısı silindi!', 'success')
    return redirect(url_for('admin.admin_posts'))