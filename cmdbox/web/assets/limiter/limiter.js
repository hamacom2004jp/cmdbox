const limiter_page = {};

/**
 * limiter save コマンドのフォーム定義を取得
 */
limiter_page.get_limiter_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('limiter', 'save');
    const vform_names = ['limiter_name', 'scope', 'target_mode', 'target_cmd', 'target_option',
        'max_registrations', 'max_total_count', 'max_total_time',
        'max_total_input', 'max_total_process', 'max_total_output',
        'exec_period_start', 'exec_period_end', 'refresh_datetime', 'refresh_interval'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

/**
 * limiter の編集フォームを動的に構築
 */
limiter_page.build_limiter_form = async () => {
    const form = $('#limiter_form_content');
    form.empty();
    const defs = await limiter_page.get_limiter_form_def();
    const modal = $('#limiter_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, modal, form, row, null);
    });
};

/**
 * バイト数を人が読みやすい形式に変換
 */
limiter_page.fmt_bytes = (n) => {
    if (n == null) return '-';
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
    return `${(n / 1024 / 1024 / 1024).toFixed(2)} GB`;
};

/**
 * null値を '-' に変換
 */
limiter_page.fmt_val = (v) => (v == null || v === '') ? '-' : v;

/**
 * datetime文字列から datetime-local input 用の文字列に変換
 */
limiter_page.to_dt_local = (s) => {
    if (!s) return '';
    // "2024-01-01 00:00:00" または "2024-01-01T00:00:00" を "2024-01-01T00:00:00" に
    return s.replace(' ', 'T').substring(0, 19);
};

/**
 * 進捗バーを生成して返す
 */
limiter_page.make_progress = (label, current, max, fmt_func) => {
    if (max == null) {
        // 上限なし: 現在値だけ表示
        return $(`<div class="mb-1">
            <div class="d-flex justify-content-between">
                <small class="text-secondary i18n">${label}</small>
                <small class="text-info">${fmt_func ? fmt_func(current) : limiter_page.fmt_val(current)}</small>
            </div>
        </div>`);
    }
    const pct = max > 0 ? Math.min(100, Math.round((current || 0) / max * 100)) : 0;
    const color = pct >= 90 ? 'bg-danger' : pct >= 70 ? 'bg-warning' : 'bg-info';
    const cur_str = fmt_func ? fmt_func(current || 0) : (current || 0);
    const max_str = fmt_func ? fmt_func(max) : max;
    return $(`<div class="mb-1">
        <div class="d-flex justify-content-between">
            <small class="text-secondary i18n">${label}</small>
            <small class="text-info">${cur_str} / ${max_str} (${pct}%)</small>
        </div>
        <div class="progress" style="height:6px;">
            <div class="progress-bar ${color}" role="progressbar" style="width:${pct}%" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
    </div>`);
};

/**
 * target_option を表示用文字列に変換
 */
limiter_page.fmt_target_opt = (opt) => {
    if (!opt) return '<span class="i18n">(all commands)</span>';
    if (Array.isArray(opt)) {
        return opt.map(o => limiter_page.fmt_target_opt(o)).join(', ');
    }
    const parts = Object.entries(opt).map(([k, v]) => `<span class="badge bg-secondary me-1">${k}=${v}</span>`);
    return parts.join('');
};

/**
 * 現在のスコープを取得
 */
limiter_page.get_scope = () => $('#scope_select').val() || 'server';

/**
 * フィルタ select ボックスを初期化（モード一覧を取得して表示）
 */
limiter_page.init_filter_options = async () => {
    try {
        const opts = await cmdbox.get_cmd_choices('limiter', 'save');
        // target_mode の options を取得
        const target_mode_opt = opts.find(o => o.opt === 'target_mode');
        if (target_mode_opt && target_mode_opt.choice) {
            const mode_select = $('#filter_target_mode');
            mode_select.empty();
            target_mode_opt.choice.forEach(mode => {
                const val = typeof mode === 'object' ? Object.keys(mode)[0] : mode;
                mode_select.append(`<option value="${val}">${val}</option>`);
            });
        }
    } catch (e) {
        console.log('Failed to init filter options:', e);
    }
};

