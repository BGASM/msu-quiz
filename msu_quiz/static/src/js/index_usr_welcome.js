$(window).on('load', function() {
    var usr = "{{ user }}";
    if(usr != ''){document.getElementById("if-user").hidden = false;}
});