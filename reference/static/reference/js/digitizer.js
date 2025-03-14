function drawLines(context, pts, width, style) {
    context.lineWidth = width;
    context.strokeStyle = style;
    context.beginPath();
    context.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) {
        context.lineTo(pts[i][0], pts[i][1]);
    }
    context.stroke();
}

function drawRectangle(context, pt1, pt2, style, width) {
    let w = pt2[0] - pt1[0]
    let h = pt2[1] - pt1[1]
    context.lineWidth = width;
    context.strokeStyle = style;
    context.strokeRect(pt1[0], pt1[1], w, h);
}

function drawCanvas(context) {
    let image = new Image();
    image.src = "data:image/png;base64," + imageBase64;
    image.onload = function () {
        context.drawImage(image, 0, 0);
        if (XAxis.length > 0) {
            drawLines(context, XAxis, 3, 'rgb(255, 0, 0)');
        }
        if (YAxis.length > 0) {
            drawLines(context, YAxis, 3, 'rgb(0, 255, 0)');
        }
        for (let key in plotData) {
            drawLines(context, plotData[key], 3, 'rgb(0, 0, 255)');
            let last = plotData[key].slice(-1)[0];
            context.font = '32px Roboto medium';
            context.fillStyle = 'rgb(0, 0, 255)';
            context.fillText(key, last[0] + 10, last[1]);
        }
    }
}

function drawSelection(context, mouse, target) {
    let pts = JSON.parse(JSON.stringify(mouse.pts));
    pts.push([mouse.x, mouse.y]);
    if (target.selectedIndex == 1) {
        drawLines(context, pts, 3, 'rgb(255, 0, 0');
    }
    else if (target.selectedIndex == 2) {
        drawLines(context, pts, 3, 'rgb(0, 255, 0');
    }
    else if (target.selectedIndex == 3) {
        drawLines(context, pts, 3, 'rgb(0, 0, 255');
    }
    else if (target.selectedIndex == 4) {
        drawRectangle(context, pts[0], pts[1], 'rgb(255, 0, 255)', 1);
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

function deletePlot(mouse) {
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
    let region = [sx, sy, ex, ey];
    let deletekey = [];
    for (let key in plotData) {
        let plot = plotData[key];
        let j;
        for (j = 0; j < plot.length; j++) {
            if (!checkPoint(region, plot[j])) {
                break;
            }
        }
        if (j == plot.length) {
            deletekey.push(key);
        }
    }
    for (let i = 0; i < deletekey.length; i++) {
        delete plotData[deletekey[i]];
    }
}

function updateAPI() {
    const xhr = new XMLHttpRequest();
    xhr.open("PATCH", apiupdateURL);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrfToken);
    let axisData = {
        'XAxis': XAxis,
        'YAxis': YAxis,
        'X1': parseFloat(document.getElementById('X1').value),
        'X2': parseFloat(document.getElementById('X2').value),
        'Y1': parseFloat(document.getElementById('Y1').value),
        'Y2': parseFloat(document.getElementById('Y2').value),
        'XTitle': document.getElementById('XTitle').value,
        'YTitle': document.getElementById('YTitle').value
    };
    let data = {
        'axis': axisData,
        'plot': plotData,
    };
    let json = JSON.stringify({
        'data': JSON.stringify(data)
    });
    xhr.send(json);
    xhr.onload = function () {
        location.href = detailURL;
    };
}

function init() {
    const target = document.getElementById("selectTarget");
    let canvas = document.getElementById('canvas');
    let context = canvas.getContext('2d');
    if (srcData.plot) {
        plotData = srcData.plot;
    }
    if (srcData.axis) {
        XAxis = srcData.axis.XAxis;
        YAxis = srcData.axis.YAxis;
        document.getElementById('X1').value = srcData.axis.X1;
        document.getElementById('X2').value = srcData.axis.X2;
        document.getElementById('Y1').value = srcData.axis.Y1;
        document.getElementById('Y2').value = srcData.axis.Y2;
        document.getElementById('XTitle').value = srcData.axis.XTitle;
        document.getElementById('YTitle').value = srcData.axis.YTitle;
    }
    drawCanvas(context);
    let fcanvas = document.getElementById('canvas_front');
    let fcontext = fcanvas.getContext('2d');
    let mouse = {
        pts: [],
        x: 0,
        y: 0,
        isOn: false
    };
    fcanvas.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX - canvas_front.getBoundingClientRect().left;
        mouse.y = e.clientY - canvas_front.getBoundingClientRect().top;
        if (mouse.isOn) {
            fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
            drawSelection(fcontext, mouse, target);
        }
    });
    fcanvas.addEventListener("mousedown", function (e) {
        if (mouse.isOn) {
            mouse.pts.push([mouse.x, mouse.y]);
            if (target.selectedIndex == 1 && mouse.pts.length == 2) {
                mouse.pts[1][1] = mouse.pts[0][1];
                XAxis = mouse.pts;
                mouse.isOn = false;
                mouse.pts = [];
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context);
            } else if (target.selectedIndex == 2 && mouse.pts.length == 2) {
                mouse.pts[1][0] = mouse.pts[0][0];
                YAxis = mouse.pts;
                mouse.isOn = false;
                mouse.pts = [];
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context);
            } else if (target.selectedIndex == 4 && mouse.pts.length == 2) {
                mouse.pts.push([mouse.x, mouse.y]);
                deletePlot(mouse);
                mouse.isOn = false;
                mouse.pts = [];
                fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
                drawCanvas(context);
            }
        } else {
            if (target.selectedIndex > 0) {
                mouse.pts.push([mouse.x, mouse.y]);
                mouse.isOn = true;
            }
        }
    });
    document.addEventListener('keydown', function (e) {
        if (target.selectedIndex >= 3 && e.key === 'Escape') {
            let name = document.getElementById('PlotName').value;
            plotData[name] = mouse.pts;
            mouse.isOn = false;
            mouse.pts = []
            fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
            drawCanvas(context);
        }
    });
    document.getElementById('buttonSave').addEventListener('click', () => {
        updateAPI();
    });
}
window.onload = init;
