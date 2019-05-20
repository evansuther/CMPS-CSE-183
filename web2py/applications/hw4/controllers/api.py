# Here go your api methods.

def get_product_list():
    product_list = db(db.products).select(db.products.id, 
        db.products.prod_name, db.products.prod_desc,
        db.products.prod_price,
         orderby=~db.products.prod_post_time).as_list()
    # format the price, stored internally as float
    for prod in product_list:
        prod['prod_price'] = represent_money(prod['prod_price'])
    logger.info("product_list= %s" %product_list)
    # I like to always return a dictionary.
    return response.json(dict(product_list=product_list))
