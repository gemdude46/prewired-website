var gui_open;

onload = function() {
    if (un === decodeURI(location.href.split('=')[1].replace(/\+/, ' '))) {
        // This is the users profile
        ImportCSS('//gemdude46.github.io/libs/+.css');                          // For class="darken-on-hover"
        document.getElementById('about').insertBefore(
            createElement('IMG', {                                              // Create the edit profile button
                src: '/static/edit.png',
                style: 'float: right; border: 1px solid #555; border-radius: 4px; cursor: pointer;',
                class: 'darken-on-hover'
            }, null, [
                ['click', function(){
                    if (!gui_open) {
                        body.appendContent(
                            createElement('DIV', {
                                style: 'position: absolute; top: 25%; left: 25%; width: 50%; height: 50%;'+
                                        'box-shadow: 10px 10px 18px black; background-color: white;'
                            }, '<h2 style="text-align:center;">Edit profile description</h2>' +             // This is the
                               '<center><textarea style="width:80%;height:25vh;resize:none;">' +            // code for the
                                md +                                                                        // edit profile
                               '</textarea><br><br><button onclick="updDesc();">Update</button></center>')  // gui. Dont ask.
                        );
                        gui_open = true;
                    }
                }]
            ]),
            document.getElementById('avatar')                                   // Put it here for floating
        );
    }
};

// Send update to server
function updDesc() {
    var text = document.getElementsByTagName('textarea')[0].value;
    AJAX('POST', '/update_profile/desc', JSON.stringify({'text': text}), function(x){
        if (x.status == 200) location.reload(true);
    });
}
