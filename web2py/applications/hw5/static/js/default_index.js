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
            // Vue.set(e, '_num_stars_display', e.rating); *** old stars code
            Vue.set(e, '_show_reviews', false);
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


    //Code for reviews
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
                $.web2py.enableElement($("#save_btn"));
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
            product_list: [],
            display_list: [],
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
            filter_prods: self.filter_prods
        }

    });

    // Gets the posts.
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
