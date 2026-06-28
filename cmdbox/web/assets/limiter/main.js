$(() => {
    // フッター
    cmdbox.copyright();
    // バージョン情報
    cmdbox.init_version_modal();
    
    // ===== Limiter (limiters) タブのイベント =====
    // フィルタ条件の変更
    $('#filter_target_mode').on('change', async () => {
        const mode = $('#filter_target_mode').val();
        await limiter_page.init_filter_cmds(mode);
    });
    // リフレッシュボタン (limiters)
    $('#btn_refresh').on('click', () => limiter_page.refresh_all());
    // target_option 追加ボタン
    $('#btn_add_target_opt').on('click', () => limiter_page._add_target_opt_row());
    // Limiter 保存ボタン
    $('#cmd_limiter_save').on('click', () => limiter_page.save_limiter());
    // Limiter 削除ボタン
    $('#cmd_limiter_del').on('click', () => {
        const name = $('#lm_limiter_name').val().trim();
        limiter_page.delete_limiter(name);
    });
    
    // ===== Plan タブのイベント =====
    // Plans タブクリック時に初期化
    $('#plans-tab').on('show.bs.tab', async () => {
        // Plans タブ用の scope_select を隠す/表示
        $('#filter_target_mode').closest('.input-group').closest('div').addClass('d-none');
        $('#filter_target_cmd').closest('.input-group').closest('div').addClass('d-none');
        await limiter_plan_page.load_plans();
    });
    // limiters タブクリック時
    $('#limiters-tab').on('show.bs.tab', async () => {
        $('#filter_target_mode').closest('.input-group').closest('div').removeClass('d-none');
        $('#filter_target_cmd').closest('.input-group').closest('div').removeClass('d-none');
        limiter_page.refresh_all();
    });
    
    // Plans リフレッシュボタン
    $('#btn_plan_refresh').on('click', () => limiter_plan_page.refresh_all());
    // Plans 新規作成ボタン
    $('#btn_plan_add').on('click', () => limiter_plan_page.open_edit_modal(null));
    // Plan 保存ボタン
    $('#cmd_plan_save').on('click', () => limiter_plan_page.save_plan());
    // Plan 削除ボタン
    $('#cmd_plan_del').on('click', () => {
        const name = $('#plan_form_content').find('[name="plan_name"]').val().trim();
        limiter_plan_page.delete_plan(name);
    });
    const plan_modal = $('#plan_modal');
    // モーダルボタン初期化
    cmdbox.init_modal_button();
    // モーダルのドラッグ対応
    cmdbox.modal_draggable($('#limiter_modal'));
    cmdbox.modal_draggable(plan_modal);
    
    // 初期化とデータ読み込み
    (async () => {
        await limiter_page.init_filter_options();
        await limiter_plan_page.load_plans();
        // 多言語対応のためのテキスト翻訳を処理
        setTimeout(() => {cmdbox.process_i18n();}, 100);
    })();
});
