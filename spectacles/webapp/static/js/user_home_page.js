function init_crop() {
    // Create variables (in this scope) to hold the API and image size
    var jcrop_api,
        boundx,
        boundy,
        // Grab some information about the preview pane
        $preview = $("#preview-box"),
        $pcnt = $("#preview-box .preview-box"),
        $pimg = $("#preview-box .preview-box img"),
        xsize = $pcnt.width(),
        ysize = $pcnt.height();

    $("#crop-box").Jcrop(
        {
            onChange: updatePreview,
            onSelect: updateCoords,
            setSelect: [0, 0, 150, 150],
            aspectRatio: 1,
        },
        function () {
            // Use the API to get the real image size
            var bounds = this.getBounds();
            boundx = bounds[0];
            boundy = bounds[1];
            // Store the API in the jcrop_api variable
            jcrop_api = this;

            jcrop_api.focus();
            // Move the preview into the jcrop container for css positioning
            $preview.appendTo(jcrop_api.ui.holder);
        }
    );

    function updatePreview(c) {
        if (parseInt(c.w) > 0) {
            var rx = xsize / c.w;
            var ry = ysize / c.h;
            $pimg.css({
                width: Math.round(rx * boundx) + "px",
                height: Math.round(ry * boundy) + "px",
                marginLeft: "-" + Math.round(rx * c.x) + "px",
                marginTop: "-" + Math.round(ry * c.y) + "px",
            });
        }
    }
}

function updateCoords(c) {
    $("#x").val(c.x);
    $("#y").val(c.y);
    $("#w").val(c.w);
    $("#h").val(c.h);
}

function DOMRegex(regex) {
    let output = [];
    for (let i of document.querySelectorAll("*")) {
        if (regex.test(i.id)) {
            // or whatever attribute you want to search
            output.push(i);
        }
    }
    return output;
}

function SetAllEventListeners() {
    var change_profile_image = document.getElementById("change_profile_image");
    change_profile_image.addEventListener("click", ChangeProfilePic);
}

function ChangeProfilePic() {
    var dialog = bootbox
        .dialog({
            size: "small",
            title: "Change profile picture",
            show: false, // We will show it manually later
            message: `<form id="upload_pic" action="/avatars/upload" method="post" enctype="multipart/form-data">
                        <label class="text-muted">File Browser</label>
                        <div class="custom-file">
                          <input type="file" class="custom-file-input" id="customFile" name="filename">
                          <label class="custom-file-label" for="customFile">Choose file</label>
                        </div>
                        <button class="btn btn-sm btn-success btn_prof_pic" type="submit">upload</button>
                    </form>`,
        })
        .modal("show");

    $(".custom-file-input").on("change", function () {
        var fileName = $(this).val().split("\\").pop();
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });
}
