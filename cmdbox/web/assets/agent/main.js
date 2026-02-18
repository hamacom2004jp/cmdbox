$(() => {
    try {
        // SVGロゴ初期化
        init_svglogo();
        $('.split-pane').splitPane();
        // agent初期化
        agentView.initView();
        // モーダルボタン初期化
        cmdbox.init_modal_button();
    } finally {
        cmdbox.hide_loading();
    }
});
