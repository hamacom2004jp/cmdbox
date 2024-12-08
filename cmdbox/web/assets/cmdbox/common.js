const cmdbox = {}
/**
 * ダークモード切替
 * @param {bool} dark_mode 
 */
cmdbox.change_dark_mode = (dark_mode) => {
  const html = $('html');
  if(dark_mode) html.attr('data-bs-theme','dark');
  else if(html.attr('data-bs-theme')=='dark') html.removeAttr('data-bs-theme');
  else html.attr('data-bs-theme','dark');
  $('body').css('background-color', '');
};
/**
 * ローディング表示
 */
cmdbox.show_loading = () => {
  const elem = $('#loading');
  elem.removeClass('d-none');
};
/**
 * ローディング非表示
 */
cmdbox.hide_loading = () => {
  const elem = $('#loading');
  elem.addClass('d-none');
  const progress = $('#progress');
  progress.addClass('d-none');
};
/**
 * テキストデータかどうか判定
 * @param {number[]} array - バイト配列
 * @returns {bool} - テキストデータかどうか
 */
cmdbox.is_text = (array) => {
  const textChars = [7, 8, 9, 10, 12, 13, 27, ...cmdbox.range(0x20, 0xff, 1)];
  return array.every(e => textChars.includes(e));
};
/**
 * Dateオブジェクトを日付文字列に変換
 * @param {Date} date - Dateオブジェクト
 * @returns {string} - 日付文字列
 */
cmdbox.toDateStr = (date) => {
  return date.toLocaleDateString('ja-JP', {
    year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'
  });
};
/**
 * 指定された範囲の数値の配列を生成する
 * @param {number} start - 開始値
 * @param {number} stop - 終了値
 * @param {number} step - ステップ数
 * @returns {number[]} - 生成された数値の配列
 */
cmdbox.range = (start, stop, step) => {
  return Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);
};
/**
 * アラートメッセージ表示
 * @param {object} res - レスポンス
 */
cmdbox.message = (res) => {
  msg = JSON.stringify(res)
  alert(msg.replace(/\\n/g, '\n'));
  cmdbox.hide_loading();
};
/**
 * コピーライト表示
 */
cmdbox.copyright = async () => {
  const res = await fetch('copyright', {method: 'GET'});
  if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
  $('.copyright').text(await res.text());
};
/**
 * appid表示
 * @param {string} sel - セレクタ
 */
cmdbox.appid = async (sel) => {
  const res = await fetch('gui/appid', {method: 'GET'});
  if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
  const appid = await res.text()
  $(sel).text(appid);
  const head = $('head');
  head.append(`<title>${appid}</title>`);
  head.append(`<link rel="icon" type="image/x-icon" href="assets/${appid}/favicon.ico">`);
};
/**
 * サインアウト
 * @param {string} sitepath - サイトパス
 **/
cmdbox.singout = (sitepath) => {
  if (confirm('Sign out ok ?')) {
    const rand = cmdbox.randam_string(8);
    location.href = `dosignout/${sitepath}?r=${rand}`;
  }
};
$(()=>{
  // サインアウトメニューを表示
  fetch('usesignout', {method: 'GET'}).then(async res => {
    try {
      if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
      const json = await res.json();
      const usesignout = json['success']['usesignout'];
      if (!usesignout) return;
      const user = await cmdbox.user_info();
      if (!user) return;
      const user_info_menu = $('.user_info');
      user_info_menu.removeClass('d-none').addClass('d-flex');
      if (!user_info_menu.find('.dropdown-menu .signout-menu-item').length) {
        const parts = location.pathname.split('/');
        const sitepath = parts[parts.length-1];
        const signout_item = $(`<li><a class="dropdown-item signout-menu-item" href="#" onclick="cmdbox.singout('${sitepath}');">Sign out</a></li>`);
        user_info_menu.find('.dropdown-menu').append(signout_item);
      }
      user_info_menu.find('.user_info_note').html(`Groups: ${user['groups'].join(', ')}`);
      user_info_menu.find('.username').text(user['name']);
    } catch (e) {}
  });
  cmdbox.appid('.navbar-brand');
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});
/**
 * バージョンモーダルを初期化
 */
