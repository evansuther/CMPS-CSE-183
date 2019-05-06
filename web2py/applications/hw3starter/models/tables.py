# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime


def get_user_email():
    return None if auth.user is None else auth.user.email


def get_current_time():
    return datetime.datetime.utcnow()


def get_user_profile():
    try :
        return db(db.user_profile.usr_email == get_user_email()).select().first().id
    except: 
        return None


def represent_money(val):
    return None if val is None else '${:10,.2f}'.format(val)


db.define_table('products',
    Field('prod_name', label='Product Name'), # At most 512 characters
    Field('prod_in_stock', 'integer',
            requires=IS_INT_IN_RANGE(0, 1e100), default=0,
            label='Quantity in Stock'),
    Field('prod_price', 'double', 
            requires=IS_FLOAT_IN_RANGE(0, 1e100), default=0,
            represent =
                lambda val, row: '${:10,.2f}'.format(val),
            label='Price (to Customer)' ),
    Field('prod_poster', default=get_user_email()),
    Field('prod_post_time', 'datetime',
            update=get_current_time()),
)
db.products.prod_post_time.readable = db.products.prod_post_time.writable = False
db.products.prod_poster.writable = False
db.products.id.readable = False


db.define_table('user_profile',
    Field('usr_email', default=get_user_email()),
    Field('usr_name','string'),
    Field('usr_street', 'string'),
    Field('usr_city', 'string'),
    Field('usr_zip', 'integer')
)


db.define_table('orders',
	Field('order_email', 'reference user_profile', ondelete='SET NULL', default = get_user_profile()),
	Field('product_id', 'reference products', ondelete='SET NULL'),
	Field('order_quantity', 'integer',
            requires=IS_INT_IN_RANGE(0, 1e100), default=0,
            label='Order Quantity'),
	Field('order_date', 'datetime',
            update=get_current_time()),
	Field('order_amt_paid', 'double',
        requires=IS_FLOAT_IN_RANGE(0, 1e100), 
        default=0,
        represent = lambda val, row: represent_money(val),
        label='Amount Paid' )
)
db.orders.order_email.writable = False
db.orders.product_id.writable = False
db.orders.order_date.writable = False
db.orders.order_amt_paid.writable  = False
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
