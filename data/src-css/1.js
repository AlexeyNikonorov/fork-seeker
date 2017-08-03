$(document).ready(function(){
    $("td").click(function(){
        var s = $(this).text();
        var c = $(this).attr("class");
        var e = document.querySelectorAll("td");
        $("td.blue").removeClass("blue");
        if (c.search("blue") == -1) {
            for (i=0; i<e.length; i++) {
                if (e[i].innerHTML == s) {
                    $(e[i]).toggleClass("blue");
                }
            }
        }
    });
});
