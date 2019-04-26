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

@auth.requires_login()
def setup():
    
    db(db.product).delete() # Deletes the content of the post table.
    db.product.insert(prod_name="first prod",
                   prod_desc="Content of first product")
    db.product.insert(prod_name="second prod",
                   prod_desc="Content of second product")
    # We don't need a view if we don't return a dictionary.
    return "ok"

def index():
    #redir to appname/default/listall if you end up on index
    redirect(URL('default', 'listall')) 
    """Displays the list of rows"""
    rows = db(db.post).select()
    prods = db(db.product).select()
    return dict(
        rows=rows, prods = prods
    )

def homepage():
    """Displays the list of rows"""
    prods = db(db.product.prod_starred == True).select()
    return dict(
         prods = prods
    )


@auth.requires_login()
def add_product():
    """More sophisticated way, in which we use web2py to come up with the form."""
    form = SQLFORM(db.product)
    # We can process the form.  This will check that the request is a product,
    # and also perform validation, but in this case there is no validation.
    # THIS process() also inserts.
    if form.process().accepted:
        # And we load default/listall via redirect.
        redirect(URL('default', 'listall'))
    # We ask web2py to lay out the form for us.
    logger.info("My session is: %r" % session)
    return dict(form=form)





# We require login.
@auth.requires_login()
def edit_product():
    """Allows editing of a post.  URL form: /default/edit/<n> where n is the post id."""

    # For this controller only, we hide the author.
    db.product.prod_poster.readable = False
    db.product.prod_post_time.writable =False
    db.product.prod_starred.readable, db.product.prod_starred.writable =False, False

    # post = db(db.post.id == int(request.args[0])).select().first()

    product = db.product(request.args(0))
    # We must validate everything we receive.
    if product is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'listall'))
    # One can edit only one's own posts.
    if product.prod_poster != auth.user.email:
        logging.info("Attempt to edit some one else's product by: %r" 
                        % auth.user.email)
        redirect(URL('default', 'listall'))
    # Now we must generate a form that allows editing the post.
    form = SQLFORM(db.product, record=product,
                    labels = {'prod_name': 'Product Name',
                    'prod_desc':'Description',
                    'prod_in_stock':'In Stock',
                     'prod_sold':'Sold', 
                     'prod_price':'Price(for consumer)', 
                     'prod_cost':'Cost(for producer)'},
                   )
    form.add_button('Back', URL('default', 'listall'))
    if form.process().accepted:
        # The deed is done.
        redirect(URL('default', 'listall'))
    return dict(form=form)

def mychecks(form):
    """Performs form validation.  
    See http://www.web2py.com/books/default/chapter/29/07/forms-and-validators#onvalidation 
    for details."""
    # form.vars contains what the user put in.
    if form.vars.view_count % 2 == 1:
        form.errors.view_count = "I am sorry but it's odd that you wrote %d" % form.vars.view_count



@auth.requires_signature()
@auth.requires_login()
def delete_product():
    product = db.product(request.args(0))
    # We must validate everything we receive.
    if product is None:
        logger.info("Invalid delete_product call")
        redirect(URL('default', 'listall'))
    # One can delete only one's own products.
    if product.prod_poster != auth.user.email:
        logger.info("Attempt to edit some one else's product by: %r" % auth.user.email)
        redirect(URL('default', 'listall'))
    db(db.product.id == product.id).delete()
    redirect(URL('default', 'listall'))

@auth.requires_signature()
@auth.requires_login()
def increment_stock():
    product = db.product(request.args(0))
    if product is None:
        redirect(URL('default', 'listall'))
    product.prod_in_stock = 1 if product.prod_in_stock is None else product.prod_in_stock + 1
    product.update_record()
    return redirect(URL('default', 'listall'))

@auth.requires_signature()
@auth.requires_login()
def increment_stock():
    product = db.product(request.args(0))
    if product is None:
        redirect(URL('default', 'listall'))
    product.prod_in_stock = 1 if product.prod_in_stock is None else product.prod_in_stock + 1
    product.update_record()
    return redirect(URL('default', 'listall'))

@auth.requires_signature()
@auth.requires_login()
def decrement_stock():
    product = db.product(request.args(0))
    if product is None:
        redirect(URL('default', 'listall'))
    if product.prod_in_stock > 0:
        product.prod_in_stock = product.prod_in_stock - 1
    product.prod_sold = 1 if product.prod_sold is None else product.prod_sold + 1
    product.update_record()
    return redirect(URL('default', 'listall'))


