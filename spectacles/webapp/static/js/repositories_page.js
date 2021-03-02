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

    var elementsPLArray = DOMRegex(/^path_link_/);

    elementsPLArray.forEach(function(elem) {
        elem.addEventListener("click", GetRepoDetails);
    });

    var elementsDELREPOArray = DOMRegex(/^del_repo_/);

    elementsDELREPOArray.forEach(function(elem) {
        elem.addEventListener("click", DelRepo);
    });

}

function GetRepoDetails(evt){

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
        url: "/repositories/get_repodetails",
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
            $("#repo_details").html(data.responseText);
            SetAllEventListeners()
        }
    });
}

function DelRepo(evt){

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    json["digest"] = attrs["data-digest"].nodeValue;
    json["name"] = attrs["data-name"].nodeValue;

    $.ajax({
        type: "POST",
        url: "/repositories/del_repo",
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
            if(data.responseJSON.hasOwnProperty('repo_details')){
                $("#repo_details").html(data.responseJSON["repo_details"]);
            }
            SetAllEventListeners()
            showMessage(data.responseJSON["status"], data.responseJSON["msg"])
        }
    });
}