cmdbox.init_version_modal = () => {
  $('#versions_modal').on('shown.bs.modal', async () => {
    // cmdboxのバージョン情報取得
    const versions_func = async (tabid, title, icon, url) => {
      const tab = $(`<li class="nav-item" role="presentation">`)
      const btn = $(`<button class="nav-link" id="${tabid}-tab" data-bs-toggle="tab" data-bs-target="#${tabid}" type="button" role="tab" aria-controls="${tabid}" aria-selected="true"/>`);
      if (icon) btn.append(`<span><img class="me-2" src="${icon}" width="32" height="32"/>${title}</span>`);
      else {
        btn.addClass('mt-2');
        btn.html(title);
      }
      tab.append(btn);
      $('.version-tabs').prepend(tab);
      if (!url) return;
      const tabcont = $(`<div class="tab-pane fade show" id="${tabid}" role="tabpanel" aria-labelledby="${tabid}-tab"/>`)
      $('.version-content').prepend(tabcont);
      const res = await fetch(url, {method: 'GET'});
      if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
      const vi = await res.json();
      vi.forEach((v, i) => {
        v = v.replace(/<([^>]+)>/g, '<a href="$1" target="_blank">$1</a>');
        const div = $('<div></div>');
        tabcont.append(div);
        if(i==0) {
          div.addClass('d-flex');
          div.addClass('m-3');
          div.append(`<h4><pre class="m-0">${v}</pre></h4>`);
        } else if(i==1) {
          div.addClass('m-3');
          div.append(`<h4>${v}</h4>`);
        } else {
          div.addClass('ms-5 me-5');
          div.append(`<h6>${v}</h6>`);
        }
      });
      $('.version-tabs').find('.nav-link').removeClass('active');
      $('.version-content').children().removeClass('active');
      $('.version-tabs').find('.nav-link').first().addClass('active');
      $('.version-content').children().first().addClass('active');
    }
    $('.version-tabs').html('');
    $('.version-content').html('<div class="tab-pane fade" id="versions_used" role="tabpanel" aria-labelledby="versions_used-tab">versions_used</div>');
    await versions_func('versions_used', 'Used software', null, null);
    const res = await fetch('gui/version_info', {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const verinfos = await res.json();
    for (const v of verinfos) {
      await versions_func(v['tabid'], v['title'], v['icon'], v['url']);
    }
    // usedのバージョン情報取得
    const versions_used_func = async () => {
      const res = await fetch('versions_used', {method: 'GET'});
      if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
      const vu =  await res.json();
      $('#versions_used').html('');
      const div = $('<div class="overflow-auto" style="height:calc(100vh - 260px);"></div>');
      const table = $('<table class="table table-bordered table-hover table-sm"></table>');
      const table_head = $('<thead class="table-dark bg-dark"></thead>');
      const table_body = $('<tbody></tbody>');
      table.append(table_head);
      table.append(table_body);
      div.append(table);
      $('#versions_used').append(div);
      vu.forEach((row, i) => {
        const tr = $('<tr></tr>');
        row.forEach((cel, j) => {
            const td = $('<td></td>').text(cel);
            tr.append(td);
        });
        if(i==0) table_head.append(tr);
        else table_body.append(tr);
      });
    };
    versions_used_func();
  });
};
/**
 * モーダルボタン初期化
 */
cmdbox.init_modal_button = () => {
  // modal setting
  $('.modal-dialog').draggable({cursor:'move',cancel:'.modal-body'});
  $('#filer_modal .modal-dialog').draggable({cursor:'move',cancel:'.modal-body, .filer_address'});
  $('.btn_window_stack').off('click').on('click', () => {
    $('.btn_window_stack').css('margin-left', '0px').hide();
    $('.btn_window').css('margin-left', 'auto').show();
    $('.btn_window_stack').parents('.modal-dialog').removeClass('modal-fullscreen');
  });
  $('.btn_window').off('click').on('click', () => {
    $('.btn_window_stack').css('margin-left', 'auto').show();
    $('.btn_window').css('margin-left', '0px').hide();
    $('.btn_window_stack').parents('.modal-dialog').addClass('modal-fullscreen');
  });
  $('.btn_window_stack').css('margin-left', '0px').hide();
  $('.btn_window').css('margin-left', 'auto').show();
  $('.bbforce').off('click').on('click', async () => {
    await bbforce_cmd();
    cmdbox.hide_loading();
  });
  // F5 and Ctrl+R 無効化
  $(document).on('keydown', (e) => {
    if ((e.which || e.keyCode) == 116) {
      return false;
    } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
      return false;
    }
  });
};
/**
 * ファイルサイズ表記を取得する
 * @param {number} size - ファイルサイズ
 * @returns {string} - ファイルサイズ表記
 */
cmdbox.calc_size = (size) => {
  const kb = 1024
  const mb = Math.pow(kb, 2)
  const gb = Math.pow(kb, 3)
  const tb = Math.pow(kb, 4)
  let target = null
  let unit = 'B'
  if (size >= tb) {
    target = tb
    unit = 'TB'
  } else if (size >= gb) {
    target = gb
    unit = 'GB'
  } else if (size >= mb) {
    target = mb
    unit = 'MB'
  } else if (size >= kb) {
    target = kb
    unit = 'KB'
  }
  const res = target !== null ? Math.floor((size / target) * 100) / 100 : size
  return `${res} ${unit}`
};
/**
 * カラーコードを取得する
 * @param {bool} color - カラーを指定。省略するとランダムなカラーコードを生成
 * @returns {string, array} - カラーコード
 **/
cmdbox.randam_color = (color=undefined) => {
  if (!color) {
    color = [(~~(256 * Math.random())), (~~(256 * Math.random())), (~~(256 * Math.random()))];
  } else if (typeof color === 'string') {
    color = color.split(',').map(e => parseInt(e, 16));
  }
  code = color.map(e => ("00"+e.toString(16)).slice(-2)).join('');
  return code;
};
/**
 * カラーコードを取得する
 * @param {number} id - ラベルID
 * @returns {string} - カラーコード
 **/
cmdbox.make_color4id = (id=0) => {
  color = [(~~(256*(id/(256**3)))), (~~(256*(id/(256**2)))), (~~(256*(id/(256**1))))];
  code = color.map(e => ("00"+e.toString(16)).slice(-2)).join('');
  return code;
};
/**
 * ランダムな文字列を生成する
 * @param {number} length - 文字列の長さ
 * @returns {string} - ランダムな文字列
 **/
cmdbox.randam_string = (length) => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  return Array.from({length: length}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
};
/**
 * ファイル名から拡張子を取り除いた文字列を取得する
 * @param {string} filename - ファイル名
 * @returns {string} - 拡張子を取り除いた文字列
 **/
cmdbox.chopext = (filename) => {
  return filename.replace(/\.[^/.]+$/, "");
};
/**
 * Imageオブジェクトを使用して画像を読み込むPromiseを生成する
 * @param {string} url - 画像のURL
 * @returns {Promise} - 画像の読み込みPromise
 **/
cmdbox.load_img_sync = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image's URL: ${url}`));
    img.src = url;
  });
};
/**
 * サーバーAPI実行
 * @param {object} opt - オプション
 * @returns {Promise} - レスポンス
 */
