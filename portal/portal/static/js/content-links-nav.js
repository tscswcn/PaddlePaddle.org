
var ContentLinksNav = {
    navContainer: null,

    init: function(navContainerSelector) {
        self = this
        self.navContainer = $(navContainerSelector);

        if (self.navContainer.length) {
            self.navContainer.find("a").click(function(e) {
                jqLink = $(this);
                url = jqLink.attr('href');

                if (!url.startsWith('#')) {
                    if (url != document.location.href) {
                        if (history.pushState) {
                            window.history.pushState(url, document.title, url);
                        } else {
                            document.location.href = url;
                        }
                        self.updatePage(url, function() {});
                    }
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
        }
    },

    updatePage: function(url, callback) {
        self = this;
        staticOnlyUrl = url + "?raw=1";
        $.get(staticOnlyUrl, function(staticData) {
            $('#doc-content').html(staticData);
            $('html').scrollTop(0);

            if (callback) {
                callback();
            }

            self.updateActiveLinks();
            $( document ).trigger( "content-updated" );
        });
    },

    updateActiveLinks: function() {
        if (this.navContainer.length) {
            this.navContainer.find("a").each(function(index, anchor) {
                jqAnchor = $(anchor);
                jqAnchorLink = jqAnchor.attr('href');

                if (jqAnchorLink == document.location.pathname) {
                    jqAnchor.addClass('active');

                    var parent = jqAnchor.closest('.chapter');
                    if (parent) {
                        var parentLink = parent.find('h3>a');
                        if (parentLink) {
                            parentLink.addClass('active');
                        }
                    }
                } else {
                    jqAnchor.removeClass('active');
                }
            });

        }
    }
}

$(function(){
    ContentLinksNav.init(".content-links");

    window.onpopstate = function(e){
        if(e.state){
            ContentLinksNav.updatePage(e.state);
        }
    };

    $( document ).on( "content-updated", function( event ) {
        $('#sidebar-nav').removeClass('show');
    });
})