function onlinetravel() {

    $.ajax({
        url : "/servicios/onlinetravel/",
        type : "GET",

        success : function(json) {
            if (json.url){
                // window.open(json.url, '_blank');
                window.location.replace(json.url);
            }
        }
    });
}

$(document).ready(onlinetravel);