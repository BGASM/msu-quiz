$(document).ready(function () {
    var form = document.getElementById("formData");
    console.log(form)

    form.onsubmit = function () {
        var formData = new FormData(form);
        console.log(formData)
        var data = JSON.stringify(Object.fromEntries(formData));
        var url = form.getAttribute('action');
        console.log(data)
        console.log(url)
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: window.location.replace('${response.data}'),
            contentType: 'application/json; charset=ytf-8'
        });
        return false;
    };
});