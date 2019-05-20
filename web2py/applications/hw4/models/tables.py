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

def represent_money(val):
    return None if val is None else '${:,.2f}'.format(val)

db.define_table('products',
    Field('prod_name', label='Product Name'), # At most 512 characters
    Field('prod_desc', 'text', label= 'Description'), # "unlimited"
    # Field('prod_in_stock', 'integer',
    #         requires=IS_INT_IN_RANGE(0, 1e100), default=0,
    #         label='Quantity in Stock'),
    Field('prod_price', 'double', 
            requires=IS_FLOAT_IN_RANGE(0, 1e100), default=0,
            represent =
                lambda val, row: represent_money(val),
            label='Price (to Customer)' ),
    Field('prod_poster', default=get_user_email()),
    Field('prod_post_time', 'datetime',
            update=get_current_time(),
            label='Posted'),

)
db.products.prod_post_time.readable = db.products.prod_post_time.writable = False
db.products.prod_poster.writable = False
db.products.id.readable = False


# db.define_table('stars',
#     Field('prod')    
# )
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
