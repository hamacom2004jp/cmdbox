const fsapi = {};
fsapi.left = $('#left_container');
fsapi.right = $('#right_container');
fsapi.filer = (svpath, is_local) => {
  // ファイルアップロード ========================================================
  const upload = async (event) => {
    cmdbox.show_loading();
    // https://qiita.com/KokiSakano/items/a122bc0a1a368c697643
    const files = [];
    const searchFile = async (entry) => {
      // ファイルのwebkitRelativePathにパスを登録する
      if (entry.isFile) {
        const file = await new Promise((resolve) => {
          entry.file((file) => {
            Object.defineProperty(file, "webkitRelativePath", {
              // fullPathは/から始まるので二文字目から抜き出す
              value: entry.fullPath.slice(1),
            });
            resolve(file);
          });
        });
        files.push(file);
        // ファイルが現れるまでこちらの分岐をループし続ける
      } else if (entry.isDirectory) {
        const dirReader = entry.createReader();
        let allEntries = [];
        const getEntries = () =>
          new Promise((resolve) => {
            dirReader.readEntries((entries) => {
              resolve(entries);
            });
          });
        // readEntriesは100件ずつの取得なので、再帰で0件になるまで取ってくるようにする
        // https://developer.mozilla.org/en-US/docs/Web/API/FileSystemDirectoryReader/readEntries
        const readAllEntries = async () => {
          const entries = await getEntries();
          if (entries.length > 0) {
            allEntries = [...allEntries, ...entries];
            await readAllEntries();
          }
        };
        await readAllEntries();
        for (const entry of allEntries) {
          await searchFile(entry);
        }
      }
    };
    const drop_path = event.originalEvent.dataTransfer.getData('path');
    const formData = new FormData();
    if (drop_path) {
      const relative = async (formData, entry, path) => {
        if (entry.kind === 'file') {
          const f = await entry.getFile();
          let p = path + '/' + entry.name;
          p = p.replace("\\","/").replace("//","/");
          formData.append('files', f, p);
        }
        else if (entry.kind === 'directory') {
          for await (const ent of entry.values()) {
            let p = path + '/' + entry.name;
            p = p.replace("\\","/").replace("//","/");
            await relative(formData, ent, p);
          }
        }
      };
      await relative(formData, fsapi.handles[drop_path], "/");
    } else {
      const items = event.originalEvent.dataTransfer.items;
      const calcFullPathPerItems = Array.from(items).map((item) => {
        return new Promise((resolve) => {
          const entry = item.webkitGetAsEntry();
          if (!entry) {
            resolve;
            return;
          }
          resolve(searchFile(entry));
        });
      });
      await Promise.all(calcFullPathPerItems);
      Object.keys(files).map((key) => {
        formData.append('files', files[key], files[key].webkitRelativePath);
      });
    }
    svpath = fsapi.right.find('.filer_address').val();
    // https://developer.mozilla.org/ja/docs/Web/API/fetch
    cmdbox.file_upload(fsapi.right, svpath, formData, orverwrite=false, progress_func=(e) => {
      cmdbox.progress(0, e.total, e.loaded, '', true, e.total==e.loaded);
    }, success_func=(target, svpath, data) => {
      if (data != "upload success") {
        cmdbox.message(data);
        return;
      }
      fsapi.tree(target, svpath, target.find('.tree-menu'), false);
    }, error_func=(target, svpath, data) => {
      fsapi.tree(target, svpath, target.find('.tree-menu'), false);
    });
  }
  // ファイルダウンロード ==============================================================
  const download = (event) => {
    if (!fsapi.left.find('.filer_address').val()) {
      cmdbox.message({warn: 'Please select a local directory before downloading.'});
      return;
    }
    cmdbox.show_loading();
    cmdbox.file_list(fsapi.right, event.originalEvent.dataTransfer.getData('path'), true).then((res) => {
      if(!res) {
        cmdbox.hide_loading();
        return;
      }
      delete res.performance;
      const file_list = Object.entries(res).sort();
      const get_list = (path) => {
        const list_downloads = [];
        for (let [key, node] of Object.entries(path['children'])) {
          if(node['is_dir']) {
            const nl = get_list(node);
            list_downloads.splice(list_downloads.length, 0, ...nl);
          } else {
            let rpath = node['path'].replace(fsapi.right.find('.filer_address').val(), '');
            rpath = rpath.startsWith('/') ? rpath.substring(1) : rpath;
            list_downloads.push({'svpath':node['path'],'rpath':rpath});
          }
        }
        return list_downloads;
      };
      const path = file_list.pop()
      const list_downloads = (!path[1] || !path[1]['children']) ? [] : get_list(path[1]);
      const jobs = [];
      fsapi.download_now = 0;
      cmdbox.progress(0, list_downloads.length, fsapi.download_now, '', true, false)
      const opt = cmdbox.get_server_opt(false, fsapi.right);
      list_downloads.forEach(async path => {
        opt['mode'] = 'client';
        opt['cmd'] = 'file_download';
        opt['capture_stdout'] = true;
        opt['svpath'] = path['svpath'];
        opt['rpath'] = path['rpath'];
        opt['capture_maxsize'] = 1024**3*10;
        //opt['svpath'] = event.originalEvent.dataTransfer.getData('path');
        jobs.push(cmdbox.sv_exec_cmd(opt).then(async res => {
          if(!res[0] || !res[0]['success']) {
            fsapi.download_now ++;
            cmdbox.progress(0, list_downloads.length, fsapi.download_now, '', true, false)
            cmdbox.message(res);
            return;
          }
          const mk_blob = (base64) => {
            const bin = atob(base64.replace(/^.*,/, ''));
            const buffer = new Uint8Array(bin.length);
            for (i=0; i<bin.length; i++) buffer[i] = bin.charCodeAt(i);
            const blob = new Blob([buffer.buffer], {type: 'application/octet-stream'});
            return blob;
          }
          const file_name = res[0]['success']['name'];
          const file_svpath = res[0]['success']['svpath'];
          const rpath = res[0]['success']['rpath'];
          let file_path = fsapi.left.find('.filer_address').val() + '/' + rpath;
          file_path = file_path.replaceAll("\\","/").replaceAll("//","/");
          cmdbox.progress(0, list_downloads.length, fsapi.download_now, file_path, true, false)
          const file_path_parts = file_path.split('/');
          let dh = fsapi.handles['/'];
          for (let i=0; i<file_path_parts.length-1; i++){
            const part = file_path_parts[i];
            if (!part) continue;
            try {
              dh = await dh.getDirectoryHandle(part, {create: true});
              fsapi.handles[file_path_parts.slice(0, i+1).join('/')] = dh;
            } catch (e) {
              continue;
            }
          }
          try {
            const dir_path = file_path_parts.slice(0, -1).join('/');
            const down_dir = fsapi.handles[dir_path?dir_path:"/"];
            const down_file = await down_dir.getFileHandle(file_name, {create: true});
            const writable = await down_file.createWritable();
            const blob = mk_blob(res[0]['success']['data']);
            await writable.write(blob);
            await writable.close();
          } catch (e) {
            console.log(e);
          }
          fsapi.download_now ++;
          cmdbox.progress(0, list_downloads.length, fsapi.download_now, file_path, true, false)
        }).catch((e) => {
          console.log(e);
        }));
      });
      Promise.all(jobs).then(() => {
        cmdbox.hide_loading();
        cmdbox.progress(0, list_downloads.length, fsapi.download_now, '', false, false)
        fsapi.download_now = 0;
        fsapi.tree(fsapi.left, fsapi.left.find('.filer_address').val(), fsapi.left.find('.tree-menu'), true);
      });
    });
  };
  // 表示 ==============================================================
  const target = is_local ? fsapi.left : fsapi.right;
  target.find('.filer_address').val(svpath);
  fsapi.right.find('.filer_address_bot').off('click').on('click', ()=>{
    fsapi.tree(fsapi.right, fsapi.right.find('.filer_address').val(), fsapi.right.find('.tree-menu'), false);
  })
  fsapi.right.find('.drop-area').off('dragover').on('dragover', (event) => {
    fsapi.right.find('.drop-area').addClass('dragover');
    event.preventDefault();
  });
  fsapi.right.find('.drop-area').off('dragleave').on('dragleave', (event) => {
    fsapi.right.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  fsapi.right.find('.drop-area').off('drop').on('drop', (event) => {
    if (fsapi.right.find('.drop-area').hasClass('dragover')) {
      fsapi.right.find('.drop-area').removeClass('dragover');
      const from = event.originalEvent.dataTransfer.getData('from');
      if (from=="local") {
          upload(event);
      }
    }
    event.preventDefault();
  });

  fsapi.left.find('.drop-area').off('dragover').on('dragover', (event) => {
    fsapi.left.find('.drop-area').addClass('dragover');
    event.preventDefault();
  });
  fsapi.left.find('.drop-area').off('dragleave').on('dragleave', (event) => {
    fsapi.left.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  fsapi.left.find('.drop-area').off('drop').on('drop', (event) => {
    if (fsapi.left.find('.drop-area').hasClass('dragover')) {
      fsapi.left.find('.drop-area').removeClass('dragover');
      const from = event.originalEvent.dataTransfer.getData('from');
      if (from=="server") {
        download(event);
      }
    }
    event.preventDefault();
  });

  if (is_local) {
    fsapi.tree(fsapi.left, "/", fsapi.left.find('.tree-menu'), true);
  } else {
    cmdbox.load_server_list(fsapi.right, (opt) => {
      fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
    }, false, false);
    //fsapi.load_server_list();
  }
  fsapi.left.find('.filer_local_bot').off('click').on('click', (event) => {
    fsapi.opendir();
  });
}
// ツリー表示 ================================================================
fsapi.tree = (target, svpath, current_ul_elem, is_local) => {
  cmdbox.show_loading();
  opt = cmdbox.get_server_opt(false, fsapi.right);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_list';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  let exec_cmd = is_local ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
  exec_cmd(opt).then(res => {
    current_ul_elem.html('');
    if (typeof opt == 'string') { // currentの場合
      res = [{"success": res}];
      if (opt.length == 1) { // ルートディレクトリの場合
        fsapi.treemem = res[0]['success']['_'];
      } else if (fsapi.treemem) {
        res[0]['success']['_'] = fsapi.treemem;
      }
    }
    if(!res[0] || !res[0]['success']) {
      cmdbox.message(res);
      target.find('.file-list').html('');
      return;
    }
    const list_tree = Object.entries(res[0]['success']).sort();
    cmdbox.hide_loading();
    // 上側ペイン
    list_tree.forEach(([key, node]) => {
      if(!node['is_dir']) return;
      const children = node['children'];
      let current_li_elem = target.find(`#${key}`);
      if (current_li_elem.length > 0) {
        current_li_elem.find('.folder-close').remove();
      } else {
        current_li_elem = $(`<li id="${key}" data_path="${node['path']}"/>`);
        current_ul_elem.append(current_li_elem);
      }
      const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
      const current_a_elem = $(`<a href="#" class="folder-open" style="${font_color}" draggable="false">${node['name']}</a>`);
      current_li_elem.append(current_a_elem);
      mk_func = (_t, _p, _e, _l) => {return ()=>{
        fsapi.tree(_t, _p, _e, _l);
        event.stopPropagation();
      }}
      current_a_elem.off('click').on('click', mk_func(target, node['path'], current_ul_elem, is_local));
      Object.keys(children).map((k, i) => {
        const n = children[k];
        if(!n['is_dir']) return;
        const ul_elem = $('<ul class="tree_ul"/>').append(`<li id="${k}" data_path="${n['path']}"><a href="#" class="folder-close" style="${font_color}" draggable="false">${n['name']}</a></li>`);
        current_li_elem.append(ul_elem);
        target.find(`#${k}`).off('click').on('click', mk_func(target, n['path'], current_ul_elem, is_local));
      });
    });
    // 下側ペイン
    list_tree.forEach(([key, node]) => {
      if(!node['path']) return;
      target.find('.filer_address').val(node['path']);
      const table = $('<table class="table table-bordered table-hover table-sm">'
                    + '<thead><tr><th scope="col">-</th><th scope="col">name</th><th scope="col">mime</th><th scope="col">size</th><th scope="col">last</th></tr></thead>'
                    + '</table>');
      const table_body = $('<tbody></tbody>');
      target.find('.file-list').html('');
      target.find('.file-list').append(table);
      table.append(table_body);
      const children = node['children'];
      if(children) {
        // ツリー表示関数の生成
        const mk_tree = (_t, _p, _e, _l) => {return ()=>fsapi.tree(_t, _p, _e, _l)}
        // 削除関数の生成
        const mk_delete = (_p, _e, is_dir, _l) => {return ()=>{
          if(confirm(`Do you want to delete "${_p}"？${is_dir?"\nNote: In the case of directories, the contents will also be deleted.":""}`)) {
            const remote = is_dir ? cmdbox.file_rmdir : cmdbox.file_remove;
            const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
            cmdbox.show_loading();
            remote(fsapi.right, _p, undefined, exec_cmd).then(res => {
              if(!res) return;
              cmdbox.hide_loading();
              fsapi.tree(target, res['path'], _e, _l);
            }).finally(() => {
              cmdbox.hide_loading();
            });
          }
        }};
        const mk_blob = (base64) => {
          const bin = atob(base64.replace(/^.*,/, ''));
          const buffer = new Uint8Array(bin.length);
          for (i=0; i<bin.length; i++) buffer[i] = bin.charCodeAt(i);
          const blob = new Blob([buffer.buffer], {type: 'application/octet-stream'});
          return blob;
        }
        // ダウンロード関数の生成
        const mk_download = (_p) => {return ()=>{
          cmdbox.file_download(fsapi.right, _p).then(res => {
            if(!res) {
              cmdbox.hide_loading();
              return;
            }
            const blob = mk_blob(res['data']);
            const link = target.find('.filer_download');
            link.attr('download', res['name']);
            link.get(0).href = window.URL.createObjectURL(blob);
            link.get(0).click();
            URL.revokeObjectURL(link.get(0).href);
          });
        }};
        // フォルダ作成関数の生成
        const mk_mkdir = (_t, _p, _e, is_dir, _l) => {return ()=>{
          _p = _p.substring(0, _p.lastIndexOf('/')+1);
          const prompt_text = prompt('Enter a new folder name.');
          if(prompt_text) {
            const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
            cmdbox.file_mkdir(fsapi.right, `${_p=="/"?"":_p}/${prompt_text}`.replace("//","/"), undefined, exec_cmd).then(res => {
              cmdbox.hide_loading();
              fsapi.tree(_t, res['path'], _e, _l);
            });
          }
        }};
        // コピー関数の生成
        const mk_copy = (_t, _p, _e, is_dir, _l) => {return ()=>{
          const prompt_text = prompt(`From: '${_p}'\nEnter a to path.`, `${_p}_copy`);
          if(prompt_text) {
            const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
            cmdbox.file_copy(fsapi.right, _p, prompt_text, false, undefined, exec_cmd).then(res => {
              cmdbox.hide_loading();
              if (res) fsapi.tree(_t, res['path'], _e, _l);
            });
          }
        }};
        // 移動関数の生成
        const mk_move = (_t, _p, _e, is_dir, _l) => {return ()=>{
          const prompt_text = prompt(`From: '${_p}'\nEnter a to path.`, `${_p}`);
          if(prompt_text) {
            const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
            cmdbox.file_move(fsapi.right, _p, prompt_text, undefined, exec_cmd).then(res => {
              cmdbox.hide_loading();
              if (res) fsapi.tree(_t, res['path'], _e, _l);
            });
          }
        }};
        // ビューアー関数の生成
        const mk_view = (_p, _mime, _size, _l) => {return ()=>{
          let bigfile = false;
          if (_size.indexOf('G') >= 0 || _size.indexOf('T') >= 0) {
            cmdbox.message({warn: `The file size is too large to view. (${_size})`});
            return;
          }
          else if (_size.indexOf('M') >= 0 && parseInt(_size.replace('M','')) > 5) {
            if (!window.confirm(`The file size is too large to view. (${_size} > 5M)\nDo you still want to open the Viewer?`)) {
              return;
            }
            bigfile = true;
          }
          const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
          cmdbox.file_download(fsapi.right, _p, undefined, exec_cmd).then(res => {
            if(!res) return;
            if (_l) {
              if (bigfile) cmdbox.message({warn: `Files that are too large may cause display errors in the viewer.`});
              fsapi.viewer(_p, res['data'], null, _mime);
            } else {
              const opt = cmdbox.get_server_opt(false, fsapi.right);
              const thum_size = "0";
              const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${encodeURIComponent(_p)}\t${opt['scope']}\t${thum_size}`);
              fsapi.viewer(_p, res['data'], `filer/download/${constr}?r=${cmdbox.randam_string(8)}`, _mime);
            }
          }).finally(() => {
            cmdbox.hide_loading();
          });
        }};
        // エディター関数の生成
        const mk_editer = (_p, _mime, _size, _l) => {return ()=>{
          if (_size.indexOf('G') >= 0 || _size.indexOf('T') >= 0) {
            cmdbox.message({warn: `The file size is too large to view. (${_size})`});
            return;
          }
          else if (_size.indexOf('M') >= 0 && parseInt(_size.replace('M','')) > 5) {
            if (!window.confirm(`The file size is too large to view. (${_size} > 5M)\nDo you still want to open the Viewer?`)) {
              return;
            }
          }
          const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
          cmdbox.file_download(fsapi.right, _p, undefined, exec_cmd).then(res => {
            if(!res) return;
            fsapi.editer(_p, res['data'], _mime, _l);
          }).finally(() => {
            cmdbox.hide_loading();
          });
        }};
        // ファイルリストの生成
        const mk_tr = (_t, _p, _e, _n, _l) => {
          const png = _n["is_dir"] ? 'folder-close.png' : 'file.png';
          const mime = _n['mime_type'] ? _n['mime_type'] : '-';
          const dt = _n["is_dir"] ? '-' : cmdbox.toDateStr(new Date(_n["last"]));
          const tr = $('<tr>'
              + `<td><img src="assets/tree-menu/image/${png}"></td>`
              + '<td>'
                + '<div class="droudown">'
                  + `<a class="dropdown-toggle" href="#">${_n['name']}</a>`
                  + '<ul class="dropdown-menu"/>'
                + '</div>'
              + '</td>'
              + `<td class="mime_type">${mime}</td>`
              + `<td class="file_size text-end">${cmdbox.calc_size(_n['size'])}</td>`
              + `<td class="text-end">${dt}</td>`
            + '</tr>');
          tr.find('.dropdown-toggle').on('dragstart', (event) => {
            event.originalEvent.dataTransfer.setData('path', _n['path']);
            event.originalEvent.dataTransfer.setData('from', _l?'local':'server');
          });
          if (_n["is_dir"]) {
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item open" href="#">Open</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
            if (!_l) {
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item copy" href="#">Copy Folder</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item move" href="#">Move Folder</a></li>');
            }
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
          } else {
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item view" href="#">View</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item edit" href="#">Edit</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
            if (!_l) {
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item copy" href="#">Copy</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item move" href="#">Move</a></li>');
            }
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
          }
          tr.find('.open').off('click').on('click', mk_tree(_t, _p, _e, _l));
          tr.find('.delete').off('click').on('click', mk_delete(_p, _e, _n["is_dir"], _l));
          tr.find('.mkdir').off('click').on('click', mk_mkdir(_t, _p, _e, _n["is_dir"], _l));
          tr.find('.copy').off('click').on('click', mk_copy(_t, _p, _e, _n["is_dir"], _l));
          tr.find('.move').off('click').on('click', mk_move(_t, _p, _e, _n["is_dir"], _l));
          tr.find('.view').off('click').on('click', mk_view(_p, tr.find('.mime_type').text(), tr.find('.file_size').text(), _l));
          tr.find('.edit').off('click').on('click', mk_editer(_p, tr.find('.mime_type').text(), tr.find('.file_size').text(), _l));
          tr.find('.droudown').off('contextmenu').on('contextmenu', (e) => {
            target.find('.dropdown-menu').hide();
            const fl = target.find('.file-list');
            //tr.find('.dropdown-menu').css('top', `calc(${e.pageY}px - ${fl.css('top')})`).css('left', `calc(${e.pageX}px - ${fl.css('left')})`).show();
            tr.find('.dropdown-menu').show();
            e.preventDefault();
            return false;
          });
          if (_n["is_dir"]) {
            tr.find('.dropdown-toggle').off('click').on('click', mk_tree(_t, _p, _e, _l));
          }
          tr.off('contextmenu').on('contextmenu', (e) => {
            target.find('.dropdown-menu').hide();
            e.preventDefault();
            return false;
          });
          return tr;
        };
        // ディレクトリを先に表示
        Object.entries(children).forEach(([k, n]) => {
          if(!n['is_dir'] || node['path']==n['path']) return;
          const tr = mk_tr(target, n['path'], current_ul_elem, n, is_local);
          table_body.append(tr);
        });
        // ファイルを表示
        Object.entries(children).forEach(([k, n]) => {
          if(n['is_dir']) return;
          const tr = mk_tr(target, n['path'], current_ul_elem, n, is_local);
          table_body.append(tr);
        });
      }
    });
    const fl_elem = target.find('.file-list').off('contextmenu').on('contextmenu', (e) => {
      target.find('.file-list-dropdown-menu').css('top', e.offsetY).css('left', e.offsetX).show();
      //e.preventDefault();
      return false;
    }).off('click').on('click', (e) => {
      target.find('.dropdown-menu').hide();
    });
    const ul_elem = $('<ul class="dropdown-menu file-list-dropdown-menu"/>');
    fl_elem.append(ul_elem);
    ul_elem.append($('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>'));
    // フォルダ作成関数の生成
    const _mk_mkdir = (_t, _e, _l) => {return ()=>{
      const _p = _t.find('.filer_address').val();
      //_p = _p.substring(0, _p.lastIndexOf('/')+1);
      const prompt_text = prompt('Enter a new folder name.');
      if(prompt_text) {
        const exec_cmd = _l ? fsapi.local_exec_cmd : cmdbox.sv_exec_cmd;
        cmdbox.file_mkdir(fsapi.right, `${_p=="/"?"":_p}/${prompt_text}`.replace("//","/"), undefined, exec_cmd).then(res => {
          cmdbox.hide_loading();
          fsapi.tree(_t, res['path'], _e, _l);
        });
      }
    }};
    ul_elem.find('.mkdir').off('click').on('click', _mk_mkdir(target, current_ul_elem, is_local));
  }).catch((e) => {
    console.log(e);
  }).finally(() => {
    cmdbox.hide_loading();
  });
}
// ローカル操作 ==============================================================
fsapi.safe_fname = (fname) => {
  return fname.replace(/[\s:\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]/g, '_');
}
fsapi.handles = {};
fsapi.file_list = async (target_path, current_path, dh) => {
  target_path = target_path.replace("\\","/").replace("//","/");
  const target_key = fsapi.safe_fname(target_path);
  current_path = current_path.replace("\\","/").replace("//","/");
  const current_key = fsapi.safe_fname(current_path);
  const path_tree = {};
  const children = {};
  for await (const entry of dh.values()) {
    let path = current_path + '/' + entry.name;
    path = path.replace("\\","/").replace("//","/");
    const key = fsapi.safe_fname(path);
    fsapi.handles[path] = entry;
    if (entry.kind === 'file') {
      const f = await entry.getFile();
      children[key] = {'name':entry.name, 'is_dir':false, 'path':path, 'mime_type':f.type, 'size':f.size, 'last':f.lastModified, 'local':true};
    }
    else if (entry.kind === 'directory') {
      children[key] = {'name':entry.name, 'is_dir':true, 'path':path, 'size':0, 'last':'', 'local':true};
      if (!target_path.startsWith(path)) {
        continue;
      }
      const res = await fsapi.file_list(target_path, path, entry);
      if (res && res[0] && res[0]['success']) {
        Object.keys(res[0]['success']).map((key) => {
          path_tree[key] = res[0]['success'][key];
        });
      }
    }
  }
  const current_name = current_path.split('/').pop();
  path_tree[current_key] = {'name':current_name?current_name :"/", 'is_dir':true, 'path':current_path, 'children':children, 'size':0, 'last':'', 'local':true};
  fsapi.handles[current_path] = dh;
  return [{"success": path_tree}]
}
fsapi.opendir = async () => {
  try {
    fsapi.dh = await window.showDirectoryPicker();
  } catch (e) {}
  fsapi.filer("/", true);
}
fsapi.local_exec_cmd = async (opt) => {
  if (opt['mode'] == 'client' && opt['cmd'] == 'file_list') {
    opt['svpath'] = opt['svpath'] ? opt['svpath'] : "/";
    fsapi.handles = {};
    return fsapi.file_list(opt['svpath'], "/", fsapi.dh);
  }
  else if (opt['mode'] == 'client' && opt['cmd'] == 'file_mkdir') {
    const parts = opt['svpath'].split('/');
    const dir = parts.slice(0, -1).join('/');
    const entry = fsapi.handles[dir];
    try {
      await entry.getDirectoryHandle(parts[parts.length-1], {create: true});
    } catch (e) {
      return {"warn": `Failed to create.${opt['svpath']}`};
    }
    return [{"success": {"path": dir}}];
  }
  else if (opt['mode'] == 'client' && (opt['cmd'] == 'file_remove' || opt['cmd'] == 'file_rmdir')) {
    const parts = opt['svpath'].split('/');
    const dir = parts.slice(0, -1).join('/');
    const entry = fsapi.handles[dir?dir:"/"];
    try {
      await entry.removeEntry(parts[parts.length-1], {recursive: false});
    } catch (e) {
      return {"warn": `Failed to delete.${opt['svpath']}`};
    }
    return [{"success": {"path": dir}}];
  }
  else if (opt['mode'] == 'server' && opt['cmd'] == 'list') {
    fsapi.tree(fsapi.left, "/", fsapi.left.find('.tree-menu'))
    return []
  }
  else if (opt['mode'] == 'client' && opt['cmd'] == 'file_download') {
    path = opt['svpath'];
    const entry = fsapi.handles[path];
    try {
      file = await entry.getFile();
      const reader = new FileReader();
      reader.readAsDataURL(file);
      return new Promise((resolve) => {
        reader.onload = () => {
          txt = reader.result.substring(reader.result.indexOf(',')+1);
          resolve([{"success": {"svpath": path, "data": txt}}]);
        };
      });
    } catch (e) {
      return {"warn": `Failed to view.${opt['svpath']}`};
    }
  }
  return {"warn": "Unknown command."}
};
fsapi.viewer = (title, data, path, mime) => {
  const viewer = $('#viewer_modal');
  viewer.find('.modal-title').text(title);
  viewer.find('.btn-save').remove();
  const viewer_body = viewer.find('.modal-body');
  viewer_body.html('');
  if (mime.indexOf('image') >= 0) {
    const img = $('<img class="img-fluid" />');
    if (path) img.attr('src', path);
    else img.attr('src', `data:${mime};base64,${data}`);
    viewer_body.append(img);
  } else if (mime.indexOf('pdf') >= 0) {
    const pdf = $(`<embed class="w-100 h-100" type="${mime}"></embed>`);
    if (path) pdf.attr('src', path);
    else  pdf.attr('src', `data:${mime};base64,${data}`);
    viewer_body.append(pdf);
  } else {
    cls = '';
    cls = mime == 'application/json' ? 'language-json' : cls;
    cls = mime == 'text/html' ? 'language-html' : cls;
    cls = mime == 'text/x-python' ? 'language-python' : cls;
    const pre = $(`<pre style="white-space:break-spaces;"><code class="${cls}" style="word-break:break-all;"></code></pre>`);
    viewer_body.append(pre);
    const txt = atob(data);
    const istxt = cmdbox.is_text(new TextEncoder().encode(txt));
    if (istxt) {
      // 文字コード判定
      const codes = Encoding.stringToCode(txt);
      let detectedEncoding = Encoding.detect(codes);
      detectedEncoding = detectedEncoding?detectedEncoding:'SJIS'
      // 文字コード変換
      const unicodeString = Encoding.convert(codes, {
        to: 'UNICODE',
        from: detectedEncoding,
        type: 'string'
      });
      pre.find('code').text(unicodeString.replace(/\r/g, ''));
      viewer.find('.modal-title').text(`[View] ${title} ( ${detectedEncoding} -> UNICODE )`);
    } else {
      pre.find('code').text('< This file is not text or image data. >');
    }
  }
  hljs.initHighlightingOnLoad();
  viewer.modal('show');
};
fsapi.editer = (svpath, data, mime, is_local) => {
  const viewer = $('#viewer_modal');
  viewer.find('.modal-title').text(svpath);
  viewer.find('.btn-save').remove();
  const viewer_body = viewer.find('.modal-body');
  viewer_body.html('');
  if (mime.indexOf('image') >= 0) {
    cmdbox.message({warn: 'This file is not text data.'});
    return;
  } else {
    const txt = atob(data);
    const istxt = cmdbox.is_text(new TextEncoder().encode(txt));
    if (!istxt) {
      cmdbox.message({warn: 'This file is not text data.'});
      return;
    }
    // 文字コード判定
    const codes = Encoding.stringToCode(txt);
    let detectedEncoding = Encoding.detect(codes);
    detectedEncoding = detectedEncoding?detectedEncoding:'SJIS'
    // 文字コード変換
    const unicodeString = Encoding.convert(codes, {
      to: 'UNICODE',
      from: detectedEncoding,
      type: 'string'
    });
    viewer.find('.modal-title').text(`[Edit] ${svpath} ( ${detectedEncoding} -> UNICODE )`);
    const textarea = $(`<textarea class="editer_code" style="width: calc(100% - 50px)"></textarea>`);
    let line_num = unicodeString.split('\n').length;
    line_num = line_num < 10 ? 10 : line_num;
    textarea.css('height', `${line_num*1.2}em`);
    viewer_body.append(textarea);
    textarea.html(unicodeString.replace(/\r/g, ''));
    const view_footer = viewer.find('.modal-footer');
    if (view_footer.find('.btn-save').length <= 0) {
      const btn_save = $('<button type="button" class="btn btn-success btn-save">Save</button>');
      view_footer.append(btn_save);
      btn_save.off('click').on('click', async () => {
        if (!window.confirm('Do you want to save the changes?')) return;
        // 保存処理
        const text = textarea.val();
        const ppath = svpath.slice(0, svpath.lastIndexOf('/'));
        const fpath = svpath.slice(svpath.lastIndexOf('/')+1);
        const blob = new Blob([text], {type:mime});
        if (!is_local) {
          // リモート側に保存
          const formData = new FormData();
          formData.append('files', blob, fpath);
          cmdbox.file_upload(fsapi.right, ppath, formData, true, undefined, (target, svpath, data) => {
            cmdbox.message(data);
            viewer.modal('hide');
          }, (target, svpath, data) => {
            cmdbox.message(data);
            viewer.modal('hide');
          });
        } else {
          // ローカル側に保存
          try {
            const down_dir = fsapi.handles[ppath?ppath:"/"];
            const down_file = await down_dir.getFileHandle(fpath, {create: true});
            const writable = await down_file.createWritable();
            await writable.write(blob);
            await writable.close();
            cmdbox.message('Save successed.');
            viewer.modal('hide');
          } catch (e) {
            cmdbox.message(e);
            viewer.modal('hide');
          }
        }
      });
    }
    viewer.modal('show');
    textarea.linedtextarea();
    viewer_body.find('.linedwrap').css('width','100%').css('height','100%');
    viewer_body.find('.lines').css('height','100%');
    textarea.css('width','calc(100% - 60px)').css('resize','');
  }
};
fsapi.onload = () => {
  cmdbox.get_server_opt(true, fsapi.right).then((opt) => {
    fsapi.filer("/", false);
  });
  hljs.addPlugin({
    'after:highlightElement': ({el, result}) => {
        el.innerHTML = result.value.replace(/^/gm,'<span class="row-number"></span>');
    }
  });
}
