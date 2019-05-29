# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    return dict()


def products():
    # list of all products
    # button to buy, redir to create_order()
    query = db.products
    links = []
    # if auth.user is not None:
        # links.append(
        #     dict(header = "Purchase",
        #         body =  lambda row : produce_buy_btn(row))
        # )
    # Let's get rid of some fields in the add form.
    if len(request.args) > 0 and request.args[0] == 'new':
        db.products.prod_poster.readable = False
        db.products.prod_post_time.writable = False

    db.products.prod_name.represent = lambda v, r : A(
        v, _href=URL('default', 'view_product', args=[r.id]))
    # Grid definition.
    grid = SQLFORM.grid(
        query, 
        field_id = db.products.id, # Useful, not mandatory.
        fields = [db.products.id, 
                    db.products.prod_name,
                    # db.products.prod_in_stock,
                    db.products.prod_price], 
        headers = {'products.prod_name': 'products Name',
                    'products.prod_in_stock':'In Stock',
                    'products.prod_price':'Price'},
        links = links,
        # And now some generic defaults.
        details=True,
        # create=True, editable=lambda r: decide_if_poster(r.id), 
        create=True, editable=True, 
        # deletable=lambda r: decide_if_poster(r.id),
        deletable=True,
        csv=False, 
        user_signature=True, # We don't need it as one cannot take actions directly from the form.
    )
    return dict(grid=grid)


def view_product():
    product = db.products(request.args(0))
    form = SQLFORM(db.products, product, readonly=T)
    # btns = []
    return dict(form=form, prod_name=product.prod_name,  )

def decide_if_poster(row):
    prod=db.products(row)
    # logger.info("row is %s"%row)
    # logger.info("prod is %s"%prod)
    res = False
    if auth.user is not None:
        if prod.prod_poster == auth.user.email:
            res = True
    return res


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


