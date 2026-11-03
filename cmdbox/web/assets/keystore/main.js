const keystore_page = {
    currentType: 'apikey',
    rows: []
};

/**
 * datetime文字列から datetime-local input 用の文字列に変換
 */
keystore_page.to_dt_local = (s) => {
    if (!s) return '';
    // "2024-01-01 00:00:00" または "2024-01-01_00:00:00" を "2024-01-01_00:00:00" に
    return s.replace(' ', 'T').replace('T', '_').substring(0, 19);
};

keystore_page.normalize_response = (res) => {
    const data_list = Array.isArray(res) ? res : [res];
    return data_list[0] || null;
};

keystore_page.get_add_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('keystore', 'add');
    const names = [
        'key_id', 'key_name', 'key_provider', 'key_type', 'key_usage','scope',
        'key_value', 'sign_key', 'sign_cert', 'key_pass', 'enc_key', 'ca_cert',
        'key_period_start', 'key_period_end', 'groups', 'owner', 'claims', 'description'
    ];
    return opts.filter(o => names.includes(o.opt));
};

keystore_page.build_add_form = async () => {
    const form = $('#keystore_form');
    form.empty();
    form.append('<input type="hidden" name="save_mode" value="add">');
    const defs = await keystore_page.get_add_form_def();
    const modal = $('#keystore_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, modal, form, row, null);
    });
    form.find('[name="key_type"]').val('apikey').trigger('change');
};

keystore_page.collect_form_data = () => {
    const form = $('#keystore_form');
    const data = { save_mode: 'add' };
    const dict_buf = {};

    form.find('input,select,textarea').each((i, elem) => {
        const e = $(elem);
        if (e.prop('disabled')) return;
        const name = e.attr('name');
        if (!name || name === 'save_mode') return;

        const typ = e.attr('param_data_type');
        const idx = parseInt(e.attr('param_data_index'));
        const multi = String(e.attr('param_data_multi')) === 'true';
        const val = e.val();

        if (typ === 'dict') {
            if (!data[name]) {
                data[name] = {};
                dict_buf[name] = {};
            }
            if (idx % 2 === 0) {
                dict_buf[name].key = val || '';
            } else if (dict_buf[name].key) {
                data[name][dict_buf[name].key] = val || '';
                delete dict_buf[name].key;
            }
            return;
        }

        if (typ === 'mlist') {
            if (Array.isArray(val) && val.length > 0) {
                data[name] = val.filter(v => v);
            }
            return;
        }

        if (!val) return;
        if (multi) {
            if (!Array.isArray(data[name])) data[name] = [];
            data[name].push(val);
        } else {
            data[name] = val;
        }
    });

    if (data.claims && Object.keys(data.claims).length === 0) {
        delete data.claims;
    }
    return data;
};

keystore_page.add = async () => {
    const data = keystore_page.collect_form_data();
    if (!data.key_name || !data.key_name.trim()) {
        cmdbox.message({ warn: 'key_name is required.' }, true, true);
        return;
    }
    if (!data.key_usage || (Array.isArray(data.key_usage) && data.key_usage.length === 0)) {
        cmdbox.message({ warn: 'key_usage is required.' }, true, true);
        return;
    }

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'keystore', cmd: 'add', ...data });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();

    const first = keystore_page.normalize_response(res);
    if (!first || !first.success) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first.success.msg || 'added', true, true);
    $('#keystore_modal').modal('hide');
    await keystore_page.load_list();
};

keystore_page.delete_row = async (row) => {
    if (!row || !row.key_id || !row.key_name) return;
    const ok = await cmdbox.confirm({ warn: `Delete key ${row.key_name} (${row.key_id}) ?` }, true);
    if (!ok) return;

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({
            mode: 'keystore',
            cmd: 'del',
            key_id: row.key_id,
            key_name: row.key_name
        });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();

    const first = keystore_page.normalize_response(res);
    if (!first || !first.success) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first.success.data || 'deleted', true, true);
    await keystore_page.load_list();
};

keystore_page.render_tabs = () => {
    const counts = { apikey: 0, signkey: 0, enckey: 0, cacert: 0 };
    keystore_page.rows.forEach(r => {
        const t = r.key_type || 'apikey';
        if (counts[t] == null) counts[t] = 0;
        counts[t] += 1;
    });

    $('#keystore_tabs .nav-link').each((i, a) => {
        const e = $(a);
        const t = e.data('ktype');
        e.text(`${t} (${counts[t] || 0})`);
        e.toggleClass('active', t === keystore_page.currentType);
    });
};