@auth.requires_signature()
@auth.requires_login()
def toggle_star():
    product = db.product(request.args(0))
    if product is None:
        redirect(URL('default', 'listall'))
    if product.prod_starred is None:
        product.prod_starred = True
    else:
        product.prod_starred = not product.prod_starred
    product.update_record()
    return redirect(URL('default', 'listall'))

# I made a wrapper to hide buttons when user is not logged in
def hide_if_no_user(func):
    def wrapper(*args, **kwargs):
        _btn = func(*args, **kwargs)
        if auth.user is not None:
            return _btn
        else:   
            return ""
    return wrapper

def produce_profit(row):
    # uses span helper to build span html elem with float of 
    #               quantity_sold * (sales_price - cost)
    # truncated to 2 decimal points
    return SPAN('${:20,.2f}'.format(row.prod_sold*(row.prod_price-row.prod_cost)),
                                 _class='green')

def produce_poster_btns(id):
    _btn = ""
    row = db.product(id)
    if auth.user is not None:
        if row.prod_poster == auth.user.email:
            _btn =  DIV(
                SPAN(A(I(_class='fa fa-pencil-square-o'), ' ','Edit', 
                        _href=URL('default', 'edit_product', args=[row.id], 
                                    user_signature=True),
                        _class='btn'),
                    _class="haha"),
             SPAN(A(I(_class='fa fa-trash'), ' ','delete', 
                        _href=URL('default', 'delete_product', args=[row.id], 
                                    user_signature=True),
                        _class='btn'),
                    _class="haha")
             )
    return _btn

@hide_if_no_user
def produce_pls_minus_btn(row):
    in_stock = row.prod_in_stock > 0
    _btns =  DIV(
             SPAN(A( I(_class='fa fa-plus'), 
                     _href=URL('default', 'increment_stock',
                                args=[row.id], user_signature=True),
                        _class='btn'),
                    _class="haha"),
             SPAN(A(  I(_class='fa fa-minus'), 
                     _href=URL('default', 'decrement_stock',
                                args=[row.id], user_signature=True)
                           if in_stock else URL('#'),
                     _class='btn'
                        if in_stock else 'btn grayed') ,
                  _class="haha")
             )
    return _btns

def produce_star_btn(id):
    row = db.product(id)
    if row.prod_starred == None:
        row.prod_starred = False
    _btn =  DIV(
        SPAN(A(I(_class='fa fa-star-o blkstr' if row.prod_starred == False
                 else 'fa fa-star goldstr'), 
             _href=URL('default', 'toggle_star', args=[row.id], 
                    user_signature=True)if auth.user is not None else URL('#'),
                    _class = "noeffect")
         )
        
        )
    return _btn



def listall():
    """This controller uses a grid to display all products."""
    # I like to define the query separately.
    query = db.product

    # List of additional links.
    links = []
    
    links.append(
        dict(header = "Profit",
            body = lambda row : produce_profit(row)
        )
    )
    links.append(
        dict(header = "",
            body = lambda row : produce_star_btn(row.id)
        )
    )
    links.append(
        dict(header = "",
            body = lambda row : produce_pls_minus_btn(row)
        )
    )
    links.append(
        dict(header='',
             body = lambda row : produce_poster_btns(row.id)
             
        )
    )
    
    # Let's get rid of some fields in the add form.
    if len(request.args) > 0 and request.args[0] == 'new':
        db.product.prod_poster.readable = False
        db.product.prod_post_time.writable = False
        db.product.prod_sold.writable = False
        db.product.prod_starred.readable, db.product.prod_starred.writable =False, False
    # Grid definition.
    grid = SQLFORM.grid(
        query, 
        field_id = db.product.id, # Useful, not mandatory.
        fields = [db.product.id, db.product.prod_name,
                    db.product.prod_in_stock, db.product.prod_sold,
                    db.product.prod_price, db.product.prod_cost], 
        headers = {'product.prod_name': 'Product Name',
                    'product.prod_in_stock':'In Stock',
                     'product.prod_sold':'Sold', 
                     'product.prod_price':'Price', 
                     'product.prod_cost':'Cost'},
        links = links,
        # And now some generic defaults.
        details=False,
        create=True, editable=False, deletable=False,
        csv=False, 
        user_signature=True, # We don't need it as one cannot take actions directly from the form.
    )
    return dict(grid=grid)

def urls():
    # request.args[1]
    # request.vars.person
    return dict()


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

