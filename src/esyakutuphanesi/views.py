# -*- coding: utf-8 -*-
import uuid
import json
import os
from datetime import datetime

from flask import render_template, send_from_directory, flash, url_for, redirect, request, jsonify, g
from flask_login import current_user, login_required, logout_user
from flask_mail import Message as MailMessage

from __init__ import app, db, mail
from forms import *
from models import *


@app.errorhandler(404)
def page_not_found(error):
    return render_template('/404.html', user=current_user), 404


@app.before_request
def before_request():
    g.user = current_user


@app.route('/categories')
@app.route('/')
def home():
    form = SearchForm()
    request_form = RequestForm()
    last_objects_shared = Stuff.query.join(User).filter(
        Stuff.approved == 1,
        Stuff.is_wanted == False,
        Stuff.owner_id == User.id,
        User.approved == True
    ).order_by(Stuff.id.desc()).limit(8)

    last_objects_wanted = Stuff.query.join(User).filter(
        Stuff.approved == 1,
        Stuff.is_wanted == True,
        Stuff.owner_id == User.id,
        User.approved == True
    ).order_by(Stuff.id.desc()).limit(8)

    return render_template(
        "index.html",
        user=current_user,
        last_objects_wanted=last_objects_wanted,
        last_objects_shared=last_objects_shared,
        form=form,
        request_form=request_form
    )


@app.route('/check_approved')
@app.route('/check_approved/<source>')
@login_required
def check_approved(source=None):
    if current_user.approved:
        return redirect(url_for('home'))
    else:
        if source == 'register':

            flash(u'Üyeliğin onay bekliyor. Onaylandığı zaman e-posta ile sana haber vereceğiz.')
            msg_body = "%s %s <br><br> %s <br> %s" % (current_user.name, current_user.email,
                                                      current_user.why,  current_user.about)
            msg = MailMessage(
                body=msg_body,
                html=msg_body,
                subject=u"Yeni Üye",
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=["bilgi@esyakutuphanesi.com"]
            )

            mail.send(msg)

        elif source == 'login':
            flash(u'Üyeliğin onay bekliyor.')
        logout_user()
        return redirect(url_for('home'))


@app.route('/search')
def search():
    form = SearchForm()
    request_form = RequestForm()
    last_objects = list()

    if request.method == 'GET':
        stuff_key = unicode(request.args.get('stuff')).lower()
        address_key = unicode(request.args.get('address')).lower()

        last_objects = Stuff.query.join(Address).join(User).filter(
            Stuff.owner_id == User.id,
            User.approved == True,
            Stuff.approved == 1,
            Address.id == Stuff.address_id,
            Stuff.title.ilike('%' + stuff_key + '%'),
            Address.detail.ilike('%' + address_key + '%')
        )

    return render_template(
        "search.html",
        user=current_user,
        last_objects=last_objects,
        form=form,
        request_form=request_form
    )


@app.route('/edit_address/<address_id>', methods=["GET", "POST"])
@app.route('/new_address', methods=["GET", "POST"])
@login_required
def edit_address(address_id=None):
    form = EditAddressForm()

    address = Address.query.filter(Address.id == address_id, Address.user == current_user).first()

    if request.args.get('status'):
        status = int(request.args.get('status'))

        if status:
            Address.query.filter(Address.id == address_id, Address.user == current_user).delete()
            db.session.commit()
            flash(u"Adres silindi.")
            return redirect(url_for("edit_profile"))

    if request.method == 'POST' and form.validate_on_submit():
        if address:
            Address.query.filter(Address.id == address_id, Address.user == current_user)\
                .update({Address.lat: form.lat.data,
                         Address.lng: form.lng.data,
                         Address.name: form.address_title.data,
                         Address.detail: unicode(form.address_str.data)})
            db.session.commit()
            flash(u"Adres güncellendi.")

        else:
            print unicode(request.form)
            address = Address(
                user=current_user,
                lat=form.lat.data,
                lng=form.lng.data,
                detail=unicode(form.address_str.data),
                name=form.address_title.data
            )
            db.session.add(address)
            db.session.commit()
            flash(u"Adres kaydedildi.")

        return redirect(url_for("edit_profile"))
    if address:
        form.fill_form(address)

    return render_template("edit_address.html", address=address,
                           action='Edit', user=current_user, form=form)


