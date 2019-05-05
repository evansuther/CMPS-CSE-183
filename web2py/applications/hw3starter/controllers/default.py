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
    grid = SQLFORM.grid(query)
    return dict(grid=grid)


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
                next=URL('default', 'create_order', args=[product]), 
                edit='y'
                )))
    form = SQLFORM(db.orders, labels = {'order_quantity': 'Quantity of %r' %product.prod_name})
    form.add_button('Back', URL('default', 'store'))
    if form.process().accepted:
        # And we load default/listall via redirect.

        # form.order_amt_paid = form.vars.order_quantity * product.prod_price
        # id = db.orders.insert(product_id =product,
        #                 order_quantity=form.vars.order_quantity,
        #                       order_amt_paid=amt_paid)
        logger.info("someone ordered %r " %form.vars.order_quantity)
        redirect(URL('default', 'store'))
    # form = FORM('%s Quantity' %product.prod_name,
    #           INPUT(_name='Quantity', requires=IS_NOT_EMPTY()),
    #           INPUT(_type='submit'))
    # We ask web2py to lay out the form for us.
    logger.info("Session: (%r) added a product" % session)
    return dict(form=form)


def profile():
    usr_profile = db(db.user_profile.usr_email == get_user_email()).select().first()
    if request.vars.edit == 'y' and usr_profile is not None:
        logger.info("first if in profile() for %r" %get_user_email())
        form = SQLFORM(db.user_profile, usr_profile)
    elif request.vars.edit == 'y':
        logger.info("elif in profile() for %r" %get_user_email())
        form = SQLFORM(db.user_profile)
    form.add_button('Back', URL('default', 'store'))
    if form.process().accepted:
        # The deed is done.
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


