agentView.fileuploader = {};
/**
 * アップロード機能の初期化
 */
agentView.fileuploader.initUploadPanel = () => {
    const dropArea = $('#upload_drop_area');
    const fileInput = $('#upload_file_input');
    const fileSelectBtn = $('#upload_file_select_btn');
    const fileList = $('#upload_file_list');
    const clearBtn = $('#upload_clear_btn');
    const startBtn = $('#upload_start_btn');

    // 選択されたファイル
    agentView.fileuploader.uploadFiles = [];

    // ドラッグアンドドロップの開始・終了時のハイライト
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.on(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    // ドラッグオーバー時のスタイル変更
    ['dragenter', 'dragover', 'mouseenter', 'mouseover'].forEach(eventName => {
        dropArea.on(eventName, () => {
            dropArea.css('transform', 'scale(1.02)');
        });
    });

    // ドラッグリーブ時のスタイル戻し
    ['dragleave', 'drop', 'mouseleave', 'mouseout'].forEach(eventName => {
        dropArea.on(eventName, () => {
            dropArea.css('transform', 'scale(1)');
        });
    });

    // ファイルがドロップされたときの処理
    dropArea.on('drop', (e) => {
        const dt = e.originalEvent.dataTransfer;
        const files = dt.files;
        agentView.fileuploader.handleFileSelect(files);
    });

    // クリックでファイル選択
    fileSelectBtn.off('click').on('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    // ファイル入力の変更
    fileInput.off('change').on('change', function() {
        agentView.fileuploader.handleFileSelect(this.files);
    });

    // クリアボタン
    clearBtn.off('click').on('click', (e) => {
        e.preventDefault();
        agentView.fileuploader.uploadFiles = [];
        fileInput.val('');
        agentView.fileuploader.updateUploadFileList();
    });

    // アップロード開始ボタン
    startBtn.off('click').on('click', async (e) => {
        e.preventDefault();
        if (agentView.fileuploader.uploadFiles.length === 0) {
            cmdbox.message({ 'error': 'ファイルが選択されていません' });
            return;
        }
        await agentView.fileuploader.uploadFiles_execute();
    });
    cmdbox.user_info().then(user => {
        agentView.user = user;
        const user_name = agentView.user ? agentView.user['name'] : 'USER';
        $('#upload_target').text(`TO : /.users/${user_name}/`);
    });

    console.log('agent_files.js initialized.');
};

/**
 * ファイル選択の処理
 */
agentView.fileuploader.handleFileSelect = (files) => {
    if (files && files.length > 0) {
        agentView.fileuploader.uploadFiles = Array.from(files);
        agentView.fileuploader.updateUploadFileList();
    }
};

/**
 * アップロードファイルリストの更新
 */
agentView.fileuploader.updateUploadFileList = () => {
    const fileList = $('#upload_file_list');
    const clearBtn = $('#upload_clear_btn');
    const startBtn = $('#upload_start_btn');

    fileList.empty();

    if (agentView.fileuploader.uploadFiles.length === 0) {
        fileList.html('<li class="list-group-item text-white-50 text-center py-3">ファイルが選択されていません</li>');
        return;
    }
    agentView.fileuploader.uploadFiles.forEach((file, index) => {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const listItem = `
            <li class="list-group-item d-flex justify-content-between align-items-center" id="upload_file_${index}">
                <div class="d-flex align-items-center flex-grow-1">
                    <i class="fa-solid fa-file me-2" style="color:var(--accent-cyan);"></i>
                    <div class="flex-grow-1">
                        <div class="text-break">${file.name}</div>
                        <small class="text-white-50">${sizeMB} MB</small>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger upload-file-remove-btn" data-index="${index}">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </li>
        `;
        fileList.append(listItem);
    });

    // 削除ボタンのイベント
    fileList.find('.upload-file-remove-btn').off('click').on('click', (e) => {
        const index = $(e.currentTarget).data('index');
        agentView.fileuploader.uploadFiles.splice(index, 1);
        agentView.fileuploader.updateUploadFileList();
    });
};

/**
 * ファイルアップロードの実行
 */
agentView.fileuploader.uploadFiles_execute = async () => {
    const fileList = $('#upload_file_list');
    
    if (!agentView.fileuploader.uploadFiles || agentView.fileuploader.uploadFiles.length === 0) {
        cmdbox.message({ 'error': 'ファイルが選択されていません' });
        return;
    }

    cmdbox.show_loading();
    const totalFiles = agentView.fileuploader.uploadFiles.length;
    
    try {
        // プログレス表示
        cmdbox.progress(0, totalFiles, 0, `アップロード中: ...`, true, false);
        // ユーザー情報の取得
        const user_name = agentView.user ? agentView.user['name'] : 'USER';
        // FormDataを準備
        const formData = new FormData();
        for (let i = 0; i < totalFiles; i++) {
            const file = agentView.fileuploader.uploadFiles[i];
            const fileName = file.name;
            const fileSize = file.size;
            formData.append('files', file);
        }
        const reset = () => {
            agentView.fileuploader.uploadFiles = [];
            $('#upload_file_input').val('');
            agentView.fileuploader.updateUploadFileList();
        };
        cmdbox.file_upload(fsapi.right, `/.users/${user_name}/`, formData, orverwrite=false,
            progress_func=(e) => {
                cmdbox.progress(0, e.total, e.loaded, '', true, e.total==e.loaded);
            },
            success_func=(target, svpath, data) => {
                const listItem = fileList.find('li i.fa-file');
                listItem.removeClass('fa-file').addClass('fa-check').css('color', 'var(--accent-green)');
                cmdbox.hide_loading();
                setTimeout(reset, 5000);
            },
            error_func=(target, svpath, data) => {
                const listItem = fileList.find('li i.fa-file');
                listItem.removeClass('fa-file').addClass('fa-exclamation').css('color', 'var(--accent-red)');
                cmdbox.hide_loading();
                setTimeout(reset, 5000);
            }
        );
        
    } catch (err) {
        console.error('Upload error:', err);
        cmdbox.hide_loading();
        cmdbox.message({ 'error': 'アップロード中にエラーが発生しました' });
    }
};
