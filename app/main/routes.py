from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm, VoteForm
from app.models import User, Post, Listing, ListingUserPref, Item, ItemUserPref
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Post succesfully submitted.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>') #user profiles
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Why you tryna follow yourself weirdo')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following  {}!'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Why you tryna unfollow yourself dude')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You unfollowed {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/dh/<listing>/search')
@login_required
def search(listing):
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    if not listing:
        posts, total = Item.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    else:
        list = Listing.query.filter_by(acronym=listing).first_or_404()
        items, total = Item.searchID(g.search_form.q.data, list.id, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    if not listing:
        return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)
    else:
        if current_user.is_authenticated:
            pref = current_user.findPref(list)
        else:
            pref = 0
        return render_template('dhlisting.html', listing=list, items=items, pref=pref)

@bp.route('/dh')
def dining():
    dh = Listing.query.filter_by(restaurant=False).order_by(Listing.percentLikes.desc())
    rest = Listing.query.filter_by(restaurant=True).order_by(Listing.percentLikes.desc())
    return render_template('dining.html', title=('Dining Halls'), listings=dh, restaurants=rest)

@bp.route('/dh/<listing>', methods=['GET', 'POST']) #dining hall info
def dhlisting(listing):
    list = Listing.query.filter_by(acronym=listing).first_or_404()
    # form = VoteForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        if current_user.is_authenticated:
            pref = current_user.findPref(list)
            if request.form['btn'] == 'Like':
                #PREF VALUES: 1 MEANS LIKE 2 MEANS DISLIKE
                #0 means neutral
                if(pref == 1): #we undo our upvote
                    current_user.changePref(list, 0)
                    list.upvotes -= 1
                elif(pref == -1): #no record in database yet
                    newpref = ListingUserPref(likePref=1)
                    newpref.child = list
                    current_user.children.append(newpref)
                    list.upvotes += 1
                elif(pref == 0):
                    current_user.changePref(list, 1)
                    list.upvotes += 1
                elif(pref == 2):
                    current_user.changePref(list, 1)
                    list.upvotes += 1
                    list.downvotes -= 1
                totalVotes = list.upvotes + list.downvotes
                if(totalVotes != 0):
                    list.percentLikes = (list.upvotes / totalVotes) * 100
                else:
                    list.percentLikes = 0
                db.session.commit()
                return redirect(url_for('main.dhlisting', listing=listing))
            elif request.form['btn'] == 'Dislike':
                if(pref == 2):
                    current_user.changePref(list, 0)
                    list.downvotes -= 1
                elif(pref == -1):
                    newpref = ListingUserPref(likePref=2)
                    newpref.child = list
                    current_user.children.append(newpref)
                    list.downvotes += 1
                elif(pref == 0):
                    current_user.changePref(list, 2)
                    list.downvotes += 1
                elif(pref == 1):
                    current_user.changePref(list, 2)
                    list.downvotes += 1
                    list.upvotes -= 1
                totalVotes = list.upvotes + list.downvotes
                if(totalVotes != 0):
                    list.percentLikes = (list.upvotes / totalVotes) * 100
                else:
                    list.percentLikes = 0
                db.session.commit()
                return redirect(url_for('main.dhlisting', listing=listing))
        else:
            flash('You must log in to do that.')
            return redirect(url_for('auth.login'))
    if current_user.is_authenticated:
        pref = current_user.findPref(list)
    else:
        pref = 0
    items = Item.query.filter_by(listing_id=list.id).order_by(Item.percentLikes.desc())
    return render_template('dhlisting.html', listing=list, pref=pref, items=items )

@bp.route('/dh/<listing>/<item>', methods=['GET', 'POST'])
def itemlisting(listing, item):
    theitem = Item.query.filter_by(id=item).first_or_404()
    if request.method == 'POST':
        if current_user.is_authenticated:
            pref = current_user.findItemPref(theitem)
            if request.form['btn'] == 'Like':
                #PREF VALUES: 1 MEANS LIKE 2 MEANS DISLIKE
                #0 means neutral
                if(pref == 1): #we undo our upvote
                    current_user.changeItemPref(list, 0)
                    theitem.upvotes -= 1
                elif(pref == -1): #no record in database yet
                    newpref = ItemUserPref(itemPref=1)
                    newpref.itemchild = theitem
                    current_user.itemchildren.append(newpref)
                    theitem.upvotes += 1
                elif(pref == 0):
                    current_user.changeItemPref(theitem, 1)
                    theitem.upvotes += 1
                elif(pref == 2):
                    current_user.changeItemPref(theitem, 1)
                    theitem.upvotes += 1
                    theitem.downvotes -= 1
                totalVotes = theitem.upvotes + theitem.downvotes
                if(totalVotes != 0):
                    theitem.percentLikes = (theitem.upvotes / totalVotes) * 100
                else:
                    theitem.percentLikes = 0
                db.session.commit()
                return redirect(url_for('main.itemlisting', listing=theitem.owner.acronym, item=item))
            elif request.form['btn'] == 'Dislike':
                if(pref == 2):
                    current_user.changeItemPref(theitem, 0)
                    theitem.downvotes -= 1
                elif(pref == -1):
                    newpref = ItemUserPref(itemPref=2)
                    newpref.itemchild = theitem
                    current_user.itemchildren.append(newpref)
                    theitem.downvotes += 1
                elif(pref == 0):
                    current_user.changeItemPref(theitem, 2)
                    theitem.downvotes += 1
                elif(pref == 1):
                    current_user.changeItemPref(theitem, 2)
                    theitem.downvotes += 1
                    theitem.upvotes -= 1
                totalVotes = theitem.upvotes + theitem.downvotes
                if(totalVotes != 0):
                    theitem.percentLikes = (theitem.upvotes / totalVotes) * 100
                else:
                    theitem.percentLikes = 0
                db.session.commit()
                return redirect(url_for('main.itemlisting', listing=theitem.owner.acronym, item=item))
        else:
            flash('You must log in to do that.')
            return redirect(url_for('auth.login'))
    if current_user.is_authenticated:
        pref = current_user.findItemPref(theitem)
    else:
        pref = 0
    return render_template('itemlisting.html', item=theitem, pref=pref, numlikes=theitem.upvotes, numdislikes=theitem.downvotes)

@bp.route('/dh/<listing>/<item>/popup')
def item_popup(listing, item):
    item = Item.query.filter_by(listing_id=list.id, id=item).first_or_404()
    return render_template('item_popup.html', item=item)
