# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

# logger.info("The user record is: %r" % auth.user)

import datetime

def get_user_email():
    return None if auth.user is None else auth.user.email

def get_current_time():
    return datetime.datetime.utcnow()

# db.define_table('post',
#                 Field('post_author', default=get_user_email()),
#                 Field('post_title'), # At most 512 characters
#                 Field('post_content', 'text'), # "unlimited"
#                 Field('post_time', 'datetime', update=get_current_time()),
#                 Field('view_count', 'integer', default=0),
#                 )

# db.post.post_time.readable = db.post.post_time.writable = False
# db.post.post_author.writable = False
# db.post.id.readable = False


db.define_table('product',
                Field('prod_name', label='Product Name'), # At most 512 characters
                Field('prod_desc', 'text', label= 'Description'), # "unlimited"
                Field('prod_starred', 'boolean', label= 'Starred', default = False), 
                Field('prod_in_stock', 'integer',
                        requires=IS_INT_IN_RANGE(0, 1e100), default=0,
                        label='Quantity in Stock'), 
                Field('prod_sold', 'integer', 
                        requires=IS_INT_IN_RANGE(0, 1e100), default=0, 
                        label='Quantity Sold'), 
                Field('prod_price', 'double', 
                        requires=IS_FLOAT_IN_RANGE(0, 1e100), default=0,
                        represent =
                         lambda val, row: '${:10,.2f}'.format(val),
                        label='Price (to Customer)' ), 
                Field('prod_cost', 'double', 
                        requires=IS_FLOAT_IN_RANGE(0, 1e100), default=0,
                        represent = 
                          lambda val, row: '${:10,.2f}'.format(val),
                        label='Cost (to bring to Market)'), 
                Field('prod_poster', default=get_user_email()),
                Field('prod_post_time', 'datetime',
                         update=get_current_time()),
                
                )

db.product.prod_post_time.readable = db.product.prod_post_time.writable = False
db.product.prod_sold.writable  =False
db.product.prod_poster.writable = False
db.product.id.readable = False

# Stars

# db.define_table('star',
#                 Field('user_id', 'reference auth_user'), # The user who starred
#                 Field('post_id', 'reference post'), # The starred post
#                 Field('product_id', 'reference product'), # The starred post
#                 )
# after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