cmdbox.sv_exec_cmd = async (opt) => {
  return fetch('exec_cmd', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(opt)
  }).then(response => response.json()).catch((e) => {
    console.log(e);
  });
};
/**
 * 接続情報取得
 * @param {bool} do_sv_exec_cmd - cmdbox.sv_exec_cmdを使用してserverモードのlistコマンドを実行する場合はtrue
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @returns {object | Promise} - 接続情報又はPromise
 */
cmdbox.get_server_opt = (do_sv_exec_cmd, parent_elem) => {
  if (do_sv_exec_cmd) {
    const prom = fetch('get_server_opt', {method: 'GET'}).then(res => res.json()).then(opt => {
        cmdbox.initargs = opt;
        parent_elem.find('.filer_host').val(opt['host']);
        parent_elem.find('.filer_port').val(opt['port']);
        parent_elem.find('.filer_password').val(opt['password']);
        parent_elem.find('.filer_svname').val(opt['svname']);
        parent_elem.find('.filer_client_data').val("client");
        parent_elem.find('.filer_client_data').val(opt['data']);
    });
    return prom;
  }
  try {
    const filer_host = parent_elem.find('.filer_host').val();
    const filer_port = parent_elem.find('.filer_port').val();
    const filer_password = parent_elem.find('.filer_password').val();
    const filer_svname = parent_elem.find('.filer_svname').val();
    const filer_scope = parent_elem.find('.filer_scope').val();
    const filer_client_data = parent_elem.find('.filer_client_data').val();
    return {"host":filer_host, "port":filer_port, "password":filer_password, "svname":filer_svname, "scope": filer_scope, "client_data": filer_client_data};
  } catch (e) {
    console.log(e);
    return {};
  }
};
/**
 * サーバーリスト取得
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @param {function} call_back_func - サーバーリストを選択した時のコールバック関数
 * @param {bool} server_only - サーバーのみ表示
 * @param {bool} current_only - カレントのみ表示
 */
