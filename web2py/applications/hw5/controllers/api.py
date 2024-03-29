# Here go your api methods.

def get_product_list():
    results = []
    rows = db(db.products).select(
        orderby=~db.products.prod_post_time)
    for row in rows:
        results.append(dict(
            id=row.id,
            prod_name=row.prod_name,
            prod_price=row.prod_price,
            display_price=represent_money(row.prod_price),
            prod_desc=row.prod_desc,
            rating = calc_avg_rating(row.id) #None if row.stars.id is None else row.stars.rating,
        ))
    return response.json(dict(product_list=results))


def get_review_list():
    results = []
    prod_id = int(request.vars.prod_id)
    # someone said on piazza they could grab all reviews with a simple
    # inner join query but I found the left joins necessary
    # to grab reviews without ratings and ratings without reviews 
    revs = db(db.reviews.prod_id == prod_id).select(db.reviews.ALL,  db.stars.ALL,
        left=[
            # this joins the ratings to the reviews if a rating exists
            db.stars.on( (db.stars.prod_id == prod_id) & (db.reviews.user_email == db.stars.user_email)),
            ],
        ) 
    logger.info("revs = %s"% revs)
    # got me the stars from haha 2 with no review
    rats = db(db.stars.prod_id == prod_id).select(db.reviews.ALL,  db.stars.ALL,
        left=[
            # this joins the reviews to the rating if a review exists
            db.reviews.on( (db.reviews.prod_id == prod_id) & (db.stars.user_email == db.reviews.user_email)),
            ],
        )
    logger.info("rats = %s"%rats)
    rows =  rats | revs # join via web2py rows OR operator

    for row in rows:
        # logger.info("row = %s"%row)
        # print "row.reviews.user_email is None = ", (row.reviews.user_email is None)
        # print "row.reviews.user_email = ", row.reviews.user_email
        # print "row.stars.user_email = ", row.stars.user_email
        # here i set the email and review content depending on what exists
        email = ""
        if row.reviews.user_email is None:
            email = row.stars.user_email
        else:
            email = row.reviews.user_email
        _rvw_cont = ""
        if row.reviews.review_content is not None:
            _rvw_cont = row.reviews.review_content 
        # build results as list of dictionaries
        results.append(dict(
            rating= 0 if row.stars.rating is None else row.stars.rating,
            review_content= _rvw_cont,
            reviewer=get_name_by_email(email),
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
    new_avg = calc_avg_rating(prod_id)
    return response.json(dict(new_avg=new_avg))


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


# Cart logic
@auth.requires_signature(hash_vars=False)
def add_prod_to_cart():
    """Sets the star rating of a post."""
    prod_id = int(request.vars.prod_id)
    logger.info("adding prod_id {%s} to cart" %prod_id)
    prod_quant = request.vars.prod_quant
    logger.info("quantity {%s}" %prod_quant)
    db.cart.update_or_insert(
        # try to find a record of the user/prod_id combo or insert
        (db.cart.user_email == auth.user.email) & (db.cart.prod_id == prod_id) ,
        prod_id = prod_id,
        user_email = auth.user.email,
        quantity = prod_quant
    )
    return "ok" # Might be useful in debugging.

@auth.requires_signature(hash_vars=False)
def get_cart():
    email = auth.user.email
    # try to find all products in the user's cart
    rows = db(db.cart.user_email == email).select()
    user_cart = []
    for row in rows:
        prod_row=db.products(row.prod_id)
        user_cart.append(dict(
            prod_id= row.prod_id,
            prod_name= prod_row.prod_name,
            prod_price= prod_row.prod_price,
            display_price= represent_money(prod_row.prod_price),
            cart_quantity= row.quantity,
            server_quantity= row.quantity,
        ))

    logger.info("cart = {%s}" %user_cart)
    return response.json(dict(cart=user_cart))

@auth.requires_signature(hash_vars=False)
def clear_cart():
    email = auth.user.email
    db(db.cart.user_email == email).delete()
    return "ok"
