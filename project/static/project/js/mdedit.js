function setText(editor, preview) {
    let html = marked.parse(editor.value);
    preview.innerHTML = html;
    MathJax.typesetPromise('Preview');
    hljs.highlightAll();
}

function updateAPI() {
    const xhr = new XMLHttpRequest();
    xhr.open("PATCH", apiupdateURL);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken);
    let text = document.getElementById('Editor').value;
    let data = {};
    data[textField] = text;
    let json = JSON.stringify(data);
    xhr.send(json);
    xhr.onload = function () {
        location.href = detailURL;
    };
}

function init() {
    let editor = document.getElementById('Editor');
    let editorbox = document.getElementById('EditorBox');
    let preview = document.getElementById('Preview');
    let previewbox = document.getElementById('PreviewBox');
    let selectview = document.getElementById('selectView');
    previewbox.style.display = 'none';
    setText(editor, preview);
    editor.addEventListener('keyup', function(e) {
        if (previewbox.style.display == 'block') {
            setText(editor, preview);
        }
    });
    editor.addEventListener('scroll', function(e) {
        let ratio = editor.scrollTop / (editor.scrollHeight - editorHeight);
        previewbox.scrollTop = ratio * (previewbox.scrollHeight - editorHeight);
    });
    const resizeObserver = new ResizeObserver((entries) => {
        if (editorbox.style.display == 'block') {
            const height = entries[0].borderBoxSize[0].blockSize;
            previewbox.style.height = height;
        }
    });
    resizeObserver.observe(editor);
    selectview.addEventListener('change', function(e) {
        if (selectview.selectedIndex == 0) {
            editorbox.style.display = 'block';
            previewbox.style.display = 'none';
        }
        else if (selectview.selectedIndex == 1) {
            editorbox.style.display = 'block';
            previewbox.style.display = 'block';
            setText(editor, preview);
        }
        else if (selectview.selectedIndex == 2) {
            editorbox.style.display = 'none';
            previewbox.style.display = 'block';
            setText(editor, preview);
        }
    });
    document.getElementById('buttonSave').addEventListener('click', () => {
        updateAPI();
    });
}
window.onload = init;
