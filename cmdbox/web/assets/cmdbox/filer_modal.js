// ファイラーモーダル
const fmodal = {};
fmodal.left = $('#filer_modal');
fmodal.filer_modal_func = async (target_id, modal_title, current_path, select_dir, is_current, call_back_func) => {
    const filer_modal = $('#filer_modal');
    filer_modal.find('.modal-title').text(modal_title);
    filer_modal.find('.modal-body').html('<ul class="tree-menu overflow-auto border col-4"></ul><div class="file-list overflow-auto col-8"></div>');
    filer_modal.find('.tree-menu').css('height', 'calc(100vh - 180px)');
    filer_modal.find('.file-list').css('height', 'calc(100vh - 180px)');
    //filer_modal.find('.tree-menu').resizable({ghost:true});
    filer_modal.find('.filer_address_bot').off('click').on('click', async () => {
        const c_path = filer_modal.find('.filer_address').val();
        if (!c_path) return;
        const key = c_path.replace(/[\s\:\\\/\,\.\#\$\%\^\&\!\@\*\(\)\{\}\[\]\'\"\`]/g, `_`);
        const current_node = $(`#${key}`);
        /*if (current_node.length <= 0) {
            alert(`invalid path:${c_path}`);
            return;
        }*/
        await reload_tree(target_id, filer_modal.find('.tree-menu'), c_path, filer_modal.find('.file-list'));
    });

    const reload_tree = async (target_id, current_node, current_path, file_list_elem, is_current) => {
        const py_list_tree = await fmodal.list_tree_server(current_path);
        current_node.html('');
        Object.entries(py_list_tree).forEach(([key, node]) => {
            if(!node['is_dir']) return;
            let li_elem = $(`#${key}`);
            const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
            if (li_elem.length > 0) {
                li_elem.html(`<a href="#" class="folder-open" style="${font_color}">${node['name']}</a>`);
            } else {
                li_elem = $(`<li id="${key}"><a href="#" class="folder-open" style="${font_color}">${node['name']}</a></li>`);
                current_node.append(li_elem);
            }
            const mk_func = (target_id, current_node, current_path) => {
                // 左側ペインのフォルダを選択した時の処理
                return () => reload_tree(target_id, current_node, current_path, file_list_elem, is_current);
            }
            li_elem.find('a').off('click').on('click', mk_func(target_id, current_node, node['path']));
            if(node['children']) {
                const ul_elem = $('<ul/>');
                li_elem.append(ul_elem);
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(!n['is_dir']) return;
                    const li = $(`<li id="${k}"><a href="#" class="folder-close" style="${font_color}">${n['name']}</a></li>`);
                    li.find('a').click(mk_func(target_id, ul_elem, n['path']));
                    ul_elem.append(li);
                });
            }
        });
        const py_list_tree_keys = Object.keys(py_list_tree);
        if (py_list_tree_keys.length > 0) {
            getdir = (list_tree, keys) => {
                for (const n of Object.values(list_tree).toReversed()) {
                    if (n['is_dir']) return n;
                }
                return list_tree[keys[0]];
            };
            const node = getdir(py_list_tree, py_list_tree_keys);
            const table = $('<table class="table table-bordered table-hover table-sm"></table>');
            filer_modal.find('.file-list').html('');
            filer_modal.find('.file-list').append(table);
            const table_head = $('<thead></thead>');
            table_head.append($('<tr><th class="th" scope="col">-</th><th class="th" scope="col">name</th><th class="th" scope="col">size</th><th class="th" scope="col">last</th></tr>'));
            table.append(table_head);
            const table_body = $('<tbody></tbody>');
            table.append(table_body);
            filer_modal.find('.filer_address').val(node['path']);
            if(node['children']) {
                const mk_dir_func = (target_id, current_node, current_path) => {
                    if (select_dir) {
                        // 右側ペインのフォルダを選択した時の処理
                        return () => {
                            $(`[id="${target_id}"]`).val(current_path);
                            filer_modal.modal('hide');
                            if(call_back_func) call_back_func(current_path, cmdbox.get_server_opt(false, fmodal.left));
                        }
                    }
                    // 右側ペインのフォルダを選択した時の処理
                    return () => reload_tree(target_id, current_node, current_path, file_list_elem, is_current);
                }
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(!n['is_dir']) return;
                    const tr_elem = $('<tr/>');
                    table_body.append(tr_elem);
                    const td = $(`<td><a href="#" class="folder-close">${n['name']}</a></td>`);
                    td.find('a').click(mk_dir_func(target_id, $(`#${k}`), n['path']));
                    tr_elem.append($('<td><img src="assets/tree-menu/image/folder-close.png"></td>'));
                    tr_elem.append(td);
                    tr_elem.append($(`<td>${n['size']}</td>`));
                    tr_elem.append($(`<td>${n['last']}</td>`));
                });
                const mk_file_func = (target_id, current_node, current_path) => {
                    // 右側ペインのファイルを選択した時の処理
                    return () => {
                        $(`[id="${target_id}"]`).val(current_path);
                        filer_modal.modal('hide');
                        if(call_back_func) call_back_func(current_path, cmdbox.get_server_opt(false, fmodal.left));
                    }
                }
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(n['is_dir']) return;
                    const tr_elem = $('<tr/>');
                    table_body.append(tr_elem);
                    tr_elem.append($('<td><img src="assets/tree-menu/image/file.png"></td>'));
                    if (!select_dir) {
                        const td = $(`<td><a href="#" class="folder-close">${n['name']}</a></td>`);
                        td.find('a').click(mk_file_func(target_id, $(`#${k}`), n['path']));
                        tr_elem.append(td);
                    } else {
                        const td = $(`<td>${n['name']}</td>`);
                        tr_elem.append(td);
                    }
                    tr_elem.append($(`<td>${n['size']}</td>`));
                    tr_elem.append($(`<td>${n['last']}</td>`));
                });
            }
        }
        cmdbox.hide_loading();
    }
    /*try {
        fsapi.tree = (target, svpath, current_ul_elem, is_local) => {
            reload_tree(target_id, filer_modal.find('.tree-menu'), current_path, filer_modal.find('.file-list'), is_current);
        };
    } catch (e) {}*/
    filer_modal.modal('show');
    cmdbox.get_server_opt(true, fmodal.left).then(() => {
        cmdbox.load_server_list(fmodal.left, (opt) => {
            if (is_current) {
                filer_modal.find('.filer_server_bot').attr('disabled', true).removeClass('dropdown-toggle');
                current_path = current_path ? current_path : '.';
            }
            reload_tree(target_id, filer_modal.find('.tree-menu'), current_path, filer_modal.find('.file-list'), is_current);
        }, false, is_current);
    });
};
fmodal.list_tree_server = async (current_path) => {
    try {
        const opt = cmdbox.get_server_opt(false, fmodal.left);
        opt['mode'] = 'client';
        opt['cmd'] = 'file_list';
        opt['capture_stdout'] = true;
        opt['svpath'] = current_path;
        const res = await cmdbox.sv_exec_cmd(opt);
        if(!res[0] || !res[0]['success']) {
            cmdbox.message(res);
            return {};
        }
        const data = Object.entries(res[0]['success']).sort();
        const ret = {};
        for (let i = 0; i < data.length; i++) {
            const [key, value] = data[i];
            if (!value['name']) continue;
            ret[key] = value;
        }
        return ret;
    } catch (e) {
        return {};
    }
}
