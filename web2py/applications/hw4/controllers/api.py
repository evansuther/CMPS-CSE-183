# Here go your api methods.

def get_product_list():
    results = []
    rows = db(db.products).select(
        orderby=~db.products.prod_post_time)
    for row in rows:
        results.append(dict(
            id=row.id,
            prod_name=row.prod_name,
            prod_price=represent_money(row.prod_price),
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
    rows =  rats | revs

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
    # return "ok" # Might be useful in debugging.


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
