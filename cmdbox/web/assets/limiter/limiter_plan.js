const limiter_plan_page = {};

/**
 * limiter plan save コマンドのフォーム定義を取得
 */
limiter_plan_page.get_plan_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('limiter', 'plan_save');
    const vform_names = ['plan_name', 'plan_title', 'plan_desc', 'limiters',
        'plan_start', 'plan_end', 'open_date', 'suspend_date', 'notice_date',
        'billing_type', 'billing_period_unit', 'billing_period_qty',
        'billing_limiter', 'billing_min_amount', 'billing_max_amount', 'billing_unit_price'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

/**
 * プランの編集フォームを動的に構築
 */
limiter_plan_page.build_plan_form = async () => {
    const form = $('#plan_form_content');
    form.empty();
    const defs = await limiter_plan_page.get_plan_form_def();
    const modal = $('#plan_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, modal, form, row, null);
    });
};

/**
 * 数値を人が読みやすい形式に変換
 */
limiter_plan_page.fmt_num = (n) => {
    if (n == null) return '-';
    if (typeof n === 'number') return n.toLocaleString();
    return n;
};

/**
 * null値を '-' に変換
 */
limiter_plan_page.fmt_val = (v) => (v == null || v === '') ? '-' : v;

/**
 * datetime文字列から datetime-local input 用の文字列に変換
 */
limiter_plan_page.to_dt_local = (s) => {
    if (!s) return '';
    // "2024-01-01 00:00:00" または "2024-01-01T00:00:00" を "2024-01-01T00:00:00" に
    return s.replace(' ', 'T').substring(0, 19);
};

/**
 * プラン一覧タブのデータを読み込んで描画
 */
limiter_plan_page.load_plans = async () => {
    cmdbox.show_loading();
    const payload = {
        mode: 'limiter',
        cmd: 'plan_list',
        kwd: null
    };
    
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
    await limiter_plan_page.render_plans(first['success']['data'] || []);
};

/**
 * プラン一覧の描画
 */
limiter_plan_page.render_plans = async (plans) => {
    const area = $('#plans_area').empty();
    if (!plans || plans.length === 0) {
        area.append('<div class="col-12 text-muted p-3 i18n">No plans found.</div>');
        return;
    }
    const is_plan_save = await cmdbox.check_cmd('limiter', 'plan_save');
    for (const plan of plans) {
        const col = $(`<div class="col-12 col-md-6 col-xl-4"></div>`).appendTo(area);
        const card = $(`<div class="card h-100 border-start border-4" style="border-left-color:var(--bs-success)!important;"></div>`).appendTo(col);
        const card_header = $(`<div class="doc-header d-flex align-items-center gap-2"></div>`).appendTo(card);
        
        card_header.append(`<i class="fas fa-layer-group text-success"></i><strong>${plan.plan_title || ''}</strong><span> ${' ( '+plan.name+' )' || ''}</span>`);
        if (plan.billing_type) {
            const billing_badge = plan.billing_type === 'period' ? 'bg-info' : 'bg-warning';
            card_header.append(`<span class="badge rounded-pill ${billing_badge} ms-auto">${plan.billing_type}</span>`);
        }
        
        if (is_plan_save) {
            const btn_add = $(`<button type="button" class="btn btn-sm btn-outline-secondary" title="Add Plan"><i class="fas fa-plus"></i></button>`);
            btn_add.on('click', () => limiter_plan_page.open_edit_modal(null));
            card_header.append(btn_add);
        }

        const card_body = $(`<div class="card-body p-2"></div>`).appendTo(card);
        // 説明
        if (plan.plan_desc) {
            card_body.append(`<div class="mb-1"><small class="text-muted i18n">Description:</small><br><small>${plan.plan_desc}</small></div>`);
        }
        // リミッター一覧
        if (plan.limiters && plan.limiters.length > 0) {
            const limiters_html = plan.limiters.map(l => `<span class="badge bg-info">${l}</span>`).join(' ');
            card_body.append(`<div class="mb-1"><small class="text-muted i18n">Limiters:</small><br>${limiters_html}</div>`);
        }
        
        // プラン期間
        if (plan.plan_start || plan.plan_end) {
            card_body.append(`<div class="mb-1"><small class="text-muted i18n">Plan Period:</small><br><small>${limiter_plan_page.fmt_val(plan.plan_start)} ~ ${limiter_plan_page.fmt_val(plan.plan_end)}</small></div>`);
        }
        
        // 操作ボタン
        const btn_row = $(`<div class="d-flex gap-2 mt-3"></div>`).appendTo(card_body);
        const btn_edit = $(`<button type="button" class="btn btn-sm btn-outline-info i18n">Edit</button>`).appendTo(btn_row);
        const btn_del = $(`<button type="button" class="btn btn-sm btn-outline-danger i18n">Delete</button>`).appendTo(btn_row);
        btn_edit.on('click', () => limiter_plan_page.open_edit_modal(plan.name));
        btn_del.on('click', () => limiter_plan_page.delete_plan(plan.name));
    }
    cmdbox.hide_loading();
};

