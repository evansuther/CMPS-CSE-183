# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

import datetime

class Post(object):
    """Simple class to create synthetic posts"""
    def __init__(self):
        pass

def attacker():
    """This controller simply produces the attack page for Form 1.
    The interesting bits are found in the corresponding view."""
    return dict()

def simple_index():
    """Unlike the real index, this does not take data from the database."""
    post1 = Post()
    post1.id = 1
    post1.post_title = "Synthetic post 1 title"
    post1.post_content = "Synthetic post 1 content"
    post1.post_author = "luca@ucsc.edu"
    post1.post_time = datetime.datetime.utcnow()
    post2 = Post()
    post2.id = 2
    post2.post_title = "Synthetic post 2 title"
    post2.post_content = "Synthetic post 2 content"
    post2.post_author = "luca@ucsc.edu"
    post2.post_time = datetime.datetime.utcnow()
    return dict(
        rows=[post1, post2]
    )


@auth.requires_login()
def setup():
    """Inserts a couple of posts just to bring the database to a known state.
    This is done for debugging purposes ony, and should not be part of a real web site."""
    db(db.post).delete() # Deletes the content of the post table.
    db.post.insert(post_title="First Post",
                   post_content="Content of first post")
    db.post.insert(post_title="Second Post",
                   post_content="Content of second post")
    # We don't need a view if we don't return a dictionary.
    return "ok"


def index():
    """Displays the list of rows"""
    rows = db(db.post).select()
    return dict(
        rows=rows,
    )


@auth.requires_login()
def add1():
    """INSECURE -- form does not contain token -- do not use."""
    """Very simple way to insert records."""
    logger.info("Request method: %r", request.env.request_method)
    if request.env.request_method == 'POST':
        # This is a postback.  Insert the record.
        logger.info("We are inserting: title: %r content: %r" % (
            # I could also access the title via request.post_vars.post_title,
            # but I don't care to differentiate betw post and get variables.
            request.vars.post_title, request.vars.post_content
        ))
        db.post.insert(
            post_title=request.vars.post_title,
            post_content=request.vars.post_content
        )
        redirect(URL('default', 'index'))
    else:
        # This is a GET request.  Returns the form.
        return dict()


@auth.requires_login()
def add2():
    """More sophisticated way, in which we use web2py to come up with the form."""
    form = SQLFORM.factory(
        Field('post_title'),
        Field('post_content', 'text'),
    )
    # We can process the form.  This will check that the request is a POST,
    # and also perform validation, but in this case there is no validation.
    if form.process().accepted:
        # We insert the result, as in add1.
        db.post.insert(
            post_title=form.vars.post_title,
            post_content=form.vars.post_content
        )
        # And we load default/index via redirect.
        redirect(URL('default', 'index'))
    # We ask web2py to lay out the form for us.
    logger.info("My session is: %r" % session)
    return dict(form=form)


@auth.requires_login()
def add3():
    """More sophisticated way, in which we use web2py to come up with the form."""
    form = SQLFORM(db.post)
    # We can process the form.  This will check that the request is a POST,
    # and also perform validation, but in this case there is no validation.
    # THIS process() also inserts.
    if form.process().accepted:
        # NOT NEEDED We insert the result, as in add1.
        # db.post.insert(
        #     post_title=form.vars.post_title,
        #     post_content=form.vars.post_content
        # )
        # And we load default/index via redirect.
        redirect(URL('default', 'index'))
    # We ask web2py to lay out the form for us.
    logger.info("My session is: %r" % session)
    return dict(form=form)





# We require login.
@auth.requires_login()
def edit():
    """Allows editing of a post.  URL form: /default/edit/<n> where n is the post id."""

    # For this controller only, we hide the author.
    db.post.post_author.readable = False

    # post = db(db.post.id == int(request.args[0])).select().first()

    post = db.post(request.args(0))
    # We must validate everything we receive.
    if post is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'index'))
    # One can edit only one's own posts.
    if post.post_author != auth.user.email:
        logging.info("Attempt to edit some one else's post by: %r" % auth.user.email)
        redirect(URL('default', 'index'))
    # Now we must generate a form that allows editing the post.
    form = SQLFORM(db.post, record=post)
    if form.process().accepted:
        # The deed is done.
        redirect(URL('default', 'index'))
    return dict(form=form)

def view1():
    post = db.post(request.args(0))
    if post is None:
        redirect(URL('default', 'index'))
    form = SQLFORM(db.post, record = post, readonly=True)
    return dict(form=form)


def view2():
    post = db.post(request.args(0))
    return dict(post=post)


def urls():
    # request.args[1]
    # request.vars.person
    return dict()


# /start/default/delete/2
@auth.requires_signature()
@auth.requires_login()
def delete():
    post = db.post(request.args(0))
    # We must validate everything we receive.
    if post is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'index'))
    # One can edit only one's own posts.
    if post.post_author != auth.user.email:
        logging.info("Attempt to edit some one else's post by: %r" % auth.user.email)
        redirect(URL('default', 'index'))
    db(db.post.id == post.id).delete()
    redirect(URL('default', 'index'))

@auth.requires_signature()
@auth.requires_login()
def toggle_star():
    star_record = db((db.star.post_id == int(request.args[0])) &
        (db.star.user_id == auth.user_id)).select().first()
    if star_record is not None:
        # Removes star.
        db(db.star.id == star_record.id).delete()
    else:
        # Adds the star.
        db.star.insert(
            user_id = auth.user.id,
            post_id = int(request.args[0]))
    redirect(URL('default', 'index_inefficient'))



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


