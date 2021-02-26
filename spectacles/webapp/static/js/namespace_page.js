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

    var elementsDELNSArray = DOMRegex(/^del_ns_/);

    elementsDELNSArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteNamespace);
    });

    $("#namespace_form").submit(function(event) {
        /* stop form from submitting normally */
        event.preventDefault();

        var form_data = ($("#namespace_form").serializeArray().map(function(v){return [v.name, v.value];}))

        $.ajax({
            type: "POST",
            url: "/namespaces/add",
            data: JSON.stringify(form_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                //
            },
            error: function(xhr, ajaxOptions, thrownError) {
                //
            },
            complete: function(data) {
                if(data.responseJSON.hasOwnProperty('namespace_data')){
                    $("#namespace_data").html(data.responseJSON["namespace_data"]);
                }

                SetAllEventListeners()

                showMessage(data.responseJSON["status"], data.responseJSON["msg"])
            }
        });

    });

    var elementsASSIGNRIGHTSArray = DOMRegex(/^rw_/);

    elementsASSIGNRIGHTSArray.forEach(function(elem) {
        elem.addEventListener("click", SetNormalClaims);
    });
}

function DeleteNamespace(evt){

    var attrs = evt.target.attributes

    json = {}
    json["id"] = attrs["data-id"].nodeValue;

    $.ajax({
             type: "POST",
             url: "/namespaces/delete",
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
                   if(data.responseJSON.hasOwnProperty('namespace_data')){
                        $("#namespace_data").html(data.responseJSON["namespace_data"]);
                   }

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });

}

function SetNormalClaims(evt) {

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    var rights_dict = {
                    'FULL' : 'btn-outline-success',
                    'WRITE' : 'btn-outline-info',
                    'READ' : 'btn-outline-warning',
                    'NONE' : 'btn-outline-secondary',
               }

    function get_checkbox(name, claim, rs_data){

        if (rs_data.responseJSON[claim] == 'FULL'){
            return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '" checked>'
        } else if (rs_data.responseJSON[claim] == 'NONE') {
            return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '">'
        } else if (rs_data.responseJSON[claim] == 'READ') {
            if (name.endsWith('pull')) {
                return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '" checked>'
            } else {
                return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '">'
            }
        } else if (rs_data.responseJSON[claim] == 'WRITE') {
            if (name.endsWith('push')) {
                return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '" checked>'
            } else {
                return '<input type="checkbox" id="' + name + '" name="' + name + '" value="' + name + '">'
            }
        }
    }

    function checkboxChange(checkboxElem) {

       var target = checkboxElem.target

       var res = checkboxElem.target.id.charAt(0);
       var slice = checkboxElem.target.id.slice(2);

       if (slice == "pull") {
            if (target.checked){
                var current = "READ"
            } else {
                var current = "RNONE"
            }

            slice = "_push"
       } else {
            if (target.checked){
                var current = "WRITE"
            } else {
                var current = "WNONE"
            }
            slice = "_pull"
       }

       var other_cb = res + slice

       var other_checkbox = document.getElementById(other_cb)

       if (current == "READ") {
            if (other_checkbox.checked){
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-success btn-sm";
            } else {
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-warning btn-sm";
            }
       } else if (current == "RNONE") {
            if (other_checkbox.checked){
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-info btn-sm";
            } else {
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-secondary btn-sm";
            }
       } else if (current == "WNONE") {
            if (other_checkbox.checked){
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-warning btn-sm";
            } else {
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-secondary btn-sm";
            }
       } else if (current == "WRITE") {
            if (other_checkbox.checked){
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-success btn-sm";
            } else {
                var btn = document.getElementById(res + "_claim")
                btn.className = "btn btn-outline-info btn-sm";
            }
       }

    }

    $.ajax({
        type: "POST",
        url: "/namespaces/get_rights",
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

            var dialog = bootbox.dialog({
                title: 'Namespace rights:',
                message: `<form id="NS_rights" action="" method="post">
                            <table class="table table-striped">
                                <thead>
                                    <th></th>
                                    <th class="text-center">Pull (Read)</th>
                                    <th class="text-center">Push (Write)</th>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><a id="P_claim" class="btn ` + rights_dict[data.responseJSON['P_claim']] + ` btn-sm" title="Personal rights"><i class="fas fa-user"></i></a>  Owner</td>
                                        <td class="text-center">` + get_checkbox("P_pull", "P_claim", data) + `</td>
                                        <td class="text-center">` + get_checkbox("P_push", "P_claim", data) + `</td>
                                    </tr>
                                    <tr>
                                        <td><a id="G_claim" class="btn ` + rights_dict[data.responseJSON['G_claim']] + ` btn-sm" title="Group rights"><i class="fas fa-users"></i></a>  Group</td>
                                        <td class="text-center">` + get_checkbox("G_pull", "G_claim", data) + `</td>
                                        <td class="text-center">` + get_checkbox("G_push", "G_claim", data) + `</td>
                                    </tr>
                                    <tr>
                                        <td><a id="O_claim" class="btn ` + rights_dict[data.responseJSON['O_claim']] + ` btn-sm" title="Global rights"><i class="fas fa-globe-americas"></i></a>  Others</td>
                                        <td class="text-center">` + get_checkbox("O_pull", "O_claim", data) + `</td>
                                        <td class="text-center">` + get_checkbox("O_push", "O_claim", data) + `</td>
                                    </tr>
                                </tbody>
                            </table>
                          </form>`,
                size: 'normal',
                buttons: {
                    cancel: {
                        label: "Cancel",
                        className: 'btn-secondary btn-sm',
                    },
                    ok: {
                        label: "Save",
                        className: 'btn-success btn-sm',
                        callback: function(){

                            var form_data = ($("#NS_rights").serializeArray().map(function(v){return [v.name, v.value];}))

                            json["form_data"] = form_data

                            $.ajax({
                             type: "POST",
                             url: "/namespaces/set_rights",
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
                                    if(data.responseJSON.hasOwnProperty('namespace_data')){
                                        $("#namespace_data").html(data.responseJSON["namespace_data"]);
                                    }

                                    SetAllEventListeners()

                                    showMessage(data.responseJSON["status"], data.responseJSON["msg"])
                                }
                           });

                        }
                    }
                }
            });

            const checkboxes = document.querySelectorAll( '#NS_rights input[type=checkbox]' );

            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].addEventListener('change', checkboxChange, false);
            }
        }
    });



}