keystore_page.render_rows = () => {
    const area = $('#keystore_list').empty();
    const rows = keystore_page.rows.filter(r => (r.key_type || 'apikey') === keystore_page.currentType);
    if (rows.length === 0) {
        area.append('<div class="col-12 text-muted p-3 i18n">No keys found.</div>');
        cmdbox.process_i18n(area, true);
        return;
    }

    rows.forEach((r) => {
        const col = $('<div class="col-12 col-md-6 col-xl-4"></div>').appendTo(area);
        const card = $('<div class="card h-100 border-start border-4" style="border-left-color:var(--bs-info)!important;"></div>').appendTo(col);
        const hdr = $('<div class="doc-header d-flex align-items-center gap-2"></div>').appendTo(card);
        hdr.append(`<span class="badge rounded-pill text-bg-primary">${r.key_type || 'apikey'}</span>`);
        hdr.append(`<strong>${r.key_name || ''}</strong>`);
        hdr.append(`<span class="ms-auto text-body-secondary">${r.key_id || ''}</span>`);

        const body = $('<div class="card-body container p-2"></div>').appendTo(card);
        const row = $('<div class="row"></div>').appendTo(body);
        row.append(`<div class="col-6 small mb-1"><span class="text-secondary">provider:</span> ${r.key_provider || '-'}</div>`);
        row.append(`<div class="col-6 small mb-1"><span class="text-secondary">usage:</span> ${(r.key_usage || []).join(', ') || '-'}</div>`);
        if (Array.isArray(r.groups) && r.groups.length > 0) {
            row.append(`<div class="col-6 small mb-1"><span class="text-secondary">groups:</span> ${r.groups.join(', ')}</div>`);
        }
        if (Array.isArray(r.owner) && r.owner.length > 0) {
            row.append(`<div class="col-6 small mb-1"><span class="text-secondary">owner:</span> ${r.owner.join(', ')}</div>`);
        }
        row.append(`<div class="col-6 small mb-1"><span class="text-secondary">period:</span> ${r.key_period_start || '-'} ~ ${r.key_period_end || '-'}</div>`);
        row.append(`<div class="col-6 small mb-1"><span class="text-secondary">created_at:</span> ${keystore_page.to_dt_local(r.created_at) || '-'}</div>`);
        row.append(`<div class="col-12 small mb-1"><span class="text-secondary">description:</span><pre class="px-2 mb-0">${r.description || '-'}</pre></div>`);

        const btnRow = $('<div class="d-flex gap-2 mt-2"></div>').appendTo(body);
        const delBtn = $('<button type="button" class="btn btn-sm btn-outline-danger ms-auto i18n">Delete</button>').appendTo(btnRow);
        delBtn.on('click', () => keystore_page.delete_row(r));
    });
    cmdbox.process_i18n(area, true);
};

keystore_page.load_list = async () => {
    const kwd = ($('#kwd').val() || '').trim();
    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'keystore', cmd: 'list', kwd: kwd || null });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();

    const first = keystore_page.normalize_response(res);
    if (!first || !first.success || !Array.isArray(first.success.data)) {
        keystore_page.rows = [];
        keystore_page.render_tabs();
        keystore_page.render_rows();
        if (first && !first.success) cmdbox.message(res, true, true);
        return;
    }

    keystore_page.rows = first.success.data.map(r => ({ ...r, key_type: r.key_type || 'apikey' }));
    keystore_page.render_tabs();
    keystore_page.render_rows();
};

keystore_page.open_modal = async () => {
    await keystore_page.build_add_form();
    $('#keystore_modal').modal('show');
    cmdbox.process_i18n($('#keystore_modal'), true);
};

$(() => {
    cmdbox.copyright();
    cmdbox.init_version_modal();
    cmdbox.versions().then((versions) => {
        $('#appid_version').html(`${versions.title}-${versions.version}`);
    });

    cmdbox.init_modal_button();
    cmdbox.modal_draggable($('#keystore_modal'));

    $('#btn_refresh').on('click', () => keystore_page.load_list());
    $('#btn_search').on('click', () => keystore_page.load_list());
    $('#kwd').on('keypress', (ev) => {
        if (ev.which === 13) {
            ev.preventDefault();
            keystore_page.load_list();
        }
    });
    $('#btn_new').on('click', () => keystore_page.open_modal());
    $('#cmd_keystore_add').on('click', () => keystore_page.add());

    $('#keystore_tabs .nav-link').on('click', (ev) => {
        ev.preventDefault();
        keystore_page.currentType = $(ev.currentTarget).data('ktype');
        keystore_page.render_tabs();
        keystore_page.render_rows();
    });

    keystore_page.load_list().then(() => {
        setTimeout(() => { cmdbox.process_i18n(); }, 100);
    });
});
