# Here go your api methods.

def get_product_list():
    results = []
    rows = db().select(db.products.ALL,  db.stars.ALL,
        left=[
            db.stars.on((db.stars.prod_id == db.products.id) ),#& (db.stars.user_email == auth.user.email)
        ],
        orderby=~db.products.prod_post_time)
    for row in rows:
        results.append(dict(
            id=row.products.id,
            prod_name=row.products.prod_name,
            prod_price=represent_money(row.products.prod_price),
            prod_desc=row.products.prod_desc,
            rating = calc_avg_rating(row.products.id) #None if row.stars.id is None else row.stars.rating,
        ))
    # product_list = db(db.products).select(db.products.id, 
    #     db.products.prod_name, db.products.prod_desc,
    #     db.products.prod_price,
    #      orderby=~db.products.prod_post_time).as_list()
    # # format the price, stored internally as float
    # for prod in product_list:
    #     prod['prod_price'] = represent_money(prod['prod_price'])
    # logger.info("product_list= %s" %product_list)
    # I like to always return a dictionary.
    # return response.json(dict(product_list=product_list))
    return response.json(dict(product_list=results))


def get_review_list():
    results = []
    prod_id = int(request.vars.prod_id)
    rows = db(db.reviews.prod_id == prod_id).select(db.reviews.ALL,  db.stars.ALL,
        left=[
            db.stars.on((db.stars.prod_id == prod_id)  & (db.reviews.user_email == db.stars.user_email)),#& & (db.reviews.prod_id == prod_id)
        ],
        )
    for row in rows:
        _email = row.stars.user_email if row.reviews.user_email is None else row.reviews.user_email
        _rvw_cont = row.reviews.review_content if row.reviews.review_content is not None else ""
        results.append(dict(
            rating=row.stars.rating,
            review_content= _rvw_cont,
            reviewer=get_name_by_email(_email),
        ))
    return response.json(dict(review_list=results))


# copied from vue-5-stars
@auth.requires_signature(hash_vars=False)
def set_stars():
    """Sets the star rating of a post."""
    prod_id = int(request.vars.prod_id)
    logger.info("changing stars on prod_id {%s}" %prod_id)
    rating = int(request.vars.rating)
    logger.info("auth.user from api: %s"%auth.user.email )
    db.stars.update_or_insert(
        (db.stars.prod_id == prod_id) & (db.stars.user_email == auth.user.email),
        prod_id = prod_id,
        user_email = auth.user.email,
        rating = rating
    )
    return "ok" # Might be useful in debugging.


# copied from vue-5-stars
@auth.requires_signature(hash_vars=False)
def save_review():
    """Sets the star rating of a post."""
    prod_id = int(request.vars.prod_id)
    logger.info("saving review on prod_id {%s}" %prod_id)
    content = request.vars.content
    db.reviews.update_or_insert(
        (db.reviews.prod_id == prod_id) & (db.reviews.user_email == auth.user.email),
        prod_id = prod_id,
        user_email = auth.user.email,
        review_content = content
    )
    return "ok" # Might be useful in debugging.
