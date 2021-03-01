function DOMRegex(regex) {
        let output = [];
        for (let i of document.querySelectorAll('*')) {
            if (regex.test(i.id)) { // or whatever attribute you want to search
                output.push(i);
            }
        }
        return output;
    }

function SetAllEventListeners(){

    var elementsDELPLArray = DOMRegex(/^del_user_/);

    elementsDELPLArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteUser);
    });

    var elementsISADMINArray = DOMRegex(/^is_admin_/);

    elementsISADMINArray.forEach(function(elem) {
        elem.addEventListener("change", SetAdmin);
    });

    var elementsDELGROUPArray = DOMRegex(/^groupbtn_/);

    elementsDELGROUPArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteFromGroup);
    });

}

function SetAdmin(evt) {

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    json["is_admin"] = evt.target.checked;

    $.ajax({
             type: "POST",
             url: "/users/set_admin",
             data: JSON.stringify(json),
             contentType: "application/json; charset=utf-8",
             dataType: "json",
             success: function(data) {
                 //
             },
             error: function(xhr, ajaxOptions, thrownError) {
                 //
             },
             complete: function(data) {
                   $("#user_data").html(data.responseJSON["user_data"]);

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });


}

function DeleteUser(evt){

    json = {}
    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    $.ajax({
             type: "POST",
             url: "/users/delete",
             data: JSON.stringify(json),
             contentType: "application/json; charset=utf-8",
             dataType: "json",
             success: function(data) {
                 //
             },
             error: function(xhr, ajaxOptions, thrownError) {
                 //
             },
             complete: function(data) {
                   $("#user_data").html(data.responseJSON["user_data"]);

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });
}

function DeleteFromGroup(evt){

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["groupmemberid"] = attrs["data-groupmemberid"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["groupmemberid"] = attrs["data-groupmemberid"].nodeValue;
    }

    $.ajax({
             type: "POST",
             url: "/users/del_group",
             data: JSON.stringify(json),
             contentType: "application/json; charset=utf-8",
             dataType: "json",
             success: function(data) {
                 //
             },
             error: function(xhr, ajaxOptions, thrownError) {
                 //
             },
             complete: function(data) {
                   if(data.responseJSON.hasOwnProperty('user_data')){
                        $("#user_data").html(data.responseJSON["user_data"]);
                   }

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });

}