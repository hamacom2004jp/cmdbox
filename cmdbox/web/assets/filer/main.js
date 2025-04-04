$(() => {
  // カラーモード対応
  cmdbox.change_color_mode();
  // スプリッター初期化
  $('.split-pane').splitPane();
  // アイコンを表示
  cmdbox.set_logoicon('.navbar-brand');
  // copyright表示
  cmdbox.copyright();
  // バージョン情報モーダル初期化
  cmdbox.init_version_modal();
  // モーダルボタン初期化
  cmdbox.init_modal_button();
  // ファイラー画面初期化
  fsapi.onload();
});
