$(() => {
    fetch('assets/agent/agent_sidebar_content.html').then(res => res.text()).then(async html => {
        try {
            // 全HTMLファイルを並行読込み（大幅な高速化）
            const htmlPromises = {
                setting_html: fetch('assets/agent/agent_settings.html').then(res => res.text()),
                llm_edit_html: fetch('assets/agent/agent_settings_llm.html').then(res => res.text()),
                mcpsv_edit_html: fetch('assets/agent/agent_settings_mcpsv.html').then(res => res.text()),
                agent_edit_html: fetch('assets/agent/agent_settings_agent.html').then(res => res.text()),
                rag_edit_html: fetch('assets/agent/agent_settings_rag.html').then(res => res.text()),
                extract_edit_html: fetch('assets/agent/agent_settings_extract.html').then(res => res.text()),
                runner_edit_html: fetch('assets/agent/agent_settings_runner.html').then(res => res.text()),
                datasource_edit_html: fetch('assets/agent/agent_settings_datasource.html').then(res => res.text()),
                skill_edit_html: fetch('assets/agent/agent_settings_skill.html').then(res => res.text()),
                files_html: fetch('assets/agent/agent_files.html').then(res => res.text()),
                chat_input_html: fetch('assets/agent/agent_chat_input.html').then(res => res.text()),
                navbar_html: fetch('assets/agent/agent_navbar.html').then(res => res.text())
            };
            
            // すべてのfetchを並行実行し完了を待機
            const htmlContents = await Promise.all(Object.values(htmlPromises));
            const htmlKeys = Object.keys(htmlPromises);
            
            // 取得したHTMLを元の変数名で割り当て
            const [setting_html, llm_edit_html, mcpsv_edit_html, agent_edit_html, rag_edit_html, 
                    extract_edit_html, runner_edit_html, datasource_edit_html, skill_edit_html, 
                    files_html, chat_input_html, navbar_html] = htmlContents;
            
            // DOMへの追加
            $('.layout-grid').append(setting_html);
            $('.layout-grid').append(llm_edit_html);
            $('.layout-grid').append(mcpsv_edit_html);
            $('.layout-grid').append(agent_edit_html);
            $('.layout-grid').append(rag_edit_html);
            $('.layout-grid').append(extract_edit_html);
            $('.layout-grid').append(runner_edit_html);
            $('.layout-grid').append(datasource_edit_html);
            $('.layout-grid').append(skill_edit_html);
            $('.layout-grid').append(files_html);
            fsapi.left = $('#left_container');
            fsapi.right = $('#right_container');

            // SVGロゴ初期化
            init_svglogo();
            $('.split-pane').splitPane();

            // チャット入力エリアの読込み
            $('#chatInputArea').append(chat_input_html);

            // ナビゲーションバーの読込み
            $('#navHeadbar').append(navbar_html);
            cmdbox.set_logoicon('.navbar-brand');
            cmdbox.appid('.navbar-brand');

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

            const initConsoleExpandButton = () => {
                const splitPane = $('.layout-grid > .split-pane.fixed-left').first();
                const consolePanel = $('.console-panel').first();
                const visualizerPanel = $('.visualizer-panel').first();
                const btn = $('#btn_console_expand_80');
                if (!splitPane.length || !consolePanel.length || !btn.length) return;

                const updateButtonState = (expanded) => {
                    if (expanded) {
                        btn.attr('data-expanded', 'true');
                        btn.find('i').removeClass('fa-expand').addClass('fa-compress');
                    } else {
                        btn.attr('data-expanded', 'false');
                        btn.find('i').removeClass('fa-compress').addClass('fa-expand');
                    }
                };

                updateButtonState(false);
                btn.off('click').on('click', () => {
                    const splitPaneWidth = splitPane[0].clientWidth;
                    const dividerWidth = splitPane.children('.split-pane-divider-left').outerWidth() || 0;
                    const minLeft = parseInt(consolePanel.css('min-width'), 10) || 350;
                    const minRight = parseInt(visualizerPanel.css('min-width'), 10) || 0;
                    const maxLeft = Math.max(minLeft, splitPaneWidth - minRight - dividerWidth);
                    const isExpanded = btn.attr('data-expanded') === 'true';

                    if (!isExpanded) {
                        const currentWidth = consolePanel.outerWidth() || minLeft;
                        const targetWidth = Math.round(window.innerWidth * 0.8);
                        const nextWidth = Math.min(maxLeft, Math.max(minLeft, targetWidth));
                        btn.attr('data-prev-width', String(currentWidth));
                        splitPane.splitPane('firstComponentSize', nextWidth);
                        updateButtonState(true);
                    } else {
                        const prevWidth = parseInt(btn.attr('data-prev-width'), 10);
                        const restoreWidth = Number.isFinite(prevWidth)
                            ? Math.min(maxLeft, Math.max(minLeft, prevWidth))
                            : minLeft;
                        splitPane.splitPane('firstComponentSize', restoreWidth);
                        updateButtonState(false);
                    }
                });
            };

            initConsoleExpandButton();
            // agent初期化
            agentView.initView();
            // アップロード機能の初期化
            agentView.fileuploader.initUploadPanel();
            // バージョン情報モーダル初期化
            cmdbox.init_version_modal();
            // モーダルボタン初期化
            cmdbox.init_modal_button();
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
                await cmdbox.process_i18n();
                // デフォルトのRunnerを設定
                await agentView.setDefaultRunner();
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
