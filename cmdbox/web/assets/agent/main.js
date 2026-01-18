$(() => {
    try {
        cmdbox.appid('#logo_title').then(() => {
            $('#logo_title').text(`${document.title} Agent`);
        });
        $('.split-pane').splitPane();
        // agent初期化
        agentView.initView();
    } finally {
        cmdbox.hide_loading();
    }
});
