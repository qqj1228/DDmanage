// upload.js
// 使用WebUploader组件实现文件上传功能
// 官网地址：http://fex.baidu.com/webuploader/

$(function() {
    var $ = jQuery,
        $list = $('#thelist'),
        $btn = $('#ctlBtn'),
        $arc = $("#archive"),
        state = 'pending',
        uploader;

    uploader = WebUploader.create({

        // 不压缩image
        resize: false,

        // swf文件路径
        swf: 'http://cdn.staticfile.org/webuploader/0.1.5/Uploader.swf',

        // 文件接收服务端。
        server: '/api/upload',

        // 选择文件的按钮。可选。
        // 内部根据当前运行时创建，可能是input元素，也可能是flash.
        pick: '#picker'
    });
    // 当有文件添加进来的时候
    uploader.on( 'fileQueued', function( file ) {
        $list.append( '<div id="' + file.id + '" class="uk-panel uk-panel-box uk-margin-bottom">' +
            '<div class=""><i class="uk-icon-file"></i> ' + file.name + '</div>' +
            '<span class="state uk-panel-badge uk-badge">等待上传</span>' +
        '</div>' );
    });

    // 文件上传过程中创建进度条实时显示。
    uploader.on( 'uploadProgress', function( file, percentage ) {
        var $li = $( '#'+file.id ),
            $percent = $li.find('.uk-progress .uk-progress-bar');

        // 避免重复创建
        if ( !$percent.length ) {
            $percent = $('<div class="uk-progress uk-progress-mini uk-active">' +
              '<div class="uk-progress-bar" style="width: 0%">' +
              '</div>' +
            '</div>').appendTo( $li ).find('.uk-progress-bar');
        }

        $li.find('span.state').text('正在上传').addClass("uk-badge-warning");

        $percent.css( 'width', percentage * 100 + '%' );
    });

    uploader.on( 'uploadSuccess', function( file, response ) {
        if (response.message){
            $( '#'+file.id ).find('span.state').text('上传出错: ' + response.message).removeClass("uk-badge-warning").addClass("uk-badge-danger");
        }else{
            $( '#'+file.id ).find('span.state').text('上传完毕').removeClass("uk-badge-warning").addClass("uk-badge-success");
        }
    });

    uploader.on( 'uploadError', function( file ) {
        $( '#'+file.id ).find('span.state').text('网络出错').removeClass("uk-badge-warning").addClass("uk-badge-danger");
    });

    uploader.on( 'uploadComplete', function( file ) {
        $( '#'+file.id ).find('.uk-progress').fadeOut();
    });

    uploader.on( 'all', function( type ) {
        if ( type === 'startUpload' ) {
            state = 'uploading';
        } else if ( type === 'stopUpload' ) {
            state = 'paused';
        } else if ( type === 'uploadFinished' ) {
            state = 'done';
        }

        if ( state === 'uploading' ) {
            $btn.text('暂停上传');
            $arc.text('暂停入库');
        } else {
            $btn.text('开始上传');
            $arc.text('图纸入库');
        }
    });

    $btn.on( 'click', function() {
        if ( state === 'uploading' ) {
            uploader.stop();
        } else {
            uploader.upload();
        }
    });

    $arc.on( 'click', function() {
        uploader.option('server', '/api/archive');
        if ( state === 'uploading' ) {
            uploader.stop();
        } else {
            uploader.upload();
        }
    });
});
