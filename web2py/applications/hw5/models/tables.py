# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime

# HELPER FUNCTIONS
def get_user_email():
    return None if auth.user is None else auth.user.email


def get_name_by_email(_email):
    if _email is None:
        return "None"
    row = db(db.auth_user.email == _email).select().first()
    name = "" + row.first_name + " " + row.last_name
    return name


def get_current_time():
    return datetime.datetime.utcnow()


def represent_money(val):
    return None if val is None else '${:,.2f}'.format(val)


def calc_avg_rating(_id):
    rows = db(db.stars.prod_id == _id).select()
    total = 0
    count = 0
    for row in rows:
        if row.id is not None:
            logger.info("calc_avg_rating: row = %s" %row)
            total = total + row.rating
            count = count + 1
    logger.info("total, count = %s"%[total, count])
    return total//count if count != 0 else 0


# TABLES
db.define_table('products',
    Field('prod_name', label='Product Name'), # At most 512 characters
    Field('prod_desc', 'text', label= 'Description'), # "unlimited"
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


# Stars ratings
db.define_table('stars',
    Field('user_email'), # The user who starred
    Field('prod_id', 'reference products'), # The starred prod
    Field('rating', 'integer', default=None) # The star rating.
    )


# text reviews
db.define_table('reviews',
    Field('user_email'), # The user who reviewed
    Field('prod_id', 'reference products'), # The reviewd prod
    Field('review_content', 'text', label= 'Review Content') # The text content.
    )
# I set less defaults and writable/readables becuase the stars and 
# reviews data is only accessed through api or admin

db.define_table('cart',
    Field('user_email'), # The user who starred
    Field('prod_id', 'reference products'),
    Field('amount', 'integer'),
    )
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
