# Here go your api methods.

def get_product_list():
    results = []
    rows = db().select(db.products.ALL,  db.stars.ALL,
                            left=[
                                db.stars.on((db.stars.prod_id == db.products.id) & (db.stars.user_email == auth.user.email)),
                            ],
                            orderby=~db.products.prod_post_time)
    for row in rows:
        results.append(dict(
            id=row.products.id,
            prod_name=row.products.prod_name,
            prod_price=row.products.prod_price,
            prod_desc=row.products.prod_desc,
            rating = None if row.stars.id is None else row.stars.rating,
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


# copied from vue-5-stars
@auth.requires_signature(hash_vars=False)
def set_stars():
    """Sets the star rating of a post."""
    prod_id = int(request.vars.prod_id)
    rating = int(request.vars.rating)
    db.stars.update_or_insert(
        (db.stars.prod_id == prod_id) & (db.stars.user_email == auth.user.email),
        prod_id = prod_id,
        user_email = auth.user.email,
        rating = rating
    )
    return "ok" # Might be useful in debugging.
