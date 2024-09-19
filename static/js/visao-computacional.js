const URL = "/static/models/my_model/";
let model, webcam, ctx, labelContainer, maxPredictions;

async function init() {
    const modelURL = URL + "model.json";
    const metadataURL = URL + "metadata.json";

    model = await tmPose.load(modelURL, metadataURL);
    maxPredictions = model.getTotalClasses();

    const size = 400;
    const flip = true;
    webcam = new tmPose.Webcam(size, size, flip);
    await webcam.setup();
    await webcam.play();
    window.requestAnimationFrame(loop);

    const canvas = document.getElementById("canvas");
    canvas.width = size;
    canvas.height = size;
    ctx = canvas.getContext("2d");

    labelContainer = document.getElementById("progress-container");
    
    // Títulos das classes na ordem correta
    const classNames = ["Mão na cabeça", "Mão no queixo", "Duas mãos na cabeça", "Braços cruzados"];

    for (let i = 0; i < maxPredictions; i++) {
        // Criação do título da classe com a porcentagem
        const classTitle = document.createElement("div");
        classTitle.className = "progress-title";
        classTitle.innerText = `${classNames[i]}: 0%`;

        // Criação do container da barra de progresso
        const barContainer = document.createElement("div");
        barContainer.className = "progress-bar";

        const barFill = document.createElement("div");
        barFill.className = "progress-bar-fill";
        barContainer.appendChild(barFill);

        // Adicionando o título e a barra de progresso ao contêiner principal
        labelContainer.appendChild(classTitle);
        labelContainer.appendChild(barContainer);
    }

    document.getElementById("start-button").style.display = "none";
}

async function loop(timestamp) {
    webcam.update();
    await predict();
    window.requestAnimationFrame(loop);
}

async function predict() {
    const { pose, posenetOutput } = await model.estimatePose(webcam.canvas);
    const prediction = await model.predict(posenetOutput);

    for (let i = 0; i < maxPredictions; i++) {
        const probability = (prediction[i].probability.toFixed(2) * 100).toFixed(0) + "%";
        const barFill = document.getElementsByClassName("progress-bar-fill")[i];
        barFill.style.width = probability;

        const classTitle = document.getElementsByClassName("progress-title")[i];
        classTitle.innerText = `${prediction[i].className}: ${probability}`;
    }

    drawPose(pose);
}

function drawPose(pose) {
    if (webcam.canvas) {
        ctx.drawImage(webcam.canvas, 0, 0);
        if (pose) {
            const minPartConfidence = 0.5;
            tmPose.drawKeypoints(pose.keypoints, minPartConfidence, ctx);
            tmPose.drawSkeleton(pose.keypoints, minPartConfidence, ctx);
        }
    }
}

async function loadModel() {
    const model = await tf.loadGraphModel('/vision_model/model.json');
    // Agora você pode utilizar o modelo para inferência
}

loadModel();