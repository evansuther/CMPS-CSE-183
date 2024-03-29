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
            update=get_current_time(),
            label='Posted'),

)
db.products.prod_post_time.readable = db.products.prod_post_time.writable = False
db.products.prod_poster.writable = False
db.products.id.readable = False


db.define_table('user_profile',
    Field('usr_email', update=get_user_email(), label='Email'), 
    Field('usr_name','string', label='Name'),
    Field('usr_street', 'string', label='Street Address'),
    Field('usr_city', 'string', label='City'),
    Field('usr_zip', 'integer', label='Zip')
)
db.user_profile.usr_email.writable=False

db.define_table('orders',
	Field('order_email', 'reference user_profile', ondelete='SET NULL'),
	Field('product_id', 'reference products', ondelete='SET NULL',
            label='Product Ordered'),
	Field('order_quantity', 'integer',
            requires=IS_INT_IN_RANGE(1, 1e100), default=1,
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
db.orders.id.readable = False
db.orders.product_id.writable = False
db.orders.order_date.writable = False
db.orders.order_amt_paid.writable  = False
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
