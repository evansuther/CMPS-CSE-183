# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


# I made a wrapper to hide buttons when user is not logged in
def hide_if_no_user(func):
    def wrapper(*args, **kwargs):
        _btn = func(*args, **kwargs)
        if auth.user is not None:
            return _btn
        else:   
            return ""
    return wrapper


def get_product_name(p):
    return None if p is None else p.prod_name

def get_db_email(p):
    return None if p is None else db.user_profile(p).usr_email


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def order_list():
    query = db.orders
    db.orders.order_email.represent = lambda v, r : A(
        get_db_email(v), _href=URL('default', 'profile', vars=dict(email=get_db_email(v))))
    db.orders.product_id.represent = lambda v, r : A(
        get_product_name(db.products(v)), _href=URL('default', 'view_product', args=[v]))
    grid = SQLFORM.grid(query, 
        create=False,editable=False, deletable=False,
        csv=False, details=False)
    return dict(grid=grid)

def view_product():
    product = db.products(request.args(0))
    form = SQLFORM(db.products, product, readonly=T)
    return dict(form=form)

def store():
    # list of all products
    # button to buy, redir to create_order()
    query = db.products
    links = []
    links.append(
        dict(header = "Profit",
            body =  lambda row : produce_buy_btn(row))
    )
    # Let's get rid of some fields in the add form.
    if len(request.args) > 0 and request.args[0] == 'new':
        db.products.prod_poster.readable = False
        db.products.prod_post_time.writable = False
    # Grid definition.
    grid = SQLFORM.grid(
        query, 
        field_id = db.products.id, # Useful, not mandatory.
        fields = [db.products.id, 
                    db.products.prod_name,
                    db.products.prod_in_stock,
                    db.products.prod_price], 
        headers = {'products.prod_name': 'products Name',
                    'products.prod_in_stock':'In Stock',
                    'products.prod_price':'Price'},
        links = links,
        # And now some generic defaults.
        details=False,
        create=True, editable=False, deletable=False,
        csv=False, 
        user_signature=True, # We don't need it as one cannot take actions directly from the form.
    )
    return dict(grid=grid)


@auth.requires_login()
def create_order():
    # make sure user has a profile, diff from auth.login obj
    # if no profile, redir to profile page with :
    product = db.products(request.args(0))
    usr_profile = db(db.user_profile.usr_email == get_user_email()).select().first()
    if usr_profile is None:
        redirect(
            URL('default', 'profile', vars=dict(
                next=URL('default', 'create_order', args=[product.id], user_signature=True), 
                edit='y'
                )))
    db.orders.order_email.readable = db.orders.product_id.readable = False
    db.orders.order_date.readable = False
    # tie the order to the product
    db.orders.product_id.default = product.id
    db.orders.order_quantity.requires = IS_INT_IN_RANGE(1, product.prod_in_stock+1)
    form = SQLFORM(db.orders, labels = {'order_quantity': 'Quantity of %r' %product.prod_name})
    form.add_button('Back', URL('default', 'store'))
    logger.info("The product.id is %s" % product.id)
    if form.process().accepted:
        # this was another way of making sure price paid was set properly
        # form.vars.id contains id of newly inserted record
        new_order = db.orders(form.vars.id) 
        new_order.order_amt_paid = product.prod_price * form.vars.order_quantity
        new_order.update_record()
        # then update stock of product being ordered
        product.prod_in_stock = product.prod_in_stock - new_order.order_quantity
        product.update_record()
        logger.info("the new order is %s " % new_order)
        # And we load default/listall via redirect.
        logger.info("someone ordered %s " %form.vars.order_quantity)
        redirect(URL('default', 'store'))
    logger.info("Session: (%r) added an order" % session)
    return dict(form=form, prod_name=product.prod_name)


def profile():
    usr_profile = db(db.user_profile.usr_email == get_user_email()).select().first()
    email = request.vars.email or get_user_email()

    email_profile = db(db.user_profile.usr_email == email).select().first()
    logger.info("email_profile: %r" %email_profile)
    db.user_profile.id.readable = False
    if request.vars.edit == 'y' and email_profile is not None:
        logger.info("first if in profile() for %r" %email)
        form = SQLFORM(db.user_profile, email_profile)
    elif request.vars.edit == 'y':
        logger.info("elif in profile() for %r" %email)
        form = SQLFORM(db.user_profile)
    else:
        logger.info("else in profile() for %r, " %email)
        form = SQLFORM(db.user_profile, email_profile, readonly=True,)
    # form.add_button('Back', URL('default', 'store'))
    if form.process().accepted:
        # The deed is done.
        if request.vars.next is None:
            redirect(URL('default','store'))
        redirect(request.vars.next)
    return dict(form=form)


@hide_if_no_user
def produce_buy_btn(row):
    _btns =  SPAN(A( I(_class='fa fa-cart-plus'), 
                 _href=URL('default', 'create_order',
                            args=[row.id], user_signature=True),
                    _class='btn'),
                _class="haha")
    return _btns


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