cmdbox.load_server_list = (parent_elem, call_back_func, server_only, current_only) => {
  cmdbox.show_loading();
  parent_elem.find('.filer_svnames').remove();
  const mk_func = (elem) => {return ()=>{
    parent_elem.find('.filer_server_bot').text(elem.attr('data-svname'));
    parent_elem.find('.filer_host').val(elem.attr('data-host'));
    parent_elem.find('.filer_port').val(elem.attr('data-port'));
    parent_elem.find('.filer_password').val(elem.attr('data-password'));
    parent_elem.find('.filer_svname').val(elem.attr('data-svname'));
    parent_elem.find('.filer_scope').val(elem.attr('data-scope'));
    parent_elem.find('.filer_client_data').val(elem.attr('data-client_data'));
    if (call_back_func) call_back_func(cmdbox.get_server_opt(false, parent_elem));
    //fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
  }};
  if (!cmdbox.initargs['client_only'] && !current_only) {
    const opt = cmdbox.get_server_opt(false, parent_elem);
    opt['mode'] = 'server';
    opt['cmd'] = 'list';
    opt["capture_stdout"] = true;
    delete opt['svname'];
    cmdbox.sv_exec_cmd(opt).then(res => {
      if(!res[0] || !res[0]['success']) {
        cmdbox.message(res);
        return;
      }
      if(res.length<=0 || !res[0]['success']) {
        cmdbox.hide_loading();
        return;
      }
      const svnames = {};
      res[0]['success'].forEach(elem => {
        const svname = elem['svname'].split('-')[0];
        if (svnames[svname]) return;
        svnames[svname] = true;
        const a_elem = $(`<a class="dropdown-item" href="#" data-client_data="">${svname} ( ${opt['host']}:${opt['port']} )</a>`);
        a_elem.attr('data-host', opt['host']);
        a_elem.attr('data-port', opt['port']);
        a_elem.attr('data-password', opt['password']);
        a_elem.attr('data-svname', svname);
        a_elem.attr('data-scope', "server");
        a_elem.off("click").on("click", mk_func(a_elem));
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        parent_elem.find('.filer_server').append(li_elem);
      });
      parent_elem.find('.filer_server').find('.dropdown-item:first').click();
    }).catch((e) => {
      console.log(e);
    }).finally(() => {
      cmdbox.hide_loading();
    });
  }
  const cl = (label, local_dir) => {
    const a_elem = $(`<a class="dropdown-item" href="#">${label}</a>`);
    a_elem.attr('data-host', cmdbox.initargs['host']);
    a_elem.attr('data-port', cmdbox.initargs['port']);
    a_elem.attr('data-password', cmdbox.initargs['password']);
    a_elem.attr('data-svname', label);
    a_elem.attr('data-scope', label);
    a_elem.attr('data-client_data', local_dir);
    a_elem.off("click").on("click", (event) => {
      parent_elem.find('.filer_address').val(current_only ? '.' : '/');
      mk_func($(event.target))();
    });
    const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
    parent_elem.find('.filer_server').append(li_elem);
  }
  if (current_only) cl('current', '.');
  else if (!server_only) {
    cl('client', cmdbox.initargs['data']);
    cl('current', '.');
  }
  parent_elem.find('.filer_server').find('.dropdown-item:first').click();
};
/**
 * deployリスト取得
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {function} error_func - エラー時のコールバック関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.deploy_list = (target, error_func=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'deploy_list';
  opt['capture_stdout'] = true;
  cmdbox.show_loading();
  return cmdbox.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    if (!res[0]['success']['data']) {
      cmdbox.hide_loading();
      return
    }
    return res[0]['success'];
  });
};
/**
 * 現在のユーザー情報取得
 * @returns {Promise} - レスポンス
 */
cmdbox.user_info = async () => {
  const res = await fetch('gui/user_info', {method: 'GET'});
  if (!res.ok) return null;
  const user = await res.json()
  return user;
};
/**
 * ファイルリスト取得
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {bool} recursive - 再帰的に取得するかどうか
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_list = (target, svpath, recursive=false, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_list';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  opt['recursive'] = recursive ? true : false;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * ファイルダウンロード
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_download = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_download';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  opt['capture_maxsize'] = 1024**3*10;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success'] || !res[0]['success']['data']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  }).catch((e) => {
    console.log(e);
  });
};
/**
 * ファイルアップロード
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {FormData} formData - ファイルデータ
 * @param {bool} orverwrite - 上書きするかどうか
 * @param {function} progress_func - 進捗状況を表示する関数。呼出時の引数はe(イベントオブジェクト)のみ
 * @param {function} success_func - 成功時のコールバック関数。呼出時の引数はtarget, svpath, data
 * @param {function} error_func - エラー時のコールバック関数。呼出時の引数はtarget, svpath, data
 * @param {bool} async_fg - 非同期で実行するかどうか
 */
