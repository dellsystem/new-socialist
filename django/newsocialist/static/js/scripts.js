function toggleHamburger() {
    $('#header .right.menu').toggleClass('visible');
    return false;
};

$('.ui.dropdown').dropdown();
$('.footnote-backref,.footnote-ref').click(function(e) {
    e.preventDefault();
    // There is a colon in the ID so can't just put into $() directly
    var dest = document.getElementById($(this).attr('href').substring(1));

    // Only add the "highlighted" class for the actual footnote text.
    if (dest.tagName == 'LI') {
        $(dest).addClass('highlighted');
        setTimeout(function () {
            $(dest).removeClass('highlighted');
        }, 3000)
    }

    var parentOffset = $('#article-top').offset().top;
    var offset = $(dest).offset().top;
    $('#scroll').animate({ scrollTop: offset-parentOffset }, 'slow');
});
