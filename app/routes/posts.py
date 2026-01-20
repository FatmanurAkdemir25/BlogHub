from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment, Like, Bookmark
from app.utils.helpers import save_image, create_notification

bp = Blueprint('posts', __name__) #yazılar için blueprint oluşturuluyor

@bp.route('/post/<int:id>') #/post/5 gibi url ler için route (5=yazı ıd si) -- int:id url den int parametresi al
def detail(id):
    """Yazı detay sayfası"""
    post = Post.query.get_or_404(id) #id ye göre yazı bul bulamazsa 404 hatası
    post.views += 1 #görüntüleme sayısını artır
    db.session.commit() #değişiklikleri kaydet
    
    comments = Comment.query.filter_by(post_id=id).order_by( #bu yazıya ait tüm yorumları getir
        Comment.created_at.desc() #desc azalan yani yeni olan başa
    ).all() #tüm sonuçları liste olarak getir
    
    related_posts = Post.query.filter( #ilgili yazıları bul
        Post.category == post.category, #aynı kategoride olan
        Post.id != post.id, #bu yazı değil
        Post.is_published == True #yayınlanmış olan
    ).limit(3).all() # en fazla 3 tane getir
    
    return render_template('post.html', #template e 3 veri gönder
                         post=post,  #yazı
                         comments=comments, #yorumlar
                         related_posts=related_posts) #ilgili yazılar

@bp.route('/post/<int:id>/comment', methods=['POST']) #yazıya yorum ekleme route u
@login_required #sadece giriş yapmış kullanıcılar yorum yapabilir
def add_comment(id):
    """Yorum ekle"""
    post = Post.query.get_or_404(id)
    content = request.form.get('content') # content:yorum metni
    parent_id = request.form.get('parent_id', type=int) #parent_id: eğer bir yoruma cevap veriliyorsa, o yorumun id si(yoksa none)
    
    if content: #yorum boş değilse
        comment = Comment( #yeni Comment nesnesi oluştur
            content=content, 
            user_id=current_user.id,  #yorumu yapan kullanıcı
            post_id=post.id, #hangi yazıya yapıldı
            parent_id=parent_id #hangi yoruma cevap (varsa)
        )
        db.session.add(comment)
        db.session.commit() #vt ye kaydet
        
        # Bildirim oluştur
        if parent_id: #eğer bir yoruma cevap veriliyorsa
            parent_comment = Comment.query.get(parent_id) #ana yorumu bul
            if parent_comment.user_id != current_user.id: #eğer kendine cevap vermiyorsa
                create_notification( #ana yorum sahibine bildirim gönder
                    user_id=parent_comment.user_id,
                    sender_id=current_user.id,
                    notif_type='reply', # bildirim tipi reply(cevap)
                    message=f'{current_user.username} yorumunuza cevap verdi',
                    link=url_for('posts.detail', id=post.id)
                )
        else: #eğer ana yorumsa (cevap değil)
            if post.user_id != current_user.id:
                create_notification( #kendi yazısına yorum yapmıyorsa yazı sahibine bildirim gönder
                    user_id=post.user_id,
                    sender_id=current_user.id,
                    notif_type='comment', #bildirim tipi comment
                    message=f'{current_user.username} yazınıza yorum yaptı: "{post.title}"',
                    link=url_for('posts.detail', id=post.id)
                )
        
        flash('Yorumunuz eklendi!', 'success') #başarı mesajı göster
    
    return redirect(url_for('posts.detail', id=id)) #yazı detay sayfasına geri dön

@bp.route('/post/<int:id>/like', methods=['POST'])
@login_required #yazıyı beğenip beğenmeme route u
def like(id):
    """Yazıyı beğen/beğenme"""
    post = Post.query.get_or_404(id) #id ye göre yazıyı bul
    
    existing_like = Like.query.filter_by( #yazı beğenilmiş mi
        user_id=current_user.id, 
        post_id=post.id
    ).first()
    
    if existing_like: #eğer zaten beğenilmişse
        db.session.delete(existing_like) #beğeniyi sil ( unlike)
        db.session.commit()
        return jsonify({ #json response döndür (ajax için)
            'liked': False, #artık beğenilmiyor
            'likes_count': post.get_likes_count() #güncel beğeni sayısı
        })
    else: #eğer beğenilmemişse
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like) #yeni like oluştur
        db.session.commit()
        
        if post.user_id != current_user.id: #yazı sahibine bildirim gönder (kendi yazısını beğenmediyse)
            create_notification(
                user_id=post.user_id,
                sender_id=current_user.id,
                notif_type='like',
                message=f'{current_user.username} yazınızı beğendi: "{post.title}"',
                link=url_for('posts.detail', id=post.id)
            )
        
        return jsonify({ #json response liked:true , güncel beğeni sayısı
            'liked': True, 
            'likes_count': post.get_likes_count()
        })

