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

    var elementsASSIGNPERSGROUPSArray = DOMRegex(/^assign_usr_group_/);

    elementsASSIGNPERSGROUPSArray.forEach(function(elem) {
        elem.addEventListener("click", SetUserGroupRights);
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

function tagTemplate(tagData){
    return `
        <tag title="${(tagData.title || tagData.email)}"
                contenteditable='false'
                spellcheck='false'
                tabIndex="-1"
                class="${this.settings.classNames.tag} ${tagData.class ? tagData.class : ""}"
                ${this.getAttributes(tagData)}>
            <x title='' class='tagify__tag__removeBtn' role='button' aria-label='remove tag'></x>
            <div>
                <div class='tagify__tag__avatar-wrap'>
                    <img onerror="this.style.visibility='hidden'" src="${tagData.avatar}">
                </div>
                <span class='tagify__tag-text'>${tagData.name}</span>
            </div>
        </tag>
    `
}

function suggestionItemTemplate(tagData){
    return `
        <div ${this.getAttributes(tagData)}
            class='tagify__dropdown__item ${tagData.class ? tagData.class : ""}'
            tabindex="0"
            role="option">
            ${ tagData.avatar ? `
            <div class='tagify__dropdown__item__avatar-wrap'>
                <img onerror="this.style.visibility='hidden'" src="${tagData.avatar}">
            </div>` : ''
            }
            <strong>${tagData.name}</strong>
            <span>${tagData.email}</span>
        </div>
    `
}

function suggestionGroupTemplate(tagData){
    return `
        <div ${this.getAttributes(tagData)}
            class='tagify__dropdown__item ${tagData.class ? tagData.class : ""}'
            tabindex="0"
            role="option">
            ${ tagData.avatar ? `
            <div class='tagify__dropdown__item__avatar-wrap'>
                <img onerror="this.style.visibility='hidden'" src="${tagData.avatar}">
            </div>` : ''
            }
            <strong>${tagData.name}</strong>
        </div>
    `
}

var tagify = null

function SetUserGroupRights(evt){

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    function getUserDiv(username, userid){

        return '<a id="user_btn_' + username + '" data-namespaceid="' + json["id"] + '" data-userid="' + userid + '" class="btn btn-info btn-sm margin_right"><i class="far fa-times-circle pointer margin_right"></i>' + username + '</a>'

    }

    function getGroupDiv(name, groupid){

        return '<a id="group_btn_' + name + '" data-namespaceid="' + json["id"] + '" data-groupid="' + groupid + '" class="btn btn-info btn-sm margin_right"><i class="far fa-times-circle pointer margin_right"></i>' + name + '</a>'

    }

    $.ajax({
        type: "POST",
        url: "/namespaces/get_assigned_users_groups",
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

              var user_div = '<div class="margin_bottom">'

              for (i=0; i < data.responseJSON["users"].length; i++) {
                       user_div = user_div + getUserDiv(data.responseJSON["users"][i]['username'].toUpperCase(), data.responseJSON["users"][i]['id'])
                  }

              user_div = user_div + '</div>'

              var group_div = '<div class="margin_bottom">'



              group_div = group_div + '</div>'

              var dialog = bootbox.dialog({
                    title: 'Namespace rights:',
                    message: `<div class="card">
                            <div class="card-header p-2">
                                <ul class="nav nav-pills">
                                    <li class="nav-item"><a class="nav-link active" href="#users_tab" data-toggle="tab">Users</a></li>
                                    <li class="nav-item"><a class="nav-link" href="#groups_tab" data-toggle="tab">Groups</a></li>
                                </ul>
                            </div>
                            <div class="card-body">
                                <div class="tab-content">
                                    <div class="active tab-pane" id="users_tab">
                                        <label>Assigned users: </label>
                                        ` + user_div + `
                                        <label>Select users: </label>
                                        <input name='users' value='' placeholder='write usernames or select below'>
                                    </div>
                                    <div class="tab-pane" id="groups_tab">
                                    <label>Assigned groups: </label>
                                    ` + group_div + `
                                    <label>Select users: </label>
                                    <input name='groups' value='' placeholder='write group names or select below'>
                                </div>
                                </div>
                            </div>
                        </div>`,
                    size: 'large',
                    buttons: {
                        cancel: {
                            label: "Cancel",
                            className: 'btn-secondary btn-sm',
                        },
                        ok: {
                            label: "Save",
                            className: 'btn-success btn-sm',
                            callback: function(){
                                var inputElm = document.querySelector('input[name=tags]');

                                send_data = {}
                                send_data["namespace_id"] = json["id"]
                                send_data["data"] = inputElm.value;

                                $.ajax({
                                     type: "POST",
                                     url: "/namespaces/set_user_list",
                                     data: JSON.stringify(send_data),
                                     contentType: "application/json; charset=utf-8",
                                     dataType: "json",
                                     success: function(data) {
                                         //
                                     },
                                     error: function(xhr, ajaxOptions, thrownError) {
                                         //
                                     },
                                     complete: function(data) {
                                            try {
                                                showMessage(data.responseJSON["status"], data.responseJSON["msg"])
                                            } catch {

                                            }
                                        }
                                });

                            }
                        }
                    }
              });

            var elementsDELUSERArray = DOMRegex(/^user_btn_/);

            elementsDELUSERArray.forEach(function(elem) {
                elem.addEventListener("click", DeleteUserFromNamespace);
            });
        }
    });


    $.ajax({
             type: "POST",
             url: "/namespaces/get_user_list",
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

                   var inputElm = document.querySelector('input[name=users]');

                   var tagify = new Tagify(inputElm, {
                        tagTextProp: 'name', // very important since a custom template is used with this property as text. allows typing a "value" or a "name" to match input with whitelist
                        enforceWhitelist: true,
                        skipInvalid: true, // do not remporarily add invalid tags
                        dropdown: {
                            closeOnSelect: false,
                            enabled: 0,
                            classname: 'users-list',
                            searchKeys: ['name', 'email']  // very important to set by which keys to search for suggesttions when typing
                        },
                        templates: {
                            tag: tagTemplate,
                            dropdownItem: suggestionItemTemplate
                        },
                        whitelist: data.responseJSON["user_list"]
                    })

                    tagify.on('dropdown:show dropdown:updated', onDropdownShow)
                    tagify.on('dropdown:select', onSelectSuggestion)

                    var addAllSuggestionsElm;

                    function onDropdownShow(e){
                        var dropdownContentElm = e.detail.tagify.DOM.dropdown.content;

                        if( tagify.suggestedListItems.length > 1 ){
                            addAllSuggestionsElm = getAddAllSuggestionsElm();

                            // insert "addAllSuggestionsElm" as the first element in the suggestions list
                            dropdownContentElm.insertBefore(addAllSuggestionsElm, dropdownContentElm.firstChild)
                        }
                    }

                    function onSelectSuggestion(e){
                        if( e.detail.elm == addAllSuggestionsElm )
                            tagify.dropdown.selectAll.call(tagify);
                    }

                    // create a "add all" custom suggestion element every time the dropdown changes
                    function getAddAllSuggestionsElm(){
                        // suggestions items should be based on "dropdownItem" template
                        return tagify.parseTemplate('dropdownItem', [{
                                class: "addAll",
                                name: "Add all",
                                email: tagify.settings.whitelist.reduce(function(remainingSuggestions, item){
                                    return tagify.isTagDuplicate(item.value) ? remainingSuggestions : remainingSuggestions + 1
                                }, 0) + " Members"
                            }]
                          )
                    }
             }
    });

    $.ajax({
             type: "POST",
             url: "/namespaces/get_group_list",
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

                   var inputElm = document.querySelector('input[name=groups]');

                   var tagify = new Tagify(inputElm, {
                        tagTextProp: 'name', // very important since a custom template is used with this property as text. allows typing a "value" or a "name" to match input with whitelist
                        enforceWhitelist: true,
                        skipInvalid: true, // do not remporarily add invalid tags
                        dropdown: {
                            closeOnSelect: false,
                            enabled: 0,
                            classname: 'users-list',
                            searchKeys: ['name']  // very important to set by which keys to search for suggesttions when typing
                        },
                        templates: {
                            tag: tagTemplate,
                            dropdownItem: suggestionGroupTemplate
                        },
                        whitelist: data.responseJSON["group_list"]
                    })

                    tagify.on('dropdown:show dropdown:updated', onDropdownShow)
                    tagify.on('dropdown:select', onSelectSuggestion)

                    var addAllSuggestionsElm;

                    function onDropdownShow(e){
                        var dropdownContentElm = e.detail.tagify.DOM.dropdown.content;

                        if( tagify.suggestedListItems.length > 1 ){
                            addAllSuggestionsElm = getAddAllSuggestionsElm();

                            // insert "addAllSuggestionsElm" as the first element in the suggestions list
                            dropdownContentElm.insertBefore(addAllSuggestionsElm, dropdownContentElm.firstChild)
                        }
                    }

                    function onSelectSuggestion(e){
                        if( e.detail.elm == addAllSuggestionsElm )
                            tagify.dropdown.selectAll.call(tagify);
                    }

                    // create a "add all" custom suggestion element every time the dropdown changes
                    function getAddAllSuggestionsElm(){
                        // suggestions items should be based on "dropdownItem" template
                        return tagify.parseTemplate('dropdownItem', [{
                                class: "addAll",
                                name: "Add all",
                                email: tagify.settings.whitelist.reduce(function(remainingSuggestions, item){
                                    return tagify.isTagDuplicate(item.value) ? remainingSuggestions : remainingSuggestions + 1
                                }, 0) + " Members"
                            }]
                          )
                    }
             }
    });

}

function DeleteUserFromNamespace(evt){

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["namespaceid"] = attrs["data-namespaceid"].nodeValue;
        evt.target.parentElement.className = "d-none";
    } catch {
        var attrs = evt.target.attributes
        json["namespaceid"] = attrs["data-namespaceid"].nodeValue;
        evt.target.className = "d-none";
    }

    json["userid"] = attrs["data-userid"].nodeValue;

    $.ajax({
        type: "POST",
        url: "/namespaces/del_user",
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
               showMessage(data.responseJSON["status"], data.responseJSON["msg"])
           }
    });

}
