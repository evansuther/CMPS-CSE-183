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

    // self.add = function () {
    //     // We disable the button, to prevent double submission.
    //     $.web2py.disableElement($("#add-post"));
    //     var sent_title = self.vue.form_title; // Makes a copy 
    //     var sent_content = self.vue.form_content; // 
    //     $.post(add_post_url,
    //         // Data we are sending.
    //         {
    //             post_title: self.vue.form_title,
    //             post_content: self.vue.form_content
    //         },
    //         // What do we do when the post succeeds?
    //         function (data) {
    //             // Re-enable the button.
    //             $.web2py.enableElement($("#add-post"));
    //             // Clears the form.
    //             self.vue.form_title = "";
    //             self.vue.form_content = "";
    //             // Adds the post to the list of posts. 
    //             var new_post = {
    //                 id: data.post_id,
    //                 post_title: sent_title,
    //                 post_content: sent_content
    //             };
    //             self.vue.post_list.unshift(new_post);
    //             // We re-enumerate the array.
    //             enumerate(self.vue.post_list);
    //         });
    //     // If you put code here, it is run BEFORE the call comes back.
    // };


    // Code for star ratings.
    // self.stars_out = function (post_idx) {
    //     // Out of the star rating; set number of visible back to rating.
    //     var p = self.vue.post_list[post_idx];
    //     p._num_stars_display = p.rating;
    // };

    // self.stars_over = function(post_idx, star_idx) {
    //     // Hovering over a star; we show that as the number of active stars.
    //     var p = self.vue.post_list[post_idx];
    //     p._num_stars_display = star_idx;
    // };

    // self.set_stars = function(post_idx, star_idx) {
    //     // The user has set this as the number of stars for the post.
    //     var p = self.vue.post_list[post_idx];
    //     p.rating = star_idx;
    //     // Sends the rating to the server.
    //     $.post(set_stars_url, {
    //         post_id: p.id,
    //         rating: star_idx
    //     });
    // };

    self.process_products = function() {
        // This function is used to post-process posts, after the list has been modified
        // or after we have gotten new posts. 
        // We add the _idx attribute to the posts. 
        enumerate(self.vue.product_list);
        // We initialize the smile status to match the like. 
        self.vue.product_list.map(function (e) {
            // I need to use Vue.set here, because I am adding a new watched attribute
            // to an object.  See https://vuejs.org/v2/guide/list.html#Object-Change-Detection-Caveats
            // Did I like it? 
            // Vue.set(e, '_smile', e.like);
            // Who liked it?
            // Vue.set(e, '_likers', []);
            // Do I know who liked it? (This could also be a timestamp to limit refresh)
            // Vue.set(e, '_likers_known', false);
            // Do I show who liked? 
            // Vue.set(e, '_show_likers', false);
            // Number of stars to display.
            Vue.set(e, '_num_stars_display', e.rating);
        });
    };

    self.get_products = function() {
        $.getJSON(get_product_list_url,
            function(data) {
                // I am assuming here that the server gives me a nice list
                // of products, all ready for display.
                self.vue.product_list = data.product_list;
                // We enumerate the products, adding an _idx to each of them.
                self.process_products();
            }
        );
    }

    // Code for star ratings.
    self.stars_out = function (prod_idx) {
        // Out of the star rating; set number of visible back to rating.
        var p = self.vue.product_list[prod_idx];
        p._num_stars_display = p.rating;
    };

    self.stars_over = function(prod_idx, star_idx) {
        // Hovering over a star; we show that as the number of active stars.
        var p = self.vue.product_list[prod_idx];
        p._num_stars_display = star_idx;
    };

    self.set_stars = function(prod_idx, star_idx) {
        // The user has set this as the number of stars for the post.
        var p = self.vue.product_list[prod_idx];
        p.rating = star_idx;
        // Sends the rating to the server.
        $.post(set_stars_url, {
            prod_id: p.id,
            rating: star_idx
        });
    };

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        // data to be kept in sync with the view
        data: {
            form_title: "",
            form_content: "",
            product_list: [],
            star_indices: [1, 2, 3, 4, 5]
        },
        // these methods are viewable to the browser js
        methods: {
            // add_post: self.add_post
             // Star ratings.
            stars_out: self.stars_out,
            stars_over: self.stars_over,
            set_stars: self.set_stars
        }

    });

    // If we are logged in, shows the form to add posts.
    if (is_logged_in) {
        // $("#add_post").show();
    }

    // Gets the posts.
    self.get_products();
    // $("#vue-div").show()
    return self;
};

var APP = null;

// No, this would evaluate it too soon.
// var APP = app();

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
