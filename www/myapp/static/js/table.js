function bat_checkbox(url_ajax, url_ret, personal){
    // 因表头的checkbox无next元素，故返回的元素没有包含表头
    var filelinks = $('input[name="subcheck"]:checked').parent().next().find('a');
    var dir = $('input[name="subcheck"]:checked').parent().next().next();
    var filelist = [];
    for (var i=0; i<filelinks.length; i++){
        filelist.push([$(filelinks[i]).text(), $(dir[i]).text()]);
    }
    if(filelist.length > 0){
        postJSON(url_ajax, {
            filelist: filelist,
            personal: personal
            }, function(err, r){
            if (err) {
                if(err.code == "403"){
                    err.message = "您没有权限访问该页面/资源!"
                }
                error(err);
                return;
            }
            if(url_ret === ''){
                location.assign(r.url);
            }else{
                location.assign(url_ret);
            }
        });
    }
}

function button(button, url_ajax, url_ret, personal){
    var filename = $(button).parent().parent().prev().prev().find('a').text();
    var dirname = $(button).parent().parent().prev().text();
    var filelist = [[filename, dirname]];
    postJSON(url_ajax, {
        filelist: filelist,
        personal: personal
        }, function(err, r){
        if (err) {
            if(err.code == "403"){
                err.message = "您没有权限访问该页面/资源!"
            }
            error(err);
            return;
        }
        if(url_ret === ''){
            location.assign(r.url);
        }else{
            location.assign(url_ret);
        }
    });
}
