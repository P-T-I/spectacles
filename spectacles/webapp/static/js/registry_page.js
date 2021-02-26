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

    $("form").each(function ()
    {
        var that = $(this);

        $("input:submit", that).bind("click keypress", function ()
        {
            // store the id of the submit-input on it's enclosing form
            that.data("callerid", this.id);
        });
    });

    $("#registry_form").submit(function(event) {
            /* stop form from submitting normally */
            event.preventDefault();

            var callerId = $(this).data("callerid");

            var form_data = ($(this).serializeArray().map(function(v){return [v.name, v.value];}))

            // determine appropriate action(s)
            if (callerId == "test"){
                document.getElementById("registry_form").style.cursor = "wait";
                document.getElementById("test").style.cursor = "wait";
                $.ajax({
                        type: "POST",
                        url: "/registries/test_connection",
                        data: JSON.stringify(form_data),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function(data) {
                            showMessage("success", "Connection to registry succeeded!")

                            var service_name = document.getElementById('service_name')
                            service_name.value = data["service"]

                            var button = document.getElementById('save')
                            button.disabled = false
                            document.getElementById("registry_form").style.cursor = "auto";
                            document.getElementById("test").style.cursor = "auto";
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            if (xhr.status == 503) {
                                showMessage("error", "Connection to registry refused!")
                            } else {
                                showMessage("error", thrownError)
                            }
                            document.getElementById("registry_form").style.cursor = "auto";
                            document.getElementById("test").style.cursor = "auto";
                        },
                        complete: function(data) {
                            //
                        }
                });
            }

            if (callerId == "save"){
                //console.log($(this))
                $.ajax({
                        type: "POST",
                        url: "/registries/add",
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
                            if(data.responseJSON.hasOwnProperty('registry_data')){
                                $("#registry_data").html(data.responseJSON["registry_data"]);
                            }

                           SetAllEventListeners()

                           showMessage(data.responseJSON["status"], data.responseJSON["msg"])
                        }
                });
            }

        });

    var elementsDELREGArray = DOMRegex(/^del_reg_/);

    elementsDELREGArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteRegistry);
    });

}

function DeleteRegistry(evt){

    var attrs = evt.target.attributes

    json = {}
    json["id"] = attrs["data-id"].nodeValue;

    $.ajax({
             type: "POST",
             url: "/registries/delete",
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
                   if(data.responseJSON.hasOwnProperty('registry_data')){
                        $("#registry_data").html(data.responseJSON["registry_data"]);
                   }

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });

}