@app.route('/edit_stuff/<stuff_id>', methods=["GET", "POST"])
@app.route('/new_stuff', methods=["GET", "POST"])
@login_required
def edit_stuff(stuff_id=None):
    stuff = Stuff.query.filter(Stuff.id == stuff_id).first()
    form = EditStuffForm()
    is_new = True
    is_wanted = bool(request.args.get('is_wanted'))
    # if is_wanted == 'true':
    #     form.is_wanted.data = 'True'

    address_choices = []
    if current_user.addresses:
        address_choices = [(address.id, address.detail)
                           for address in current_user.addresses]
    address_choices += [(-1, u'Yeni adres: Haritadan sağ tıklayarak seçebilirsiniz.')]
    #else:
    #    flash('Adres girmeniz gerekiyor')
    #    return redirect(url_for("new_address",
    #                            next=request.script_root+request.path))

    form.address.choices = address_choices

    if current_user.groups:
        group_choices = [(membership.group.id, membership.group.name)
                         for membership in current_user.groups]
        group_choices = [(-1, u'Herkese açık')] + group_choices
    else:
        group_choices = [(-1, u'Herkese açık')]

    form.group.choices = group_choices

    categories = Category.query.order_by(Category.name)
    category_choices = [(category.id, category.name)
                        for category in categories]
    form.category.choices = category_choices
    if stuff:
        category = Category.query. \
            filter(Category.id == stuff.category_id).first()
    else:
        category = categories[0]
    stuff_types = category.type_list
    stuff_type_choices = [(stuff_type.id, stuff_type.name)
                          for stuff_type in stuff_types]
    form.stuff_type.choices = stuff_type_choices

    if request.args.get('status'):
        status = int(request.args.get('status'))

        if status:
            Stuff.query.filter(Stuff.id == stuff_id).\
                update({Stuff.approved: status})
            db.session.commit()
            flash(u"Eşya kaldırıldı.")
            return redirect(url_for("my_stuff"))

    if request.method == 'POST':
        category = Category.query.\
            filter(Category.id == form.category.data).first()

        stuff_types = category.type_list
        stuff_type_choices = [(stuff_type.id, stuff_type.name)
                              for stuff_type in stuff_types]
        form.stuff_type.choices = stuff_type_choices

        if form.validate_on_submit():
            if form.address.data == -1:
                address = Address(
                    user=current_user,
                    lat=request.form.get('lat'),
                    lng=request.form.get('lng'),
                    detail=unicode(request.form.get('address_str')),
                    name="addr"
                )
                db.session.add(address)
            else:
                address = Address.query.\
                    filter(Address.id == form.address.data).\
                    first()

            if stuff:
                stuff.title = form.title.data
                stuff.detail = form.detail.data
                stuff.stuff_address = address
                stuff.category_id = form.category.data
                stuff.type_id = form.stuff_type.data
                #stuff.is_wanted = form.is_wanted.data == 'True'
                flash(u"Eşya güncellendi.")

            else:
                group_id = None if form.group.data == -1 else form.group.data
                stuff = Stuff(
                    title=form.title.data,
                    detail=form.detail.data,
                    stuff_address=address,
                    owner=current_user,
                    category_id=form.category.data,
                    type_id=form.stuff_type.data,
                    group_id=group_id,
                    is_wanted=form.is_wanted.data == 'True'
                )
                db.session.add(stuff)
                db.session.commit()

                photo_file = form.photo.data

                stuff_id = str(stuff.id)

                if photo_file:
                    file_ext = get_file_extension(photo_file.filename)
                    generated_name = str(uuid.uuid1()) + '.' + file_ext

                    folder_path = app.config['UPLOADS_FOLDER'] + '/stuff/' + stuff_id + '/'

                    new_folder = os.path.dirname(folder_path)
                    if not os.path.exists(new_folder):
                        os.makedirs(new_folder)

                    filepath = os.path.join(folder_path, generated_name)
                    photo_file.save(filepath)

                    file_new_name = 'stuff/' + stuff_id + '/' + generated_name

                # else:
                #     generated_name = str(form.category.data)+'.jpg'
                #     file_new_name = generated_name

                    new_photo = StuffPhoto(
                        owner=current_user,
                        filename=file_new_name,
                        stuff=stuff
                    )
                    db.session.add(new_photo)
                    db.session.commit()

                # flash(u"Eşya kaydedildi.")

                msg_body = u"Eşya ekleyen: %s %s <br><br>Eşya başlık: %s<br> Eşya detay : %s" \
                           % (current_user.name, current_user.email, stuff.title, stuff.detail)
                msg = MailMessage(
                    body=msg_body,
                    html=msg_body,
                    subject=u"Yeni Eşya",
                    sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                    recipients=["bilgi@esyakutuphanesi.com"]
                )

                mail.send(msg)
                return render_template("onaybekliyor.html", user=current_user)

            tags = form.tags.data.split(',')
            for t in tags:
                if t > '':
                    new_tag = Tag(stuff=stuff, name=t)
                    db.session.add(new_tag)

            db.session.commit()

            if stuff_id is None:
                return redirect(url_for('edit_stuff', stuff_id=stuff.id))

    if stuff:
        is_new = False

        if stuff.group_id > 0:
            group_choices = [(stuff.group_id, stuff.group.name)]
        else:
            group_choices = [(-1, u'Herkese açık')]

        form.group.choices = group_choices
        form.fill_form(stuff)

    return render_template(
        "edit_stuff.html",
        user=current_user,
        is_wanted=is_wanted,
        form=form,
        action='Edit',
        stuff=stuff,
        is_new=is_new
    )