/**
 * 選択されたモードに対応するコマンド一覧を取得して filter_target_cmd を初期化
 */
limiter_page.init_filter_cmds = async (mode) => {
    const cmd_select = $('#filter_target_cmd');
    cmd_select.empty();
    if (!mode) return;
    // 選択されたモードに対応するコマンド一覧を取得
    const cmds = await get_cmds(mode);
    if (cmds && Array.isArray(cmds)) {
        cmds.forEach(cmd => {
            cmd_select.append(`<option value="${cmd}">${cmd}</option>`);
        });
    }
};

/**
 * Targets タブのデータを読み込んで描画
 */
limiter_page.load_targets = async () => {
    cmdbox.show_loading();
    const scope = limiter_page.get_scope();
    const filter_target_mode = $('#filter_target_mode').val();
    const filter_target_cmd = $('#filter_target_cmd').val();
    
    const payload = {
        mode: 'limiter',
        cmd: 'targets',
        scope: scope
    };
    // フィルタ条件がある場合のみ追加
    if (filter_target_mode) payload.filter_target_mode = filter_target_mode.trim();
    if (filter_target_cmd) payload.filter_target_cmd = filter_target_cmd.trim();
    
    let res;
    try {
        res = await cmdbox.sv_exec_cmd(payload);
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    if (!res) { cmdbox.message({ warn: 'No response from server.' }, true, true); return; }
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success']) {
        cmdbox.message(res, true, true);
        return;
    }
    await limiter_page.render_targets(first['success']['data'] || []);
};

/**
 * Targets タブの描画
 */
limiter_page.render_targets = async (targets) => {
    const area = $('#targets_area').empty();
    if (!targets || targets.length === 0) {
        area.append('<div class="col-12 text-muted p-3 i18n">No LimitedFeature targets found.</div>');
        return;
    }
    const is_limiter_save = await cmdbox.check_cmd('limiter', 'save');
    for (const target of targets) {
        const mode = Array.isArray(target.mode) ? target.mode.join('/') : (target.mode || '');
        const cmd = target.cmd || '';
        const limiters = target.limiters || [];
        const col = $(`<div class="col-12 col-md-6 col-xl-4"></div>`).appendTo(area);
        const card = $(`<div class="card h-100 border-start border-4" style="border-left-color:var(--bs-info)!important;"></div>`).appendTo(col);
        const card_header = $(`<div class="doc-header d-flex align-items-center gap-2"></div>`).appendTo(card);
        card_header.append(`<span class="badge rounded-pill text-bg-primary">mode</span><strong>${mode}</strong>`);
        card_header.append(`<span class="badge rounded-pill text-bg-success ms-2">cmd</span><strong>${cmd}</strong>`);
        card_header.append(`<span class="ms-auto badge ${limiters.length > 0 ? 'rounded-pill text-bg-info' : 'text-body text-opacity-75'}">${limiters.length} limiter${limiters.length !== 1 ? 's' : ''}</span>`);

        if (is_limiter_save) {
            // 「＋」ボタンを追加（mode/cmd をデフォルト値として渡す）
            const btn_add = $(`<button type="button" class="btn btn-sm btn-outline-secondary ms-2" title="Add limiter"><i class="fas fa-plus"></i></button>`);
            btn_add.on('click', () => limiter_page.open_edit_modal(null, { target_mode: mode, target_cmd: cmd }));
            card_header.append(btn_add);
        }

        const card_body = $(`<div class="card-body p-2"></div>`).appendTo(card);
        if (limiters.length === 0) {
            card_body.append('<small class="text-secondary i18n">No limiters applied.</small>');
            continue;
        }
        for (const lm of limiters) {
            limiter_page._render_limiter_item(card_body, lm, true);
        }
    }
    cmdbox.hide_loading();
};



