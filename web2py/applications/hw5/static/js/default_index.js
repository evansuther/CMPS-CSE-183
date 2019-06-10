// This is the js for the default/index.html view.
var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};

    self.process_products = function() {
        // This function is used to post-process products, 
        // mostly to add attributes to products that Vue can track dynamically
        // We add the _idx attribute to the products with enumerate
        enumerate(self.vue.product_list);
        // when starting up, just having all products displayed is fine
        // display_list is changed by filter_prods(the search bar)
        self.vue.display_list = self.vue.product_list;
        self.vue.product_list.map(function (e) {
            // I need to use Vue.set here, because I am adding a new watched attribute
            // to an object.  See https://vuejs.org/v2/guide/list.html#Object-Change-Detection-Caveats
            // Number of stars to display, separate avg and user ratings
            Vue.set(e, '_avg_stars', e.rating);
            // user stars can be set by get_reviews
            Vue.set(e, '_user_stars', 0);
            Vue.set(e, '_show_reviews', false);
            Vue.set(e, '_show_check', false);
            // 3 different quantities to show/hide update btn in cart
            // and be able to display 0 for default buy quantity 
            // on each product
            Vue.set(e, 'desired_quantity', 0);
            Vue.set(e, 'cart_quantity', 0);
            Vue.set(e, 'server_quantity', 0)
            if (is_logged_in){
                // inserting a dummy fake review to be filled in by user
                // this attribute can also be replaced by the user's
                // review if one already exists
                Vue.set(e, "_user_review", 
                    {rating:0, review_content:"", reviewer:user_name}
                );
            }
            Vue.set(e, '_review_list', []);
        });
    };

    self.find_prod_idx_by_id = function(xid){
        for (i in self.vue.product_list){
            var prod = self.vue.product_list[i];
            console.log('prod = ', prod)
            if (prod.id === xid){
                return prod._idx;
            };
        };
        return -1;
    };

    // this function takes the search_term from the top search bar,
    // then filters the overall product list for names containing the 
    // term, modifying the displayed list
    self.filter_prods = function(){
        var results = [];
        // not sure if neccessary but for my sanity
        if (self.vue.search_term === ""){
            self.vue.display_list = self.vue.product_list;
            return;
        }
        for (i in self.vue.product_list){
            var prod = self.vue.product_list[i];
            var name = prod.prod_name.toLowerCase()
            if(name.includes(self.vue.search_term.toLowerCase())){
                results.push(prod);
            }
        }
        // change whats displayed in the browser
        self.vue.display_list = results;
    }

    // fills vue's product list, called when index is loading
    self.get_products = function() {
        // an AJAX call to app/api/get_product_list
        $.getJSON(get_product_list_url,
            function(data) {
                // I am assuming here that the server gives me a nice list
                // of products, all ready for display.
                self.vue.product_list = data.product_list;
                // add dynamic attributes and _idx to products
                self.process_products();
                // get_cart matches cart prods to the overall
                // product_list _idx so it has to wait for the list
                // and for the list to be processed
                if(is_logged_in){
                  self.get_cart();
                };
            }
        );
    }

    // Code for star ratings.
    // copied from vue-5-stars branch changed to _user_stars
    self.stars_out = function (prod_idx) {
        // Out of the star rating; set number of visible back to rating.
        var p = self.vue.product_list[prod_idx];
        p._user_stars = p._user_review.rating;
    };

    self.stars_over = function(prod_idx, star_idx) {
        // Hovering over a star; we show that as the number of active stars.
        var p = self.vue.product_list[prod_idx];
        p._user_stars = star_idx;
    };

    self.set_stars = function(prod_idx, star_idx) {
        if (is_logged_in){
        // The user has set this as the number of stars for the post.
            var p = self.vue.product_list[prod_idx];
            p._user_review.rating = star_idx;
            // Sends the rating to the server.
            $.web2py.disableElement($("#user_stars"));
            $.post(set_stars_url, {
                prod_id: p.id,
                rating: star_idx
                }, function(data){
                    $.web2py.enableElement($("#user_stars"));
                    p._avg_stars = data.new_avg
                }
            );
        };
    };

    // change the page between cart and products
    self.goto = function(page){
        self.vue.page=page;
    };

    // called when adding products to the cart from the products page
    // or when updating the cart quantity in the actual cart.
    // this changes the cart total, gives an idx to each product
    // according to the overall products list.
    self.update_cart_total = function(){
        var cart_sum = 0;
        for (i in self.vue.cart){
            var p = self.vue.cart[i];
            // p._changed = false; *** OLD
            console.log('var p = ', p);
            cart_sum = cart_sum + p.cart_quantity * p.prod_price.toFixed(2);
            // give products in the cart an _idx to be able to change the quantity in the future
            var p_idx = self.find_prod_idx_by_id(p.prod_id);
            p._idx = p_idx;
            console.log('p_idx = ', p_idx);
            var prod = self.vue.product_list[p_idx];
            // set cart quantity so that cart quantity can be properly incremented
            prod.cart_quantity=p.cart_quantity;
        };
        self.vue.cart_total = cart_sum.toFixed(2);
        return;
    };

    self.get_cart = function() {
        // an AJAX call to app/api/get_product_list
        $.getJSON(get_cart_url,
            function(data) {
                self.vue.cart = data.cart;
                // sum the total due and assign an _idx matching the
                // overall product list's _idx
                self.update_cart_total();
            }
        );
    };

    self.clear_cart = function(){
        // clear cart on server, wait for response, then clear local cart
        $.post(clear_cart_url, function(data){
            self.vue.cart = [];
            self.vue.cart_total = 0;
        });
        self.get_cart();
        self.process_products();
    };

    // called to update cart quantity server-side and keep
    // track of these changes browser-side
    self.buy_product = function(product_idx) {
        var p = self.vue.product_list[product_idx];
        // I need to put the product in the cart.
        // Check if it is already there.
        var already_present = false;
        var found_idx = 0;
        for (var i = 0; i < self.vue.cart.length; i++) {
            if (self.vue.cart[i].prod_id === p.id) {
                already_present = true;
                found_idx = i;
            }
        }
        // If it's there, just replace the quantity; otherwise, insert it.
        if (!already_present) {
            found_idx = self.vue.cart.length;
            self.vue.cart.push({
                prod_id: p.id,
                cart_quantity: p.cart_quantity, // will be 0 or the quant from the server
                server_quantity: p.server_quantity, // will be 0 or the quant from the server
                prod_name: p.prod_name,
                prod_price: p.prod_price,
                display_price: p.display_price,
            });
        };
        // update display quantities
        self.vue.cart[found_idx].cart_quantity += p.desired_quantity;
        p.cart_quantity += p.desired_quantity;
        // send changes to server
        $.post(add_prod_to_cart_url, {
            prod_id: p.id,
            prod_quant: p.cart_quantity
            }, function(data){
                p.desired_quantity = 0;
                // update server_quantity to reflect changes
                p.server_quantity = p.cart_quantity;
                self.vue.cart[found_idx].server_quantity = p.cart_quantity;
                // properly wait for server response to update total
                self.update_cart_total();
            }
        );
    };

    self.inc_desired_quantity = function(product_idx, qty) {
        // Inc and dec to desired quantity.
        var p = self.vue.product_list[product_idx];
        p.desired_quantity = Math.max(0, p.desired_quantity + qty);
    };

    self.inc_cart_quantity = function(product_idx, qty) {
        // Inc and dec to cart quantity.
        // updates pushed to server with buy_product()
        var p = self.vue.product_list[product_idx];
        var found_idx=self.vue.cart.length;
        for (i in self.vue.cart){
            if(self.vue.cart[i].prod_id === p.id){
                found_idx = i; 
            }
        };
        var cart_prod = self.vue.cart[found_idx];
        p.cart_quantity = Math.max(0, p.cart_quantity + qty);
        cart_prod.cart_quantity = Math.max(0, cart_prod.cart_quantity + qty);
        // p._changed = true; *****OLD
    };

    // Code for reviews
    self.get_reviews = function(prod_idx) {
        // hide all other reviews
        for (prod in self.vue.product_list){
            self.hide_reviews(prod);
        }
        var p = self.vue.product_list[prod_idx];
        console.log("user_name: " + user_name)
        $.getJSON(get_review_list_url, 
            {prod_id: p.id}, // args sent in the get request
            function (data) { // called when data sent back
                // instead of just taking the reviews I have to filter them
                // for the user review
                p._review_list = [];
                console.log(data.review_list);
                if (is_logged_in){
                    // inserting a dummy fake review to be filled in by user
                    // Vue.set(p, "_user_review", 
                    //     {rating:0, review_content:"", reviewer:user_name}
                    // );
                    // filtering the user's review
                    for (i in data.review_list){
                        var rev = data.review_list[i];
                        console.log(`rev.reviewer: ${rev.reviewer}`);
                        if (rev.reviewer !== user_name){
                            p._review_list.push(rev);
                        }
                        else{
                            // hopefully takes care of tracking the whole review object?
                            // Vue.set(p, "_user_review", rev); 
                            // Vue.set(p, "_user_stars", rev.rating);
                            p._user_review = rev;
                            p._user_stars = rev.rating;
                        };
                    };
                }
                else{
                    // not logged in, just fill reviews
                    p._review_list = data.review_list;
                };
                p._show_reviews = true;
            }
        );
    };

    self.hide_reviews = function(prod_idx){
        var p = self.vue.product_list[prod_idx];
        p._show_reviews = false;
    };

    self.save_review = function(prod_idx){
        $.web2py.disableElement($("#save_btn"));
        var p = self.vue.product_list[prod_idx];
        $.post(save_review_url, {
                prod_id: p.id,
                content: p._user_review.review_content
            }, function(data){
                p._show_check = true;
                setTimeout(function(){ 
                    $.web2py.enableElement($("#save_btn"));
                    p._show_check = false;
                 },
                 500);
                // $.web2py.enableElement($("#save_btn"));
            });
    };

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        // data to be kept in sync with the browser view
        data: {
            form_title: "",
            form_content: "",
            search_term: "",
            page:'prods',
            product_list: [],
            display_list: [],
            cart: [],
            cart_total:0,
            star_indices: [1, 2, 3, 4, 5]
        },
        // these methods are viewable to the browser js
        methods: {
             // Star ratings.
            stars_out: self.stars_out,
            stars_over: self.stars_over,
            set_stars: self.set_stars,
            // review methods
            get_reviews: self.get_reviews,
            hide_reviews: self.hide_reviews,
            save_review: self.save_review,
            // search bar
            filter_prods: self.filter_prods,
            // cart
            goto: self.goto,
            get_cart: self.get_cart,
            inc_desired_quantity: self.inc_desired_quantity,
            inc_cart_quantity: self.inc_cart_quantity,
            buy_product: self.buy_product,
            clear_cart: self.clear_cart,
        }

    });

    // Gets the products and cart.
    self.get_products();
    
    
    $("#vue-div").show()
    return self;
};

var APP = null;

// No, this would evaluate it too soon.
// var APP = app();

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