@app.route('/my_stuff')
@login_required
def my_stuff():
    return render_template("my_stuff.html", user=current_user)


@app.route('/get_stuff_types/<category_id>')
@app.route('/get_stuff_types')
def get_stuff_types(category_id=None):
    if category_id:
        category = Category.query.filter(Category.id == category_id).first()
        stuff_types = category.type_list
    else:
        stuff_types = StuffType.query.order_by(StuffType.name)

    stuff_type_choices = [{"id": stuff_type.id, "name": stuff_type.name}
                          for stuff_type in stuff_types]
    stuff_type_choices_json = json.dumps(stuff_type_choices)

    return stuff_type_choices_json


@app.route('/get_categories')
@app.route('/get_categories/<type_id>')
def get_categories(type_id=None):
    if type_id:
        stuff_type = StuffType.query.filter(StuffType.id == type_id).first()
        categories = stuff_type.category_list
    else:
        categories = Category.query.order_by(Category.name)

    category_list = [{"id": category.id, "name": category.name}
                     for category in categories]
    category_list_json = json.dumps(category_list)

    return category_list_json


@app.route('/show_stuff/<stuff_id>')
@login_required
def show_stuff(stuff_id):
    request_form = RequestForm()
    is_wanted = request.args.get('is_wanted')

    stuff = Stuff.query.join(User).filter(
        Stuff.id == stuff_id,
        Stuff.owner_id == User.id,
        User.approved == True
    ).first()

    if stuff.approved == 1:
        stuff_address = Address.query.filter(Address.id == stuff.address_id).first()
        reviews = Review.query.filter(Review.request_id == Request.id, Request.stuff_id == stuff_id)

        user_rates = Review.query.filter(Review.reviewed_user_id == stuff.owner_id)
        rating_count = user_rates.count()

        total_rating = 0
        if rating_count > 0:
            for rate in user_rates:
                if rate.rating:
                    total_rating += rate.rating
            avg_rate = total_rating / rating_count
        else:
            avg_rate = 0

        return render_template(
            "show_stuff.html",
            stuff_address=stuff_address,
            user=current_user,
            rating=avg_rate,
            request_form=request_form,
            is_wanted=is_wanted,
            stuff=stuff,
            reviews=reviews
        )
    elif stuff.approved == 0 and stuff.owner == current_user:
        return redirect(url_for("edit_stuff", stuff_id=stuff_id))

    else:
        # flash(u"Eşya kaldırılmış.")
        return render_template('/404.html', user=current_user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        if current_user.id == int(form.userid.data):
            photo_file = form.photo.data

            if photo_file:
                file_ext = get_file_extension(photo_file.filename)
                generated_name = str(uuid.uuid1()) + '.' + file_ext

                current_user_id = str(current_user.id)
                folder_path = app.config['UPLOADS_FOLDER'] + '/user/' + current_user_id + '/'
                new_folder = os.path.dirname(folder_path)
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder)

                filepath = os.path.join(folder_path, generated_name)

                photo_file.save(filepath)

                new_photo = Photo(owner=current_user, filename='user/' + current_user_id + '/' + generated_name)
                db.session.add(new_photo)
                db.session.commit()

                User.query.filter(User.id == current_user.id).\
                    update({User.photo: new_photo.filename})

            User.query.filter(User.id == current_user.id).\
                update({User.name: form.name.data,
                        User.email: form.email.data,
                        User.phone_number: form.phone_number.data,
                        User.about: form.about.data})
            db.session.commit()

            flash(u"Profil güncellendi.", current_user.id)

    form.fill_form(current_user)

    return render_template(
        'edit_profile.html',
        form=form,
        user=current_user
    )


