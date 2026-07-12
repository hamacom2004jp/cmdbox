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

            // rag追加/編集モーダルの読込み
            const rag_edit_html = await fetch('assets/agent/agent_settings_rag.html').then(res => res.text());
            $('.layout-grid').append(rag_edit_html);

            // extract追加/編集モーダルの読込み
            const extract_edit_html = await fetch('assets/agent/agent_settings_extract.html').then(res => res.text());
            $('.layout-grid').append(extract_edit_html);

            // runner追加/編集モーダルの読込み
            const runner_edit_html = await fetch('assets/agent/agent_settings_runner.html').then(res => res.text());
            $('.layout-grid').append(runner_edit_html);

            // datasource追加/編集モーダルの読込み
            const datasource_edit_html = await fetch('assets/agent/agent_settings_datasource.html').then(res => res.text());
            $('.layout-grid').append(datasource_edit_html);

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
            // 多言語対応のためのテキスト翻訳を処理
            setTimeout(() => {cmdbox.process_i18n();}, 100);
            // ツールメニュー初期化
            const tools = async (sel, url) => {
                const res = await fetch(url, {method: 'GET'});
                const menu = await res.json();
                for (let key in menu) {
                    const m = menu[key];
                    const li = $('<li>');
                    const css_class = m["css_class"] ? m["css_class"] : '';
                    const href = m["href"] ? m["href"] : '#';
                    const target = m["target"] ? m["target"] : '_self';
                    const onclick = m["onclick"] ? m["onclick"] : '';
                    const html = m["html"] ? m["html"] : '';
                    const a = $('<a>').attr('class', css_class).attr('href', href).attr('onclick', onclick).attr('target', target);
                    a.addClass('i18n').html(html);
                    li.append(a);
                    $(sel).append(li);
                }
                cmdbox.process_i18n($(sel));
            };
            // ユーザー情報メニュー初期化
            cmdbox.init_user_info_menu().then(async () => {
                // ツールメニュー初期化
                const bar = $('.nav-sidebar-content');
                const res = await fetch('gui/toolmenu', {method: 'GET'});
                const item = await res.json();
                const menu_ul = bar.find('.tools_menu ul');
                for (let key in item) {
                    const m = item[key];
                    if (m["href"]=="agent") continue;
                    const li = $('<li>').appendTo(menu_ul);
                    const a = $('<a class="dropdown-item i18n"/>').appendTo(li);
                    a.html(m["html"] || '');
                    a.addClass(m["css_class"] ? m["css_class"] : '');
                    a.attr('href', m["href"] ? m["href"] : '#');
                    a.attr('target', m["target"] ? m["target"] : '_self');
                    a.attr('onclick', m["onclick"] ? m["onclick"] : '');
                }
                cmdbox.process_i18n(menu_ul);
                // デフォルトのRunnerを設定
                agentView.setDefaultRunner();
            });
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
