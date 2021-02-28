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

    var elementsADDUSERArray = DOMRegex(/^add_user_/);

    elementsADDUSERArray.forEach(function(elem) {
        elem.addEventListener("click", AddUserForm);
    });

    var elementsDELGMEMArray = DOMRegex(/^user_btn_/);

    elementsDELGMEMArray.forEach(function(elem) {
        elem.addEventListener("click", DeleteGroupMember);
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

var tagify = null

function AddUserForm(evt){

    json = {}

    try {
        var attrs = evt.target.parentElement.attributes
        json["id"] = attrs["data-id"].nodeValue;
    } catch {
        var attrs = evt.target.attributes
        json["id"] = attrs["data-id"].nodeValue;
    }

    json["name"] = attrs["data-name"].nodeValue;

    var dialog = bootbox.dialog({
        title: 'Select users to assign to the group: ' + json["name"],
        message: "<input name='tags' value='' placeholder='write usernames or select below'>",
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
                    send_data["group_id"] = json["id"]
                    send_data["data"] = inputElm.value;

                    $.ajax({
                         type: "POST",
                         url: "/groups/set_user_list",
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
                                if(data.responseJSON.hasOwnProperty('group_data')){
                                    $("#group_data").html(data.responseJSON["group_data"]);
                                }

                                SetAllEventListeners()

                                showMessage(data.responseJSON["status"], data.responseJSON["msg"])
                            }
                        });
                }
            }
        }
    });

    $.ajax({
             type: "POST",
             url: "/groups/get_user_list",
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

                   var inputElm = document.querySelector('input[name=tags]');

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

}

function DeleteGroup(evt){

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
                   if(data.responseJSON.hasOwnProperty('group_data')){
                        $("#group_data").html(data.responseJSON["group_data"]);
                   }

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });
}


function DeleteGroupMember(evt){

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
             url: "/groups/del_groupmember",
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
                   if(data.responseJSON.hasOwnProperty('group_data')){
                        $("#group_data").html(data.responseJSON["group_data"]);
                   }

                   SetAllEventListeners()

                   showMessage(data.responseJSON["status"], data.responseJSON["msg"])
             }
         });

}