@app.route('/photos/<path:filename>')
def photos_static(filename):
    return send_from_directory(app.root_path + '/static/photos/', filename)


def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1]


@app.route('/category/<category_name>/')
def category_view(category_name=None):
    request_form = RequestForm()
    is_wanted = request.args.get('is_wanted')

    if category_name == "Hepsi":
        if is_wanted is None:
            stuff_list = Stuff.query.join(User).filter(
                Stuff.approved == 1,
                Stuff.owner_id == User.id,
                User.approved == True
            ).order_by(Stuff.id.desc())
        else:
            stuff_list = Stuff.query.join(User).filter(
                Stuff.is_wanted == is_wanted,
                Stuff.approved == 1,
                Stuff.owner_id == User.id,
                User.approved == True
            ).order_by(Stuff.id.desc())
        category_value = 'all'
    else:
        category = Category.query.\
            filter(Category.name == category_name).first()
        #stuff_list = category.stuff_list
        if is_wanted is None:
            stuff_list = Stuff.query.join(User).filter(
                Stuff.category == category,
                Stuff.approved == 1,
                Stuff.owner_id == User.id,
                User.approved == True
            ).order_by(Stuff.id.desc())

        else:
            stuff_list = Stuff.query.join(User).filter(
                Stuff.category == category,
                Stuff.is_wanted == is_wanted,
                Stuff.approved == 1,
                Stuff.owner_id == User.id,
                User.approved == True
            ).order_by(Stuff.id.desc())

        category_value = category.id

    params = {
        'category': {
            'type': 'category',
            'value': category_value
        },
        'stuff_type': {
            'type': 'stuff_type',
            'value': 'all'
        },
        'is_wanted': {
            'type': 'is_wanted',
            'value': is_wanted if is_wanted is not None else 2
        }
    }

    return render_template(
        "browse.html",
        user=current_user,
        stuff_list=stuff_list,
        params=params,
        request_form=request_form
    )

#@app.route('/stuff_type/<type_name>/')
#def stuff_type_view(type_name=None):
#    stuff_type = StuffType.query.\
#        filter(StuffType.name == type_name).first()
#    stuff_list = stuff_type.stuff_list
#    params = {
#        'stuff_type': {
#            'type': 'stuff_type',
#            'value': stuff_type.id
#        },
#    }
#    return render_template("browse.html", user=current_user,
#                           stuff_list=stuff_list, params=params)


@app.route('/category/<category_name>/type/<type_name>')
def category_stuff_type_view(category_name, type_name):
    request_form = RequestForm()
    is_wanted = request.args.get('is_wanted')
    stuff_type = StuffType.query.\
        filter(StuffType.name == type_name).first()
    category = Category.query.\
        filter(Category.name == category_name).first()
    if is_wanted is None:
        stuff_list = Stuff.query.join(User).join(Category).join(StuffType).filter(
            Category.id == category.id,
            StuffType.id == stuff_type.id,
            Stuff.approved == 1,
            Stuff.owner_id == User.id,
            User.approved == True
        ).order_by(Stuff.id.desc())
            # filter(Category.id == category.id)
    else:
        stuff_list = Stuff.query.join(User).join(Category).join(StuffType).filter(
            Category.id == category.id,
            StuffType.id == stuff_type.id,
            Stuff.approved == 1,
            Stuff.is_wanted == is_wanted,
            Stuff.owner_id == User.id,
            User.approved == True
        ).order_by(Stuff.id.desc())
            # filter(Category.id == category.id).\
            # filter(Stuff.is_wanted == is_wanted)

    params = {
        'category': {
            'type': 'category',
            'value': category.id
        },
        'stuff_type': {
            'type': 'stuff_type',
            'value': stuff_type.id
        },
        'is_wanted': {
            'type': 'is_wanted',
            'value': is_wanted if is_wanted is not None else 2
        }
    }

    return render_template(
        "browse.html",
        user=current_user,
        stuff_list=stuff_list,
        params=params,
        request_form=request_form
    )


