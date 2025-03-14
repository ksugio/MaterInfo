function RGBStyle(rgb) {
    return 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')'
}

function drawLine(context, pt1, pt2, style, width) {
    context.lineWidth = width;
    context.strokeStyle = style;
    context.beginPath();
    context.moveTo(pt1[0], pt1[1]);
    context.lineTo(pt2[0], pt2[1]);
    context.stroke();
}

function drawArrow(context, pt1, pt2, style, width) {
    context.lineWidth = width;
    context.strokeStyle = style;
    let vx = 0.1 * (pt2[0] - pt1[0]);
    let vy = 0.1 * (pt2[1] - pt1[1]);
    let vx1 = 0.5 * (-Math.sqrt(2) * vx - Math.sqrt(2) * vy);
    let vy1 = 0.5 * (Math.sqrt(2) * vx - Math.sqrt(2) * vy);
    let vx2 = 0.5 * (-Math.sqrt(2) * vx + Math.sqrt(2) * vy);
    let vy2 = 0.5 * (-Math.sqrt(2) * vx - Math.sqrt(2) * vy);
    context.beginPath();
    context.moveTo(pt1[0], pt1[1]);
    context.lineTo(pt2[0], pt2[1]);
    context.lineTo(pt2[0] + vx1, pt2[1] + vy1);
    context.stroke();
    context.beginPath();
    context.moveTo(pt2[0], pt2[1]);
    context.lineTo(pt2[0] + vx2, pt2[1] + vy2);
    context.stroke();
}

function drawRectangle(context, pt1, pt2, style, width) {
    let w = pt2[0] - pt1[0]
    let h = pt2[1] - pt1[1]
    if (width > 0) {
        context.lineWidth = width;
        context.strokeStyle = style;
        context.strokeRect(pt1[0], pt1[1], w, h);
    }
    else {
        context.fillStyle = style;
        context.fillRect(pt1[0], pt1[1], w, h);
    }
}

function drawCircle(context, pt1, radius, style, width) {
    if (width > 0) {
        context.lineWidth = width;
        context.strokeStyle = style;
        context.beginPath();
        context.arc(pt1[0], pt1[1], radius, 0, Math.PI * 2);
        context.stroke();
    }
    else {
        context.fillStyle = style;
        context.beginPath();
        context.arc(pt1[0], pt1[1], radius, 0, Math.PI * 2);
        context.fill();
    }
}

function drawShapes(context) {
    for (let i = 0; i < drawData.length; i++) {
        let draw = drawData[i];
        if (draw.type == 'line') {
            drawLine(context, draw.pt1, draw.pt2, RGBStyle(draw.color), draw.thickness);
        }
        else if (draw.type == 'arrow') {
            drawArrow(context, draw.pt1, draw.pt2, RGBStyle(draw.color), draw.thickness);
        }
        else if (draw.type == 'rectangle') {
            drawRectangle(context, draw.pt1, draw.pt2, RGBStyle(draw.color), draw.thickness);
        }
        else if (draw.type == 'circle') {
            drawCircle(context, draw.pt1, draw.radius, RGBStyle(draw.color), draw.thickness);
        }
    }
}

function drawCanvas(canvas, context) {
    let back = document.getElementById('selectBackground')
    if (back.selectedIndex == 0) {
        let image = new Image();
        image.src = "data:image/png;base64," + imageBase64;
        image.onload = function() {
            context.drawImage(image, 0, 0);
            drawShapes(context);
        }
    }
    else {
        if (back.selectedIndex == 1) {
            context.fillStyle = 'rgb(255, 255, 255)';
        }
        else if (back.selectedIndex == 2) {
            context.fillStyle = 'rgb(128, 128, 128)';
        }
        else if (back.selectedIndex == 3) {
            context.fillStyle = 'rgb(0, 0, 0)';
        }
        context.beginPath();
        context.fillRect(0, 0, canvas.width, canvas.height);
        drawShapes(context);
    }
}

function calcRadius(mouse) {
    let dx = mouse.x - mouse.startX;
    let dy = mouse.y - mouse.startY;
    let radius = Math.sqrt(dx * dx + dy * dy) / imageRatio;
    return Math.round(radius);
}

function ScalePt(pt) {
    return [pt[0] / imageRatio, pt[1] / imageRatio];
}