@bp.route('/post/<int:id>/bookmark', methods=['POST'])
@login_required # yer imi (bookmark) toogle
def bookmark(id):#kaydetme
    """Yazıyı yer imlerine ekle/çıkar"""
    post = Post.query.get_or_404(id)
    
    existing_bookmark = Bookmark.query.filter_by(
        user_id=current_user.id, 
        post_id=post.id
    ).first()
    
    if existing_bookmark: #varsa sil
        db.session.delete(existing_bookmark)
        db.session.commit()
        return jsonify({'bookmarked': False})
    else: #yoksa ekle
        bookmark = Bookmark(user_id=current_user.id, post_id=post.id)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'bookmarked': True}) #json response döndür bildirim yok (çünkü private bir işlem)

@bp.route('/create', methods=['GET', 'POST'])
@login_required #sadece giriş yapmış kullanıcılar
def create():
    """Yeni yazı oluştur"""
    if request.method == 'POST': #form gönderilerini al
        title = request.form.get('title') #request.form.get():text inputlar için
        content = request.form.get('content')
        summary = request.form.get('summary')
        category = request.form.get('category')
        image = request.files.get('image') #request.files.get():dosya yükleme için
        is_published = request.form.get('is_published') == 'true' #is_published==true string i boolean a çevir (yayınla/taslak)
        
        image_filename = save_image(image) if image else None 
        #eğer resim yüklendiyse save image fonk ile kaydet resmi küçült, optimize et, benzersiz isim ver dosya adını döndür resim yoksa none
        
        post = Post( #yeni post nesnesi oluştur
            title=title,
            content=content,
            summary=summary,
            category=category,
            image=image_filename,
            user_id=current_user.id, #yazarı kaydet
            is_published=is_published
        )
        
        db.session.add(post) #vt ye ekle
        db.session.commit() # kaydet
        
        if is_published: #eğer yayınlandıysa başarı mesajı, yazı detay sayfasına git
            flash('Yazı başarıyla yayınlandı!', 'success')
            return redirect(url_for('posts.detail', id=post.id))
        else: #eğer taslaksa bilgi mesjı, taslaklar sayfasına git
            flash('Yazı taslak olarak kaydedildi!', 'info')
            return redirect(url_for('user.drafts'))
    
    return render_template('create.html')

@bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Yazıyı düzenle"""
    post = Post.query.get_or_404(id)
    
    if post.user_id != current_user.id: # yazıyı sadece sahibi düzenleyebilir
        flash('Bu yazıyı düzenleme yetkiniz yok!', 'danger') #değilse hata mesajı ve ana sayfaya yönlendir
        return redirect(url_for('main.index'))
    
    if request.method == 'POST': #post ise yanı form gönderildiyse mevcut post nesnesini düzenle
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.summary = request.form.get('summary')
        post.category = request.form.get('category')
        
        image = request.files.get('image')
        if image: #yeni resim yüklendiyse eskiyi değiştir
            image_filename = save_image(image)
            if image_filename:
                post.image = image_filename
        
        db.session.commit() #değişiklikleri kaydet(update sql) 
        flash('Yazı güncellendi!', 'success')
        return redirect(url_for('posts.detail', id=post.id)) #yazı sayfasına yönlendir
    
    return render_template('edit.html', post=post) #get ise düzenleme formunu göster mevcut verileri doldur

@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Yazıyı sil"""
    post = Post.query.get_or_404(id)
    
    if post.user_id != current_user.id: #sadece sahibi silebilir
        flash('Bu yazıyı silme yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))
    
    db.session.delete(post) #vt den sil (delete sql) -- cascade delete yani ilişkili yorum ve beğeniler de otomatik silinir (models.py deki tanımdan)
    db.session.commit()
    flash('Yazı silindi!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    """Yorum sil"""
    comment = Comment.query.get_or_404(id)
    
    if comment.post.user_id != current_user.id and not current_user.is_admin: #yazı sahibi veya admin silebilir 
        flash('Bu yorumu silme yetkiniz yok!', 'danger')
        return redirect(url_for('posts.detail', id=comment.post_id))
    
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    
    flash('Yorum silindi!', 'success')
    return redirect(url_for('posts.detail', id=post_id))