@app.route('/my_messages')
@login_required
def my_messages():
    return render_template("my_messages.html", user=current_user)


@app.route('/unread_messages')
@login_required
def get_unread_messages():
    message_count = Message.query.filter(Message.to_user == current_user,
                                         Message.status == 0).count()
    return jsonify(count=message_count)


@app.route('/conversation/<conversation_id>', methods=["GET", "POST"])
@login_required
def show_conversation(conversation_id):
    conversation = Conversation.query.\
        filter(Conversation.id == conversation_id).first()

    if current_user not in conversation.users:
        return redirect('/my_messages')

    else:
        form = ConversationForm()
        if request.method == 'POST' and form.validate_on_submit():

            if current_user.id == conversation.request.user.id:
                to_user = conversation.request.from_user
            else:
                to_user = conversation.request.user

            print to_user.id
            new_message = Message(
                from_user=current_user,
                to_user=to_user,
                conversation=conversation,
                txt=form.message.data
            )
            db.session.add(new_message)
            db.session.commit()

            Conversation.query.filter(Conversation.id == new_message.conversation_id)\
                .update({Conversation.updated_at: new_message.created_at})
            db.session.commit()

            msg_body = render_template('email/conversation.txt', user=to_user, from_user=current_user.name,
                                       stuff_title=conversation.title, conversation=new_message)

            html_msg = render_template('email/conversation.html', user=to_user, from_user=current_user.name,
                                       stuff_title=conversation.title, conversation=new_message)

            # msg_body = u'%s sana mesaj gönderdi. <br><br> esyakutuphanesi.com'\
            #            % current_user.name
            # html_msg = u'%s sana mesaj gönderdi. <br><br> Mesajı okumak için' \
            #            u' <a href="http://esyakutuphanesi.com/conversation/{{conversation_id}}">tıkla!</a>' \
            #            % current_user.name

            msg_subject = u"Mesajın var"

            msg = MailMessage(
                body=msg_body,
                html=html_msg,
                subject=msg_subject,
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=[to_user.email]
            )

            mail.send(msg)

        Message.query.filter(
            Message.conversation_id == conversation_id,
            Message.status == 0,
            Message.to_user == current_user
        ).update({Message.status: 1})
        db.session.commit()

        form.message.data = None

        review_form = ReviewForm()

        if request.args.get('status'):
            status = int(request.args.get('status'))
        else:
            status = 0
        if status > 0 and \
                (conversation.request.stuff.owner == current_user or conversation.request.from_user_id == current_user.id):
            if conversation.request.stuff.status == 1:
                if status == 1 and conversation.request.status == 0:
                    flash(u'Eşyan şu anda ödünç olarak bir başka kullanıcıda.')
                    conversation.request.stuff.status = 0
                    conversation.request.status = 1
                    conversation.request.given_at = datetime.utcnow()
                    db.session.commit()
            elif status == 2 and conversation.request.status == 1:
                flash(u'Eşyayı geri aldınız.')
                conversation.request.stuff.status = 1
                conversation.request.status = 2
                conversation.request.returned_at = datetime.utcnow()
                db.session.commit()
            else:
                flash(u'Eşya zaten başkasına verilmiş.')

        wanted_stuff = StuffPhoto.query.filter(StuffPhoto.stuff_id == conversation.request.stuff_id).first()
        review_form.request_id.data = conversation.request_id
        return render_template(
            "conversation.html",
            user=current_user,
            wanted_stuff=wanted_stuff,
            form=form,
            action='Edit',
            conversation=conversation,
            review_form=review_form
        )


