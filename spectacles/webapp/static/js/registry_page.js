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

            json = {}

            // determine appropriate action(s)
            if (callerId == "test"){
                $.ajax({
                        type: "POST",
                        url: "/registries/test_connection",
                        data: JSON.stringify(json),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function(data) {
                            //
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            if (xhr.status == 503) {
                                showMessage("error", "Connection to registry refused!")
                            } else {
                                showMessage("error", thrownError)
                            }
                        },
                        complete: function(data) {
                            //
                        }
                });
            }

            if (callerId == "save"){
                //console.log($(this))
            }

        });

}