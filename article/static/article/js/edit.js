function setText(editor, preview) {
    let html = marked.parse(editor.value);
    preview.innerHTML = html;
    MathJax.typesetPromise('Preview');
    hljs.highlightAll();
}

function setPDF(editor, preview, log) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", apipdfURL);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken);
    let text = document.getElementById('Editor').value;
    let data = {};
    data["text"] = text;
    let json = JSON.stringify(data);
    xhr.send(json);
    xhr.onload = function () {
        json = JSON.parse(xhr.responseText);
        if (json.data) {
            preview.type = `${json.type}`
            preview.src = `data:${json.type};${json.encode},${json.data}`;
            log.innerText = json.log;
        }
        else if (json.std) {
            preview.type = `${json.type}`
            preview.src = `data:${json.type},${json.std}`;
            log.innerText = json.log;
        }
    };
}

function updateAPI() {
    const xhr = new XMLHttpRequest();
    xhr.open("PATCH", apiupdateURL);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken);
    let text = document.getElementById('Editor').value;
    let comment = document.getElementById('Comment').value;
    let data = {};
    data["text"] = text;
    data["comment"] = comment;
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
    previewbox.style.display = 'none';
    let selectview = document.getElementById('selectView');
    let log = document.getElementById('Log');
    let logbox = document.getElementById('LogBox');
    logbox.style.display = 'none';
    if (articleType == 0) setText(editor, preview);
    else if (articleType == 1) setPDF(editor, preview, log);
    let textmodified = false;
    editor.addEventListener('keyup', function(e) {
        if (articleType == 0 && previewbox.style.display == 'block') {
            setText(editor, preview);
        }
        textmodified = true;
    });
    if (articleType == 0) {
        editor.addEventListener('scroll', function (e) {
            let ratio = editor.scrollTop / (editor.scrollHeight - editorHeight);
            previewbox.scrollTop = ratio * (previewbox.scrollHeight - editorHeight);
        });
    }
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
            logbox.style.display = 'none';
        }
        else if (selectview.selectedIndex == 1) {
            editorbox.style.display = 'block';
            previewbox.style.display = 'block';
            logbox.style.display = 'none';
            if (articleType == 0) setText(editor, preview);
            else if (articleType == 1 && textmodified) {
                setPDF(editor, preview, log);
                textmodified = false;
            }
        }
        else if (selectview.selectedIndex == 2) {
            editorbox.style.display = 'none';
            previewbox.style.display = 'block';
            logbox.style.display = 'none';
            if (articleType == 0) setText(editor, preview);
            else if (articleType == 1 && textmodified) {
                setPDF(editor, preview, log);
                textmodified = false;
            }
        }
        else if (selectview.selectedIndex == 3) {
            editorbox.style.display = 'none';
            previewbox.style.display = 'none';
            logbox.style.display = 'block';
        }
    });
    if (articleType == 1) {
        document.getElementById('buttonCompile').addEventListener('click', () => {
            setPDF(editor, preview, log);
            texmodified = false;
        });
    }
    document.getElementById('buttonSave').addEventListener('click', () => {
        updateAPI();
    });
}
window.onload = init;
