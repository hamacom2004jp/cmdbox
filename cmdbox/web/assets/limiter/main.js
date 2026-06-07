$(() => {
    // フッター
    cmdbox.copyright();
    // バージョン情報
    cmdbox.init_version_modal();
    // スコープ変更
    $('#scope_select').on('change', () => limiter_page.refresh_all());
    // フィルタ条件の変更
    $('#filter_target_mode').on('change', async () => {
        const mode = $('#filter_target_mode').val();
        await limiter_page.init_filter_cmds(mode);
    });
    // リフレッシュボタン
    $('#btn_refresh').on('click', () => limiter_page.refresh_all());
    // target_option 追加ボタン
    $('#btn_add_target_opt').on('click', () => limiter_page._add_target_opt_row());
    // 保存ボタン
    $('#cmd_limiter_save').on('click', () => limiter_page.save_limiter());
    // 削除ボタン
    $('#cmd_limiter_del').on('click', () => {
        const name = $('#lm_limiter_name').val().trim();
        limiter_page.delete_limiter(name);
    });
    // モーダルのドラッグ対応
    cmdbox.modal_draggable($('#limiter_modal'));
    // 初期化とデータ読み込み
    (async () => {
        await limiter_page.init_filter_options();
        limiter_page.refresh_all();
    })();
    // 多言語対応のためのテキスト翻訳を処理
    setTimeout(() => {cmdbox.process_i18n();}, 100);
});
