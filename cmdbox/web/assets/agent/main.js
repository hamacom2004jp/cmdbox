$(() => {
    fetch('assets/agent/agent_sidebar_content.html').then(res => res.text()).then(async html => {
        try {
            // 設定画面の読込み
            const setting_html = await fetch('assets/agent/agent_settings.html').then(res => res.text());
            $('.layout-grid').append(setting_html);

            // LLM追加/編集モーダルの読込み
            const llm_edit_html = await fetch('assets/agent/agent_settings_llm.html').then(res => res.text());
            $('.layout-grid').append(llm_edit_html);

            // MCPSV追加/編集モーダルの読込み
            const mcpsv_edit_html = await fetch('assets/agent/agent_settings_mcpsv.html').then(res => res.text());
            $('.layout-grid').append(mcpsv_edit_html);

            // agent追加/編集モーダルの読込み
            const agent_edit_html = await fetch('assets/agent/agent_settings_agent.html').then(res => res.text());
            $('.layout-grid').append(agent_edit_html);

            // embed追加/編集モーダルの読込み
            const embed_edit_html = await fetch('assets/agent/agent_settings_embed.html').then(res => res.text());
            $('.layout-grid').append(embed_edit_html);

            // memory追加/編集モーダルの読込み
            const memory_edit_html = await fetch('assets/agent/agent_settings_memory.html').then(res => res.text());
            $('.layout-grid').append(memory_edit_html);

            // rag追加/編集モーダルの読込み
            const rag_edit_html = await fetch('assets/agent/agent_settings_rag.html').then(res => res.text());
            $('.layout-grid').append(rag_edit_html);

            // extract追加/編集モーダルの読込み
            const extract_edit_html = await fetch('assets/agent/agent_settings_extract.html').then(res => res.text());
            $('.layout-grid').append(extract_edit_html);

            // runner追加/編集モーダルの読込み
            const runner_edit_html = await fetch('assets/agent/agent_settings_runner.html').then(res => res.text());
            $('.layout-grid').append(runner_edit_html);

            // ファイラー画面の読込み
            const files_html = await fetch('assets/agent/agent_files.html').then(res => res.text());
            $('.layout-grid').append(files_html);
            fsapi.left = $('#left_container');
            fsapi.right = $('#right_container');

            // SVGロゴ初期化
            init_svglogo();
            $('.split-pane').splitPane();
            // --- サイドバー初期化 ---
            agentView.navSidebar = $('#navSidebar');
            agentView.navSidebar.find('.nav-sidebar-content').remove();
            agentView.navSidebar.append(html);
            agentView.btnToggleSidebar = $('#btn_toggle_sidebar');
            agentView.sidebarExpanded = false;

            agentView.btnToggleSidebar.on('click', () => {
                agentView.sidebarExpanded = !agentView.sidebarExpanded;
                if (agentView.sidebarExpanded) {
                    agentView.navSidebar.addClass('expanded');
                } else {
                    agentView.navSidebar.removeClass('expanded');
                }
            });
            // agent初期化
            agentView.initView();
            // アップロード機能の初期化
            agentView.fileuploader.initUploadPanel();
            // バージョン情報モーダル初期化
            cmdbox.init_version_modal();
            // モーダルボタン初期化
            cmdbox.init_modal_button();
        } finally {
            cmdbox.hide_loading();
        }
    });
});
// ノード変更を監視
const buttons = ['nav-sidebar-content','btn_histories'];
buttons.forEach(btnId => {
    const btn = document.querySelector(`#${btnId}`);
    if (btn) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(m => {
                console.log(`⚠️ ${btnId} changed:`, m);
                console.trace(); // 呼び出し元を表示
            });
        });
        observer.observe(btn, { attributes: true });
    }
});