/**
 * 制限設定カードアイテムを親要素に追加 (Targets ビュー内)
 */
limiter_page._render_limiter_item = (parent, lm, show_counter) => {
    const item = $(`<div class="border rounded p-2 mb-2 bg-body-tertiary"></div>`).appendTo(parent);
    const name_row = $(`<div class="d-flex align-items-center mb-1 gap-1"></div>`).appendTo(item);
    name_row.append(`<i class="fas fa-lock fa-sm text-info me-1"></i><strong class="me-auto">${lm.limiter_name || ''}</strong>`);
    name_row.append(`<span class="badge bg-secondary">${lm.scope || ''}</span>`);
    // target_mode/target_cmd
    //item.append(`<div class="mb-1"><small class="i18n me-1">Target Mode:</small><span class="badge bg-info text-dark">${limiter_page.fmt_val(lm.target_mode)}</span></div>`);
    //item.append(`<div class="mb-1"><small class="i18n me-1">Target Cmd:</small><span class="badge bg-success">${limiter_page.fmt_val(lm.target_cmd)}</span></div>`);

    // target_option
    if (lm.target_option) {
        item.append(`<div class="mb-1"><small class="i18n me-1">Conditions:</small>${limiter_page.fmt_target_opt(lm.target_option)}</div>`);
    }
    // 期間
    if (lm.exec_period_start || lm.exec_period_end) {
        item.append(`<div class="mb-1"><small class="i18n me-1">Period: </small><small>${limiter_page.fmt_val(lm.exec_period_start)} ~ ${limiter_page.fmt_val(lm.exec_period_end)}</small></div>`);
    }
    // リフレッシュ
    if (lm.refresh_interval || lm.refresh_datetime) {
        let rf = '';
        if (lm.refresh_interval) rf += `<small class="i18n">every </small><small>${lm.refresh_interval}s</small> `;
        if (lm.refresh_datetime) rf += `<small class="i18n">reset at </small><small>${lm.refresh_datetime}</small>`;
        item.append(`<div class="mb-1"><small class="i18n">Refresh: </small>${rf}</div>`);
    }

    // 制限値とカウンター
    const counter = lm.counter || {};
    const last_refresh = counter.last_refresh;
    const progress_area = $(`<div class="mt-1"></div>`).appendTo(item);

    limiter_page.make_progress('Count', counter.total_count, lm.max_total_count, null).appendTo(progress_area);
    limiter_page.make_progress('Time (s)', counter.total_time, lm.max_total_time, (v) => v != null ? `${typeof v === 'number' ? v.toFixed(1) : v}s` : '-').appendTo(progress_area);
    limiter_page.make_progress('Input', counter.total_input, lm.max_total_input, limiter_page.fmt_bytes).appendTo(progress_area);
    limiter_page.make_progress('Process', counter.total_process, lm.max_total_process, limiter_page.fmt_bytes).appendTo(progress_area);
    limiter_page.make_progress('Output', counter.total_output, lm.max_total_output, limiter_page.fmt_bytes).appendTo(progress_area);
    limiter_page.make_progress('Registrations', counter.total_registrations, lm.max_registrations, limiter_page.fmt_bytes).appendTo(progress_area);

    if (last_refresh) {
        progress_area.append(`<div><small class="i18n">Last reset: </small><small>${last_refresh}</small></div>`);
    }

    // 操作ボタン
    const btn_row = $(`<div class="d-flex gap-2 mt-2"></div>`).appendTo(item);
    const btn_edit = $(`<button type="button" class="btn btn-sm btn-outline-info i18n">Edit</button>`).appendTo(btn_row);
    const btn_del = $(`<button type="button" class="btn btn-sm btn-outline-danger i18n">Delete</button>`).appendTo(btn_row);
    btn_edit.on('click', () => limiter_page.open_edit_modal(lm.limiter_name));
    btn_del.on('click', () => limiter_page.delete_limiter(lm.limiter_name));
};

