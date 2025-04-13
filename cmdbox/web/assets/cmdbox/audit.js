const audit = {};
// 監査ログ一覧
audit.rawlog = async () => {
    const form = $('#filter_form');
    const [title, opt] = cmdbox.get_param(form);
    cmdbox.show_loading();
    const res = await fetch(`audit/rawlog`,
        {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(opt)});
    if (res.status != 200) {
        cmdbox.message({'error':`${res.status}: ${res.statusText}`});
        cmdbox.hide_loading();
        return;
    }
    cmdbox.hide_loading();
    try {
        const content = JSON.parse(await res.text());
        if (!content['success']) {
            cmdbox.message({'error': content});
            return;
        }
        const rawlog_area = $('#rawlog_area').html('');
        render_result_func(rawlog_area, content['success']['data'], 100);
    } catch (e) {
        cmdbox.message({'error': e.message});
        return;
    }
};
// メトリクスの表示
audit.metrics = async () => {
    const metrics_area = $('#metrics_area');
    metrics_area.html('');
    audit.list_audit_metrics().then((res) => {
        if (!res['success']) return;
        res['success'].forEach((row) => {
            // 時系列グラフの追加
            const card = $('<div class="col p-1"><div class="card card-hover"><div class="card-body"></div></div></div>').appendTo(metrics_area);
            const card_body = card.find('.card-body');
            const title = $(`<div class="d-flex"><h5 class="d-inline-block">${row['title']}</h5></div>`).appendTo(card_body);
        });
    });
};
// メトリクスのモーダルダイアログを表示
audit.metrics_modal_func = (title) => {
    const modal = $('#metrics_modal');
    modal.find('.modal-title').text(title ? `Edit Metrics : ${title}` : 'New Metrics');
    const row_content = modal.find('.row_content');
    row_content.empty();
    audit.load_audit_metrics(title?title:null).then((res) => {
        const axis = ['audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_src', 'clmsg_title', 'clmsg_user', 'clmsg_body', 'clmsg_tag', 'svmsg_id', 'svmsg_date'];
        const chart = ['line', 'bar', 'pie', 'scatter', 'area', 'radar'];
        const data = res['success']?res['success']:{};
        const rows = [
            {opt:'title', type:'str', default:title?title:'', required:true, multi:false, hide:false, choice:null},
            {opt:'chart', type:'str', default:'', required:true, multi:false, hide:false, choice:chart},
            {opt:'horizontal', type:'str', default:data['horizontal']?data['horizontal']:'', required:true, multi:false, hide:false, choice:axis},
            {opt:'vertical', type:'str', default:data['vertical']?data['vertical']:'', required:true, multi:true, hide:false, choice:axis},
        ];
        rows.forEach((row, i) => cmdbox.add_form_func(i, modal, row_content, row, null, 12, 6));
    });
    // 保存実行
    modal.find('#metrics_save').off('click').on('click', async () => {
        if (!window.confirm('Do you want to save?')) return;
        await audit.save_audit_metrics(title);
        await audit.metrics();
        modal.modal('hide');
    });
    // 削除実行
    modal.find('#metrics_del').off('click').on('click', async () => {
        if (!window.confirm('Do you want to delete?')) return;
        await audit.del_audit_metrics(title);
        await audit.metrics();
        modal.modal('hide');
    });
    modal.modal('show');
};
// 監査ログのフィルターフォームの初期化
audit.init_form = async () => {
    // フォームの初期化
    const form = $('#filter_form');
    const row_content = form.find('.row_content');
    const res = await fetch('audit/mode_cmd', {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const msg = await res.json();
    if (!msg['success']) {
        cmdbox.message({'error': msg['message']});
        return;
    }
    const args = msg['success'];
    const py_get_cmd_choices = await cmdbox.get_cmd_choices(args['mode'], args['cmd']);
    row_content.html('');
    // 検索ボタンを表示
    const search_btn = $('<button type="button" class="btn btn-primary col-11 m-3">Search</button>').appendTo(row_content);
    search_btn.off('click').on('click', (e) => {
        audit.rawlog();
        const condition = {};
        row_content.find(':input').each((i, el) => {
            const elem = $(el);
            const id = elem.attr('id');
            const val = elem.val();
            if (!id || id == '') return;
            if (!val || val == '') return;
            condition[id] = {'name': elem.attr('name'), 'value': val,
                          'param_data_index': elem.attr('param_data_index'),
                          'param_data_type': elem.attr('param_data_type'),
                          'param_data_multi': elem.attr('param_data_multi')};
        });
        cmdbox.save_user_data('audit', 'condition', JSON.stringify(condition));
    });
    // 主なフィルター条件のフォームを表示
    const nml_conditions = ['filter_audit_type', 'filter_clmsg_id', 'filter_clmsg_src', 'filter_clmsg_title', 'filter_clmsg_title', 'filter_clmsg_user',
                        'filter_clmsg_tag', 'filter_svmsg_sdate', 'filter_svmsg_edate']
    py_get_cmd_choices.filter(row => nml_conditions.includes(row.opt)).forEach((row, i) => cmdbox.add_form_func(i, form, row_content, row, null, 12, 12));
    const adv_link = $('<div class="text-center card-hover col-12 mb-3"><a href="#">[ advanced options ]</a></div>').appendTo(row_content);
    adv_link.off('click').on('click', (e) => {row_content.find('.adv').toggle();});
    // 高度なフィルター条件のフォームを表示
    const adv_conditions = ['select', 'filter_clmsg_body', 'filter_clmsg_sdate', 'filter_svmsg_edate',
                            'filter_svmsg_id', 'sort', 'offset', 'limit'];
    const adv_row_content = $('<div class="row_content"></div>').appendTo(row_content);
    py_get_cmd_choices.filter(row => adv_conditions.includes(row.opt)).forEach((row, i) => cmdbox.add_form_func(i, form, adv_row_content, row, null, 12, 12));
    adv_row_content.children().each((i, elem) => {$(elem).addClass('adv').hide();}).appendTo(row_content);
    adv_row_content.remove();
    let condition = await cmdbox.load_user_data('audit', 'condition');
    condition = condition && condition['success'] ? JSON.parse(condition['success']) : {};
    Object.keys(condition).forEach((id) => {
        const data = condition[id];
        if (!data) return;
        let elem = row_content.find(`#${id}`);
        if (elem.length > 0) {
            elem.val(data['value']);
            return;
        }
        const last_elem = row_content.find(`[name="${data['name']}"]:last`);
        const add_btn = last_elem.next('.add_buton');
        if (add_btn.length <= 0) return;
        add_btn.click();
        elem = row_content.find(`[name="${data['name']}"]:last`);
        elem.val(val);
    });
    row_content.find(':input').each((i, elem) => {
        const id = $(elem).attr('id');
        if (!id || id == '') return;
        const val = localStorage.getItem(id);
        if (!val || val == '') return
        $(elem).val(val);
    });
};
audit.list_audit_metrics = async () => {
    const formData = new FormData();
    const res = await fetch('audit/metrics/list', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
audit.load_audit_metrics = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('audit/metrics/load', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
audit.save_audit_metrics = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('audit/metrics/save', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
};
const del_audit_metrics = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('audit/metrics/delete', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
$(() => {
    // カラーモード対応
    cmdbox.change_color_mode();
    // アイコンを表示
    cmdbox.set_logoicon('.navbar-brand');
    // copyright表示
    cmdbox.copyright();
    // バージョン情報モーダル初期化
    cmdbox.init_version_modal();
    // モーダルボタン初期化
    cmdbox.init_modal_button();
    // コマンド実行用のオプション取得
    cmdbox.get_server_opt(true, $('.filer_form')).then(async (opt) => {
        // フィルターフォーム初期化
        await audit.init_form();
        // 監査ログ一覧表示
        await audit.rawlog();
        // メトリクス表示
        $('#add_metrics').off('click').on('click', (e) => {
            audit.metrics_modal_func();
        });
        await audit.metrics();
    });
    // スプリッター初期化
    $('.split-pane').splitPane();
});