cmdbox.file_upload = (target, svpath, formData, orverwrite=false, progress_func=undefined, success_func=undefined, error_func=undefined, async_fg=true) => {
  const param = {method: 'POST', body: formData};
  const opt = cmdbox.get_server_opt(false, target);
  let param_str = `host=${encodeURI(opt['host'])}`;
  param_str += `&port=${encodeURI(opt['port'])}`;
  param_str += `&password=${encodeURI(opt['password'])}`;
  param_str += `&svname=${encodeURI(opt['svname'])}`;
  param_str += `&orverwrite=${!!orverwrite}`;
  param_str += `&svpath=${encodeURI(svpath)}`;
  param_str += `&scope=${encodeURI(opt['scope'])}`;
  param_str += `&client_data=${encodeURI(opt['client_data'])}`;
  $.ajax({ // fetchだとxhr.upload.onprogressが使えないため、$.ajaxを使用
    url: `filer/upload?${param_str}`,
    type: 'POST',
    processData: false,
    contentType: false,
    async: async_fg,
    data: formData,
    xhr: function() {
      const xhr = $.ajaxSettings.xhr();
      xhr.upload.onprogress = function(e) {
        if (e.lengthComputable && progress_func) {
          progress_func(e);
        }
      };
      return xhr;
    },
    success: function(data) {
      if (success_func) {
        success_func(target, svpath, data);
      }
    },
    error: function(data) {
      console.log(data);
      cmdbox.message(data);
      if (error_func) {
        error_func(target, svpath, data);
      }
    }
  });
}
/**
 * ファイルコピ－
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} from_path - コピー元パス
 * @param {string} to_path - コピー先パス
 * @param {bool} orverwrite - 上書きするかどうか
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 */
cmdbox.file_copy = (target, from_path, to_path, orverwrite=false, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_copy';
  opt['capture_stdout'] = true;
  opt['from_path'] = from_path;
  opt['to_path'] = to_path;
  opt['orverwrite'] = orverwrite;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * ファイル移動
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} from_path - 移動元パス
 * @param {string} to_path - 移動先パス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 */
cmdbox.file_move = (target, from_path, to_path, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_move';
  opt['capture_stdout'] = true;
  opt['from_path'] = from_path;
  opt['to_path'] = to_path;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * ファイル削除
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_remove = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_remove';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * ディレクトリ削除
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_rmdir = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_rmdir';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * ディレクトリ作成
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_mkdir = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
  const opt = cmdbox.get_server_opt(false, target);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_mkdir';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  cmdbox.show_loading();
  const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
  return exec(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      if (error_func) {
        error_func(res);
        return;
      }
      cmdbox.hide_loading();
      cmdbox.message(res);
      return;
    }
    return res[0]['success'];
  });
};
/**
 * プログレスバー表示
 * @param {number} _min - 最小値
 * @param {number} _max - 最大値
 * @param {number} _now - 現在値
 * @param {string} _text - テキスト
 * @param {bool} _show - 表示するかどうか
 * @param {bool} _cycle - サイクル表示するかどうか
 */
cmdbox.progress = (_min, _max, _now, _text, _show, _cycle) => {
  const prog_elem = $('.progress');
  const bar_elem = prog_elem.find('.progress-bar');
  const bar_text = bar_elem.find('.progress-bar-text');
  if(_show) prog_elem.removeClass('d-none');
  else prog_elem.addClass('d-none');
  prog_elem.attr('aria-valuemin', _min);
  prog_elem.attr('aria-valuemax', _max);
  prog_elem.attr('aria-valuenow', _now);
  if (!_cycle) {
    const par = Math.floor((_now / (_max-_min)) * 10000) / 100
    bar_elem.css('left', 'auto').css('width', `${par}%`);
    bar_text.text(`${par.toFixed(2)}% ( ${_now} / ${_max} ) ${_text}`);
    if (cmdbox.progress_handle) clearTimeout(cmdbox.progress_handle);
  } else {
    let maxwidth = prog_elem.css('width');
    maxwidth = parseInt(maxwidth.replace('px', ''));
    let left = bar_elem.css('left');
    if (!left || left=='auto') left = 0;
    else left = parseInt(left.replace('px', ''));
    if (left > maxwidth) left = -200;
    left += 2;
    bar_elem.css('width', '200px').css('position', 'relative').css('left', `${left}px`);
    bar_text.text(_text?_text:'Server processing...');
    cmdbox.progress_handle = setTimeout(() => {
      if (!$('#loading').is('.d-none')) cmdbox.progress(_min, _max, _now, _text, _show, _cycle);
    }, 20);
  }
};