/**
 * 制限設定の編集モーダルを開く (name=null で新規作成)
 * defaults: { target_mode, target_cmd } で初期値を設定可能
 */
limiter_page.open_edit_modal = async (name, defaults) => {
    const modal = $('#limiter_modal');
    const is_new = !name;
    const scope = limiter_page.get_scope();

    // フォーム構築
    cmdbox.show_loading();
    try {
        await limiter_page.build_limiter_form();
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    modal.find('#cmd_limiter_del').addClass('d-none');
    if (is_new) {
        modal.find('.modal-title').text('New Limiter');
        // デフォルト値を設定
        const form = $('#limiter_form_content');
        form.find('[name="scope"]').val(scope);
        // defaults から target_mode/target_cmd を設定
        if (defaults) {
            if (defaults.target_mode) form.find('[name="target_mode"]').val(defaults.target_mode);
            if (defaults.target_cmd) {
                const res = await get_cmds($("[name='target_mode']").val());
                form.find("[name='target_cmd']").empty();
                res.map(elm=>{form.find("[name='target_cmd']").append('<option value="'+elm+'">'+elm+'</option>');});
                form.find('[name="target_cmd"]').val(defaults.target_cmd);
            }
        }
        cmdbox.process_i18n(modal);
        cmdbox.hide_loading();
        modal.modal('show');
        return;
    }
    // 既存の設定をロード
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'load', scope: scope, limiter_name: name });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success']) {
        cmdbox.hide_loading();
        cmdbox.message(res, true, true);
        return;
    }
    const cfg = first['success']['data'] || {};
    modal.find('.modal-title').text(`Edit Limiter: ${name}`);
    modal.find('#cmd_limiter_del').removeClass('d-none');
    // 設定値を form にセット
    const form = $('#limiter_form_content');
    Object.keys(cfg).forEach(key => {
        const input = form.find(`[name="${key}"]`);
        if (input.length > 0) {
            if (key === 'exec_period_start' || key === 'exec_period_end' || key === 'refresh_datetime') {
                // datetime 型は変換が必要
                input.val(limiter_page.to_dt_local(cfg[key]));
            } else {
                input.val(cfg[key]);
            }
        }
    });
    if (cfg['target_mode']) {
        form.find('[name="target_mode"]').val(cfg['target_mode']);
        const res = await get_cmds(cfg['target_mode']);
        form.find("[name='target_cmd']").empty();
        res.map(elm=>{form.find("[name='target_cmd']").append('<option value="'+elm+'">'+elm+'</option>');});
        form.find('[name="target_cmd"]').val(cfg['target_cmd']);
    }

    cmdbox.process_i18n(modal);
    cmdbox.hide_loading();
    modal.modal('show');
};

/**

 * 制限設定を保存
 */
limiter_page.save_limiter = async () => {
    const form = $('#limiter_form_content');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    if (!data.limiter_name || !data.limiter_name.trim()) {
        cmdbox.message({ warn: 'Limiter Name is required.' }, true, true);
        return;
    }

    const payload = {
        mode: 'limiter',
        cmd: 'save',
        ...data
    };

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd(payload);
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success'] || !first['success']['data']) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first['success']['data'], true, true);
    $('#limiter_modal').modal('hide');
    await limiter_page.refresh_all();
};

/**
 * 制限設定を削除
 */
limiter_page.delete_limiter = async (name) => {
    if (!name) return;
    const confirmed = await cmdbox.confirm({ warn: `Delete limiter "${name}"?` }, true);
    if (!confirmed) return;

    const scope = limiter_page.get_scope();
    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'del', scope: scope, limiter_name: name });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success'] || !first['success']['data']) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first['success']['data'], true, true);
    $('#limiter_modal').modal('hide');
    await limiter_page.refresh_all();
};

/**
 * Targets タブのデータを再読み込み
 */
limiter_page.refresh_all = async () => {
    await limiter_page.load_targets();
};
