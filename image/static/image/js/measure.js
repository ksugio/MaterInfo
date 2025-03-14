function drawLines(context, pts, type) {
    context.lineWidth = 1;
    context.strokeStyle = 'rgb(255, 0, 0)';
    context.beginPath();
    context.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) {
        context.lineTo(pts[i][0], pts[i][1]);
    }
    if (type == 2) {
        context.lineTo(pts[0][0], pts[0][1])
    }
    context.stroke();
}

function drawCanvas(context, type) {
    let image = new Image();
    image.src = "data:image/png;base64," + imageBase64;
    image.onload = function () {
        context.drawImage(image, 0, 0);
        for (let i = 0; i < measureData.length; i++) {
            drawLines(context, measureData[i], type);
        }
    }
}

function ScalePoints(pts) {
    newpts = [];
    for (let i = 0; i < pts.length; i++) {
        let px = Math.round(pts[i][0] / imageRatio);
        let py = Math.round(pts[i][1] / imageRatio);
        newpts.push([px, py]);
    }
    return newpts;
}

function drawSelection(context, mouse) {
    if (document.getElementById('deleteCheck').checked) {
        context.lineWidth = 1;
        context.strokeStyle = 'rgb(255, 255, 255)';
        let w = mouse.x - mouse.pts[0][0];
        let h = mouse.y - mouse.pts[0][1]
        context.strokeRect(mouse.pts[0][0] / imageRatio, mouse.pts[0][1] / imageRatio,
            w / imageRatio, h / imageRatio);
    }
    else {
        let pts = JSON.parse(JSON.stringify(mouse.pts));
        pts.push([mouse.x, mouse.y]);
        drawLines(context, ScalePoints(pts));
    }
}

function checkPoint(region, pt) {
    if (pt[0] >= region[0] && pt[0] <= region[2] && pt[1] >= region[1] && pt[1] <= region[3]) {
        return true;
    }
    else {
        return false;
    }
}

function deleteMeasure(mouse) {
    let sx, sy, ex, ey;
    if (mouse.x > mouse.pts[0][0]) {
        sx = mouse.pts[0][0];
        ex = mouse.x;
    }
    else {
        sx = mouse.x;
        ex = mouse.pts[0][0];
    }
    if (mouse.y > mouse.pts[0][1]) {
        sy = mouse.pts[0][1];
        ey = mouse.y;
    }
    else {
        sy = mouse.y;
        ey = mouse.pts[0][1];
    }
    let region = [sx / imageRatio, sy / imageRatio, ex / imageRatio, ey / imageRatio];
    let deleteid = [];
    for (let i = 0; i < measureData.length; i++) {
        let measure = measureData[i];
        let j;
        for (j = 0; j < measure.length; j++) {
            if (!checkPoint(region, measure[j])) {
                break;
            }
        }
        if (j == measure.length) {
            deleteid.push(i);
        }
    }
    for (let i = deleteid.length - 1; i >= 0; i--) {
        measureData.splice(deleteid[i], 1);
    }
}

function init() {
    document.getElementById('Zoom').value = 100;
    document.getElementById('ZoomValue').innerText = 100;
    let canvas = document.getElementById('canvas');
    let context = canvas.getContext('2d');
    drawCanvas(context, measureType);
    let fcanvas = document.getElementById('canvas_front');
    let fcontext = fcanvas.getContext('2d');
    let mouse = {
        pts: [],
        x: 0,
        y: 0,
        isOn: false
    };
    fcanvas.addEventListener("mousemove", function(e) {
        mouse.x = e.clientX - canvas_front.getBoundingClientRect().left;
        mouse.y = e.clientY - canvas_front.getBoundingClientRect().top;
        if (mouse.isOn) {
            fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
            drawSelection(fcontext, mouse);
        }
    });
    fcanvas.addEventListener("mousedown", function(e){
        mouse.pts.push([mouse.x, mouse.y]);
        if (mouse.isOn) {
            if (document.getElementById('deleteCheck').checked) {
                deleteMeasure(mouse);
                mouse.isOn = false;
                mouse.pts = []
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context, measureType);
            }
            else if (measureType == 0 && mouse.pts.length == 2) {
                measureData.push(ScalePoints(mouse.pts));
                mouse.isOn = false;
                mouse.pts = []
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context, measureType);
            }
            else if (measureType == 1 && mouse.pts.length == 3) {
                measureData.push(ScalePoints(mouse.pts));
                mouse.isOn = false;
                mouse.pts = []
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context, measureType);
            }
            else if (measureType == 2){
                dx = mouse.x - mouse.pts[0][0];
                dy = mouse.y - mouse.pts[0][1];
                if (Math.sqrt(dx * dx + dy * dy) < 3) {
                    mouse.pts.pop();
                    measureData.push(ScalePoints(mouse.pts));
                    mouse.isOn = false;
                    mouse.pts = []
                    fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                    drawCanvas(context, measureType);
                }
            }
        }
        else {
            mouse.isOn = true;
        }
    });
    document.getElementById('buttonPop').addEventListener('click', () => {
        measureData.pop();
        drawCanvas(context, measureType);
    });
    document.getElementById('Zoom').addEventListener('change', () => {
        let zoom = document.getElementById('Zoom').value;
        let width = imageWidth * zoom / 100;
        let height = imageHeight * zoom / 100;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        fcanvas.style.width = width + 'px';
        fcanvas.style.height = height + 'px';
        imageRatio = zoom / 100;
        document.getElementById('ZoomValue').innerText = zoom;
    });
    document.getElementById('buttonSave').addEventListener('click', () => {
        const xhr = new XMLHttpRequest();
        xhr.open("PATCH", apiupdateURL);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("X-CSRFToken", csrfToken);
        let json = JSON.stringify({
            'data': JSON.stringify(measureData)
        });
        xhr.send(json);
        xhr.onload = function () {
            location.href = detailURL;
        };
    });
}
window.onload = init;
