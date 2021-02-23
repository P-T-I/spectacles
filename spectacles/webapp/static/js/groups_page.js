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

    var elementsDELPLArray = DOMRegex(/^del_group_/);

    elementsDELPLArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteGroup);
    });

}

function DeleteGroup(evt){

    var attrs = evt.target.attributes

    json = {}
    json["id"] = attrs["data-id"].nodeValue;

    $.ajax({
             type: "POST",
             url: "/groups/delete",
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
                   $("#group_data").html(data.responseJSON["group_data"]);

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });
}