@app.route('/make_request/<stuff_id>', methods=['GET', 'POST'])
@app.route('/make_request', methods=['POST'])
@login_required
def make_request(stuff_id=None):
    form = RequestForm()
    message = None
    return_url = request.form['return_url']
    if form.validate_on_submit():
        message = form.message.data
        stuff_id = form.stuff_id.data
        duration = int(form.duration.data)
        unit = int(form.unit.data)

        address = Address.query.filter(Address.user_id == current_user.id).first()

        if stuff_id is None or not (stuff_id > ''):
            flash(u'İstek gönderilemedi.')
            return redirect(return_url)
        stuff = Stuff.query.filter(Stuff.id == stuff_id).first()

        if stuff.is_wanted is False and address is None:
            flash(u'Ödünç istemek için adres girmelisin.')
            return redirect(url_for('edit_address'))

        else:
            if stuff.is_wanted == True:
                user = stuff.owner
                from_user = current_user
            else:
                user = current_user
                from_user = stuff.owner

            new_request = Request(
                stuff_id=stuff_id,
                user_id=user.id,
                from_user_id=from_user.id,
                duration=(duration * unit)
            )

            db.session.add(new_request)
            new_conversation = Conversation(
                title='%s' % stuff.title,
                users=[current_user, stuff.owner],
                request=new_request
            )

            db.session.add(new_conversation)

            new_message = Message(
                from_user=current_user,
                to_user=stuff.owner,
                conversation=new_conversation,
                txt=message
            )

            db.session.add(new_message)

            db.session.commit()

            msg_body = render_template('email/request.txt', to_user=user, from_user=from_user,
                                       stuff=stuff, conversation_url=new_conversation.url)

            html_msg = render_template('email/request.html', to_user=user, from_user=from_user,
                                       stuff=stuff, conversation_url=new_conversation.url)
            if stuff.is_wanted:
                msg_subject = u"%s sana %s ödünç vermek istiyor" % (from_user.name, stuff.title)

            else:
                msg_subject = u"%s için bir talip var!" % stuff.title

            msg = MailMessage(
                body=msg_body,
                html=html_msg,
                subject=msg_subject,
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=[stuff.owner.email]
            )

            mail.send(msg)

            return redirect(url_for('my_messages'))

    else:
        flash(u'İstek gönderilemedi. Kaç gün için ödünç istediğini girmelisin.')
        return redirect(return_url)


@app.route('/moderation')
@login_required
def moderation():
    action = request.args.get("action")
    id = request.args.get("id")

    user_action = request.args.get("user_action")
    user_id = request.args.get("user_id")

    new_user = User.query.filter(User.id > 0).order_by(User.id.desc()).limit(40)

    if action == 'approve' and id > 0:
        if 'admin' in current_user.roles:
            stuff = Stuff.query.filter(Stuff.approved == 0,
                                       Stuff.id == id). \
                order_by(Stuff.id.desc()).first()
        else:
            stuff = Stuff.query.join(Group).join(GroupMembership) \
                .filter(GroupMembership.user_id == current_user.id,
                        GroupMembership.is_moderator,
                        Stuff.id == id,
                        Stuff.approved == 0). \
                order_by(Stuff.id.desc()).first()
        if stuff:
            stuff.approved = 1
            db.session.commit()

            msg_body = render_template('email/approved.txt', user=stuff.owner, stuff=stuff)

            html_msg = render_template('email/approved.html', user=stuff.owner, stuff=stuff)

            msg_subject = u"Eşyan artık sitede!"

            msg = MailMessage(
                body=msg_body,
                html=html_msg,
                subject=msg_subject,
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=[stuff.owner.email]
            )

            mail.send(msg)

            flash(u"Eşya onaylandı ve e-posta gönderildi!")

    if user_action == 'approve_user' and user_id > 0:
        unapproved_user = User.query.filter(User.approved == False, User.id == user_id). \
            order_by(User.id.desc()).first()

        if unapproved_user:
            unapproved_user.approved = True
            db.session.commit()

            msg_body = render_template('email/welcome.txt', user=unapproved_user)
            html_msg = render_template('email/welcome.html', user=unapproved_user)

            msg_subject = u"Hoşgeldin!"
            msg = MailMessage(
                body=msg_body,
                html=html_msg,
                subject=msg_subject,
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=[unapproved_user.email]
            )

            mail.send(msg)

            flash(u"Kullanıcı onaylandı ve e-posta gönderildi!")

    if 'admin' in current_user.roles:
        last_objects = Stuff.query.filter(Stuff.id > 0).\
            order_by(Stuff.id.desc()).limit(40)

    else:
        last_objects = Stuff.query.join(Group).join(GroupMembership)\
            .filter(GroupMembership.user_id == current_user.id,
                    GroupMembership.is_moderator).order_by(Stuff.id.desc()).limit(40)

    return render_template(
        "moderation.html",
        user=current_user,
        new_user=new_user,
        last_objects=last_objects
    )


