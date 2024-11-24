$(function() {
    $(".tree-menu a").each(function() {
        if ($(this).parent("li").children("ul").size()) {
            $(this).addClass("folder-close");
        } else {
            $(this).addClass("file");
        }
    });
    $(".tree-menu a").click(function() {
        $(".tree-menu a").removeClass("current");
        $(this).addClass("current");
        $(this).parent("li").children("ul").toggle(100, function() {
            if ($(this).parent("li").children("ul").css("display") == "block") {
                $(this).parent("li").children("a").removeClass("folder-close");
                $(this).parent("li").children("a").addClass("folder-open");
            } else {
                $(this).parent("li").children("a").removeClass("folder-open");
                $(this).parent("li").children("a").addClass("folder-close");
            }
        });
        if ($(this).attr("href") != "#") {
            return true;
        } else {
            return false;
        }
    });
});
