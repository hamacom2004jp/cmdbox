// captureファイルを選択して表示する
const open_capture_func = (target_id) => {
    // ファイル選択後に結果画面を開く
    const view_capture_func = (current_path) => {
        load_capture(current_path).then((result) =>{
            view_result_func(current_path, result);
            cmdbox.hide_loading();
        });
    };
    fmodal.filer_modal_func(target_id, 'capture', '', false, true, view_capture_func);
};
const load_capture = async (current_path) => {
    const formData = new FormData();
    formData.append('current_path', current_path);
    const res = await fetch('gui/load_capture', {method: 'POST', body: formData});
    return await res.json();
}