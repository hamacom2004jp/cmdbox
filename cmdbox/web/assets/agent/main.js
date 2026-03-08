$(() => {
    try {
        // SVGロゴ初期化
        init_svglogo();
        $('.split-pane').splitPane();
        // agent初期化
        agentView.initView();
        // バージョン情報モーダル初期化
        cmdbox.init_version_modal();
        // モーダルボタン初期化
        cmdbox.init_modal_button();
    } finally {
        cmdbox.hide_loading();
    }
});