/**
 * プラン編集モーダルを開く (name=null で新規作成)
 */
limiter_plan_page.open_edit_modal = async (name) => {
    const modal = $('#plan_modal');
    const is_new = !name;

    // フォーム構築
    cmdbox.show_loading();
    try {
        await limiter_plan_page.build_plan_form();
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    modal.find('#cmd_plan_del').addClass('d-none');
    if (is_new) {
        modal.find('.modal-title').text('New Plan');
        // デフォルト値を設定
        const form = $('#plan_form_content');
        form.find('[name="billing_type"]').val('period');
        cmdbox.process_i18n(modal);
        cmdbox.hide_loading();
        modal.modal('show');
        return;
    }
    
    // 既存のプラン設定をロード
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'plan_load', plan_name: name });
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
    modal.find('.modal-title').text(`Edit Plan: ${name}`);
    modal.find('#cmd_plan_del').removeClass('d-none');

    // 設定値を form にセット
    const form = $('#plan_form_content');
    Object.keys(cfg).forEach(key => {
        const input = form.find(`[name="${key}"]`);
        if (input.length > 0) {
            if (key === 'plan_start' || key === 'plan_end' || key === 'open_date' || 
                key === 'suspend_date' || key === 'notice_date') {
                // datetime 型は変換が必要
                input.val(limiter_plan_page.to_dt_local(cfg[key]));
            } else if (key === 'limiters' && Array.isArray(cfg[key])) {
                // limiters は複数値
                input.val(cfg[key].join('\n'));
            } else {
                input.val(cfg[key]);
            }
        }
    });
    // limiterリストをロード
    await cmdbox.callcmd('limiter','list',{},(res)=>{
        const val = $("[name='limiters']").val();
        $("[name='limiters']").empty().append('<option></option>');
        res['data'].map(elm=>{$('[name="limiters"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        form.find('[name="limiters"]').val(cfg.limiters);
    },$('[name="title"]').val(),'limiter');
    // billing_limiterリストをロード
    await cmdbox.callcmd('limiter','list',{},(res)=>{
        const val = $("[name='billing_limiter']").val();
        $("[name='billing_limiter']").empty().append('<option></option>');
        res['data'].map(elm=>{$('[name="billing_limiter"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        form.find('[name="billing_limiter"]').val(cfg.billing_limiter);
    },$('[name="title"]').val(),'limiter');

    cmdbox.process_i18n(modal);
    cmdbox.hide_loading();
    modal.modal('show');
};

/**
 * プランを保存
 */
limiter_plan_page.save_plan = async () => {
    const form = $('#plan_form_content');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) {
            // limiters は改行区切りの複数値
            if (item.name === 'limiters') {
                if (!data['limiters']) data['limiters'] = [];
                data['limiters'].push(item.value.trim());
            } else {
                data[item.name] = item.value;
            }
        }
    });

    if (!data.plan_name || !data.plan_name.trim()) {
        cmdbox.message({ warn: 'Plan Name is required.' }, true, true);
        return;
    }
    
    // limiters を配列から文字列配列に変換（重複を除去）
    if (data.limiters) {
        data.limiters = [...new Set(data.limiters.map(l => l.trim()).filter(l => l))];
    }

    const payload = {
        mode: 'limiter',
        cmd: 'plan_save',
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
    $('#plan_modal').modal('hide');
    await limiter_plan_page.refresh_all();
};

/**
 * プランを削除
 */
limiter_plan_page.delete_plan = async (name) => {
    if (!name) return;
    const confirmed = await cmdbox.confirm({ warn: `Delete plan "${name}"?` }, true);
    if (!confirmed) return;

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'plan_del', plan_name: name });
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
    $('#plan_modal').modal('hide');
    await limiter_plan_page.refresh_all();
};

/**
 * プラン一覧を再読み込み
 */
limiter_plan_page.refresh_all = async () => {
    await limiter_plan_page.load_plans();
};