function drawSelection(context, mouse) {
    const shape = document.getElementById("selectShape");
    const color = document.getElementById("selectColor");
    const thickness = document.getElementById("Thickness");
    const angle = document.getElementById("Angle");
    if (thickness.value > 0) {
        line_width = thickness.value;
    }
    else {
        line_width = 1;
    }
    if (shape.selectedIndex == 0) {
        drawLine(context, ScalePt([mouse.startX, mouse.startY]), ScalePt([mouse.x, mouse.y]), color.value, line_width);
    }
    else if (shape.selectedIndex == 1) {
        drawArrow(context, ScalePt([mouse.startX, mouse.startY]), ScalePt([mouse.x, mouse.y]), color.value, line_width);
    }
    else if (shape.selectedIndex == 2) {
        drawRectangle(context, ScalePt([mouse.startX, mouse.startY]), ScalePt([mouse.x, mouse.y]), color.value, line_width);
    }
    else if (shape.selectedIndex == 3) {
        drawCircle(context, ScalePt([mouse.startX, mouse.startY]), calcRadius(mouse), color.value, line_width);
    }
    else if (shape.selectedIndex == 4) {
        drawRectangle(context, ScalePt([mouse.startX, mouse.startY]), ScalePt([mouse.x, mouse.y]), 'rgb(255, 255, 255)', 1);
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

function deleteShape(mouse) {
    let sx, sy, ex, ey;
    if (mouse.x > mouse.startX) {
        sx = mouse.startX;
        ex = mouse.x;
    }
    else {
        sx = mouse.x;
        ex = mouse.startX;
    }
    if (mouse.y > mouse.startY) {
        sy = mouse.startY;
        ey = mouse.y;
    }
    else {
        sy = mouse.y;
        ey = mouse.startY;
    }
    let region = [sx / imageRatio, sy / imageRatio, ex / imageRatio, ey / imageRatio];
    let deleteid = [];
    for (let i = 0; i < drawData.length; i++) {
        let draw = drawData[i];
        if (draw.type == 'line') {
            if (checkPoint(region, draw.pt1) && checkPoint(region, draw.pt2)) {
                deleteid.push(i);
            }
        }
        else if (draw.type == 'arrow') {
            if (checkPoint(region, draw.pt1) && checkPoint(region, draw.pt2)) {
                deleteid.push(i);
            }
        }
        else if (draw.type == 'rectangle') {
            if (checkPoint(region, draw.pt1) && checkPoint(region, draw.pt2)) {
                deleteid.push(i);
            }
        }
        else if (draw.type == 'circle') {
            let pt1 = [draw.pt1[0] - draw.radius, draw.pt1[1] - draw.radius];
            let pt2 = [draw.pt1[0] + draw.radius, draw.pt1[1] + draw.radius];
            if (checkPoint(region, pt1) && checkPoint(region, pt2)) {
                deleteid.push(i);
            }
        }
    }
    for (let i = deleteid.length - 1; i >= 0; i--) {
        drawData.splice(deleteid[i], 1);
    }
}

function addShape(canvas, context, mouse) {
    const shape = document.getElementById("selectShape");
    const color = document.getElementById("selectColor");
    let red   = parseInt(color.value.substring(1,3), 16);
    let green = parseInt(color.value.substring(3,5), 16);
    let blue  = parseInt(color.value.substring(5,7), 16);
    const thickness = parseInt(document.getElementById("Thickness").value);
    let pt1x = Math.round(mouse.startX / imageRatio);
    let pt1y = Math.round(mouse.startY / imageRatio);
    let pt2x = Math.round(mouse.x / imageRatio);
    let pt2y = Math.round(mouse.y / imageRatio);
    if (shape.selectedIndex == 0) {
        newline = {
            "type": "line",
            "pt1": [pt1x, pt1y],
            "pt2": [pt2x, pt2y],
            "color": [red, green, blue],
            "thickness": thickness
        }
        drawData.push(newline);
    }
    else if (shape.selectedIndex == 1) {
        newarrow = {
            "type": "arrow",
            "pt1": [pt1x, pt1y],
            "pt2": [pt2x, pt2y],
            "color": [red, green, blue],
            "thickness": thickness
        }
        drawData.push(newarrow);
    }
    else if (shape.selectedIndex == 2) {
        newrect = {
            "type": "rectangle",
            "pt1": [pt1x, pt1y],
            "pt2": [pt2x, pt2y],
            "color": [red, green, blue],
            "thickness": thickness
        }
        drawData.push(newrect);
    }
    else if (shape.selectedIndex == 3) {
        newcircle = {
            "type": "circle",
            "pt1": [pt1x, pt1y],
            "radius": calcRadius(mouse),
            "color": [red, green, blue],
            "thickness": thickness
        }
        drawData.push(newcircle);
    }
    else if (shape.selectedIndex == 4) {
        deleteShape(mouse);
    }
    drawCanvas(canvas, context);
}

function init() {
    document.getElementById('Zoom').value = 100;
    document.getElementById('ZoomValue').innerText = 100;
    let canvas = document.getElementById('canvas');
    let context = canvas.getContext('2d');
    drawCanvas(canvas, context);
    let fcanvas = document.getElementById('canvas_front');
    let fcontext = fcanvas.getContext('2d');
    let mouse = {
        startX: 0,
        startY: 0,
        x: 0,
        y: 0,
        isDown: false
    };
    fcanvas.addEventListener("mousemove", function(e) {
        mouse.x = e.clientX - canvas_front.getBoundingClientRect().left;
        mouse.y = e.clientY - canvas_front.getBoundingClientRect().top;
        if (mouse.isDown) {
            fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
            drawSelection(fcontext, mouse);
        }
    });
    fcanvas.addEventListener("mousedown", function(e){
        mouse.isDown = true;
        mouse.startX = mouse.x;
        mouse.startY = mouse.y;
    });
    fcanvas.addEventListener("mouseup", function(e){
        mouse.isDown = false;
        fcontext.clearRect(0, 0, fcanvas.width, fcanvas.height);
        addShape(canvas, context, mouse);
    });
    document.getElementById('buttonPop').addEventListener('click', () => {
        drawData.pop();
        drawCanvas(canvas, context);
    });
    document.getElementById('selectBackground').addEventListener('change', () => {
        drawCanvas(canvas, context);
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
        xhr.open("PUT", apiupdateURL);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("X-CSRFToken", csrfToken);
        const order = parseInt(document.getElementById("Order").value);
        let json = JSON.stringify({
            'name': 'Draw',
            'order': order,
            'data': JSON.stringify(drawData, null, ' ')
        });
        xhr.send(json);
    });
}
window.onload = init;