@app.route('/profile/<user_id>')
@app.route('/profile')
@login_required
def get_profile(user_id=None):
    if user_id is None:
        user_id = current_user.id

    request_form = RequestForm()
    user_profile = User.query.filter(User.id == user_id).first()

    if user_profile:

        user_stuff_shared = Stuff.query.join(User).\
            filter(Stuff.owner_id == user_id, Stuff.is_wanted == False, Stuff.approved == 1,
                   Stuff.owner_id == User.id, User.approved == True).order_by(Stuff.id.desc())
        user_stuff_wanted = Stuff.query.join(User).\
            filter(Stuff.owner_id == user_id, Stuff.is_wanted == True, Stuff.approved == 1,
                   Stuff.owner_id == User.id, User.approved == True).order_by(Stuff.id.desc())

        reviews = Review.query.filter(Review.reviewed_user_id == user_id)
        reviews_count = reviews.count()

        total_rating = 0
        if reviews_count > 0:
            for review in reviews:
                if review.rating:
                    total_rating += review.rating
            avg_rate = total_rating / reviews_count
        else:
            avg_rate = 0

        users_group = Group.query.join(GroupMembership).\
            filter(GroupMembership.group_id == Group.id,
                   GroupMembership.user_id == user_id)

        returned_request = Request.query.filter(Request.from_user_id == user_id)\
            .join(Conversation)\
            .filter(Conversation.request_id == Request.id).join(Message)\
            .filter(Message.conversation_id == Conversation.id, Message.from_user_id == user_id)\
            .group_by(Message.conversation_id, Request.id)\
            .count()

        if returned_request > 0:
            # returned_request = int(returned_request)
            # returned_request = 1
            # print returned_request

            request_from_me = Request.query.filter(Request.from_user_id == user_id).count()
            request_from_me = int(request_from_me)
            # print request_from_me.count()

            return_ratio = (returned_request * 100 / request_from_me)

            # print return_ratio
        else:
            return_ratio = 0

        return render_template(
            "profile.html",
            user_stuff_shared=user_stuff_shared,
            user_stuff_wanted=user_stuff_wanted,
            users_group=users_group,
            user_profile=user_profile,
            user=current_user,
            rating=avg_rate,
            request_form=request_form,
            return_ratio=return_ratio
        )

    else:
        return render_template('/404.html', user=current_user)


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    form = CreateGroupForm()
    if request.method == 'POST' and form.validate_on_submit():
        group_info = Group(
            name=request.form.get('group_name'),
            description=request.form.get('text'),
            logo="logo"
        )
        db.session.add(group_info)
        db.session.commit()

        # mail gelsin tabi burda bize.

        flash(u"Grup kurma isteğiniz gönderildi :)")

    return render_template("groups.html", form=form, user=current_user)


@app.route('/group/<group_id>')
@login_required
def group(group_id):
    group_info = Group.query.filter(Group.id == group_id).first()

    group_shares = Stuff.query.filter(Stuff.group_id == group_id)

    group_members = User.query.join(GroupMembership).\
        filter(GroupMembership.group_id == group_id, User.id == GroupMembership.user_id)

    for members_photos in group_members:
        photos = Photo.query.filter(Photo.owner_id == members_photos.id)

        return render_template("group.html", group_info=group_info, group_shares=group_shares,
                               group_members=group_members, photos=photos, user=current_user)


@app.route('/invite', methods=["GET", "POST"])
@login_required
def invite():
    form = InvitationForm()

    if request.method == 'POST' and form.validate_on_submit():

        emails = request.form.get('emails')
        message = request.form.get('message')

        invite_info = Invitations(
            user_id=current_user.id,
            emails=emails,
            message=message
        )

        db.session.add(invite_info)
        db.session.commit()

        email_list = emails.split()

        for email in email_list:
            msg_body = '%s <br><br> %s <br><br> esyakutuphanesi.com'\
                       % (current_user.name, message)
            html_msg = '%s <br><br> %s <br><br> <a href="http://esyakutuphanesi.com/">esyakutuphanesi.com</a>' \
                       % (current_user.name, message)
            msg_subject = u"%s seni Eşya Kütüphanesi'ne davet ediyor!" % current_user.name
            msg = MailMessage(
                body=msg_body,
                html=html_msg,
                subject=msg_subject,
                sender=(u"Eşya Kütüphanesi", "no-reply@esyakutuphanesi.com"),
                recipients=[email]
            )

            mail.send(msg)

        flash(u"Davetini ilettik!")
        return redirect(url_for('invite'))

    return render_template("invite.html", form=form, user=current_user)


