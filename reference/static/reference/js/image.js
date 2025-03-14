function drawCanvas(canvas, context) {
    let image = new Image();
    image.src = "data:image/png;base64," + imageBase64;
    image.onload = function () {
        context.drawImage(image, 0, 0);
        let sx = document.getElementById('StartX').value;
        let sy = document.getElementById('StartY').value;
        let ex = document.getElementById('EndX').value;
        let ey = document.getElementById('EndY').value;
        context.lineWidth = 1;
        context.strokeStyle = 'rgb(255, 0, 0)';
        context.strokeRect(sx, sy, ex - sx, ey - sy);
    }
}

function drawSelection(context, mouse) {
    let w = mouse.x - mouse.startX;
    let h = mouse.y - mouse.startY;
    context.lineWidth = 1;
    context.strokeStyle = 'rgb(255, 0, 0)';
    context.strokeRect(mouse.startX / imageRatio, mouse.startY / imageRatio, w / imageRatio, h / imageRatio);
}

function setRegion(mouse) {
    let sx, sy, ex, ey;
    if (mouse.x > mouse.startX) {
        sx = mouse.startX;
        ex = mouse.x;
    } else {
        sx = mouse.x;
        ex = mouse.startX;
    }
    if (mouse.y > mouse.startY) {
        sy = mouse.startY;
        ey = mouse.y;
    } else {
        sy = mouse.y;
        ey = mouse.startY;
    }
    document.getElementById('StartX').value = Math.round(sx / imageRatio);
    document.getElementById('StartY').value = Math.round(sy / imageRatio);
    document.getElementById('EndX').value = Math.round(ex / imageRatio);
    document.getElementById('EndY').value = Math.round(ey / imageRatio);
}

function updateAPI() {
    const xhr = new XMLHttpRequest();
    xhr.open("PATCH", apiupdateURL);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken);
    let json = JSON.stringify({
        'startx': document.getElementById('StartX').value,
        'starty': document.getElementById('StartY').value,
        'endx': document.getElementById('EndX').value,
        'endy': document.getElementById('EndY').value,
        'zoom': document.getElementById('Zoom').value
    });
    xhr.send(json);
    xhr.onload = function () {
        location.href = detailURL;
    };
}

// function getPDFImage(canvas, context, fcanvas) {
//     const url = '/reference/api/image/' + objectID + '/pdfimage';
//     const xhr = new XMLHttpRequest();
//     xhr.open("POST", url);
//     xhr.setRequestHeader("Content-Type", "application/json");
//     xhr.setRequestHeader("X-CSRFToken", csrfToken);
//     let json = JSON.stringify({
//         'page': parseInt(document.getElementById('Page').value),
//         'scale': parseFloat(document.getElementById('Scale').value),
//         'rotate': parseFloat(document.getElementById('Rotate').value)
//     });
//     xhr.send(json);
//     xhr.onload = function () {
//         ret = JSON.parse(xhr.responseText);
//         if (ret['width'] > 0 && ret['height'] > 0) {
//             imageWidth = ret['width'];
//             imageHeight = ret['height'];
//             imageBase64 = ret['image'];
//             drawCanvas(canvas, context);
//         }
//     }
// }

function updateZoom(canvas, fcanvas) {
    let zoom = document.getElementById('Zoom').value;
    let width = imageWidth * zoom / 100;
    let height = imageHeight * zoom / 100;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    fcanvas.style.width = width + 'px';
    fcanvas.style.height = height + 'px';
    imageRatio = zoom / 100;
    document.getElementById('ZoomValue').innerText = zoom;
}

function init() {
    let canvas = document.getElementById('canvas');
    let context = canvas.getContext('2d');
    let fcanvas = document.getElementById('canvas_front');
    let fcontext = fcanvas.getContext('2d');
    drawCanvas(canvas, context);
    updateZoom(canvas, fcanvas)
    let mouse = {
        startX: 0,
        startY: 0,
        x: 0,
        y: 0,
        isDown: false
    };
    fcanvas.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX - canvas_front.getBoundingClientRect().left;
        mouse.y = e.clientY - canvas_front.getBoundingClientRect().top;
        if (mouse.isDown) {
            fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
            drawSelection(fcontext, mouse);
        }
    });
    fcanvas.addEventListener("mousedown", function (e) {
        mouse.isDown = true;
        mouse.startX = mouse.x;
        mouse.startY = mouse.y;
    });
    fcanvas.addEventListener("mouseup", function (e) {
        mouse.isDown = false;
        fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
        setRegion(mouse);
        drawCanvas(canvas, context);
    });
    document.getElementById('StartX').addEventListener('change', () => {
        drawCanvas(canvas, context);
    });
    document.getElementById('StartY').addEventListener('change', () => {
        drawCanvas(canvas, context);
    });
    document.getElementById('EndX').addEventListener('change', () => {
        drawCanvas(canvas, context);
    });
    document.getElementById('EndY').addEventListener('change', () => {
        drawCanvas(canvas, context);
    });
    document.getElementById('Zoom').addEventListener('change', () => {
        updateZoom(canvas, fcanvas);
    });
    // document.getElementById('Page').addEventListener('change', () => {
    //     getPDFImage(canvas, context, fcanvas);
    // });
    // document.getElementById('Scale').addEventListener('change', () => {
    //     getPDFImage(canvas, context, fcanvas);
    // });
    // document.getElementById('Rotate').addEventListener('change', () => {
    //     getPDFImage(canvas, context, fcanvas);
    // });
    document.getElementById('buttonSave').addEventListener('click', () => {
        updateAPI();
    });
}
window.onload = init;