@app.route('/review', methods=["GET", "POST"])
@login_required
def review():
    form = ReviewForm()
    conversation_id = request.form.get('conversation_id')

    if request.method == 'POST' and form.validate_on_submit():
        rating = request.form.get('rate')

        rq = Request.query. \
            filter(Request.id == form.request_id.data).first()

        # reviewed_user_id = rq.user_id if rq.user_id == current_user.id \
        #     else rq.from_user_id

        reviewed_user_id = rq.from_user_id

        new_review = Review(
            user_id=current_user.id,
            reviewed_user_id=reviewed_user_id,
            request_id=rq.id,
            comment=form.comment.data,
            rating=rating
        )

        db.session.add(new_review)
        db.session.commit()
        flash(u"Yorumunuz eklendi :)")
        return redirect('/show_stuff/%s' % rq.stuff_id)

    flash(u"Mesaj alanını boş bıraktınız.")
    return redirect('/conversation/%s' % conversation_id)


@app.route('/masalgibi')
def fairytail():
    return render_template("masalgibi.html", user=current_user)


@app.route('/purpose')
def purpose():
    return render_template("purpose.html", user=current_user)


@app.route('/press')
def press():
    return render_template("press.html", user=current_user)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get('user_name')
        email = request.form.get('user_email')
        message = request.form.get('message')

        msg_body = "%s %s <br><br> %s" % (name, email, message)
        msg = MailMessage(
            body=msg_body,
            html=msg_body,
            subject=u"İletişime geçmek isteyen var",
            sender=(name, email),
            recipients=["bilgi@esyakutuphanesi.com", "ezgi@esyakutuphanesi.com"]
        )

        mail.send(msg)

        flash(u"E-postan gönderildi!")
        return redirect(url_for('contact'))

    return render_template("contact.html", form=form, user=current_user)


@app.route('/companies')
def companies():
    return render_template("for_companies.html", user=current_user)


@app.route('/universities')
def universities():
    return render_template("for_universities.html", user=current_user)


@app.route('/events')
def events():
    return render_template("events.html", user=current_user)


@app.route('/sos')
def sos():
    return render_template("sos.html", user=current_user)


@app.route('/user_agreement')
def user_agreement():
    return render_template("user_agreement.html", user=current_user)


@app.route('/kurulus')
def organization():
    return render_template("organization.html", user=current_user)


@app.route('/girisim_yolu')
def enterprise_path():
    return render_template("enterprise_path.html", user=current_user)


@app.route('/ekip_ve_gonulluluk')
def team_and_volunteering():
    return render_template("team_and_volunteering.html", user=current_user)


@app.route('/stats')
def stats_view():
    user_count = User.query.count()
    approved_user_count = User.query.filter(User.approved == True).count()
    monthly_user_count = User.query.filter(User.registered_at >= '2014-12-01',
                                           User.registered_at <= '2014-12-31').count()
    stuff_count = Stuff.query.filter(Stuff.approved == 1).count()
    user_with_stuff_count = Stuff.query.filter(Stuff.approved == 1).distinct(Stuff.owner_id).count()
    request_count = Request.query.count()
    request_ok_count = Request.query.filter(Request.status != 0).count()

    return render_template(
        "stats.html",
        user=current_user,
        user_count=user_count,
        approved_user_count=approved_user_count,
        monthly_user_count=monthly_user_count,
        stuff_count=stuff_count,
        user_with_stuff_count=user_with_stuff_count,
        request_count=request_count,
        request_ok_count=request_ok_count
    )

@app.route('/destekle', methods=["GET", "POST"])
def destekle():
    form = ContactForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get('user_name')
        email = request.form.get('user_email')
        message = request.form.get('message')

        msg_body = "%s %s <br><br> %s" % (name, email, message)
        msg = MailMessage(
            body=msg_body,
            html=msg_body,
            subject=u"Destekliyorum",
            sender=(name, email),
            recipients=["bilgi@esyakutuphanesi.com", "ezgi@esyakutuphanesi.com"]
        )

        mail.send(msg)

        flash(u"E-postan gönderildi!")
        return redirect(url_for('home'))

    return render_template("destekle.html", form=form, user=current_user)