document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("image-input");
    const previewImage = document.getElementById("preview-image");
    const previewMessage = document.getElementById("preview-message");
    const removeButton = document.getElementById("remove-image");
    const analyzeButton = document.getElementById("analyze-button");
    const loadImageLabel = document.getElementById("load-image-label");
    const analysisForm = document.getElementById("analysis-form");
    const resultContent = document.getElementById("result-content");
    const resultBox = document.querySelector(".result-box");

    const fileName = document.getElementById("file-name");
    const fileType = document.getElementById("file-type");
    const fileSize = document.getElementById("file-size");

    if (
        !imageInput ||
        !previewImage ||
        !removeButton ||
        !analyzeButton
    ) {
        return;
    }

    const allowedTypes = [
        "image/jpeg",
        "image/png"
    ];

    const maxSize = 5 * 1024 * 1024;

    const hasServerResult =
        resultBox &&
        (
            resultBox.classList.contains("result-active-normal") ||
            resultBox.classList.contains("result-active-pneumonia") ||
            resultBox.classList.contains("result-active-warning")
        );

    if (!hasServerResult) {
        analyzeButton.disabled = true;
    }

    imageInput.addEventListener("change", function () {
        clearClientError();

        const file = imageInput.files[0];

        if (!file) {
            clearPreview();
            return;
        }

        if (!allowedTypes.includes(file.type)) {
            showClientError(
                "Formato no permitido. Solo se aceptan archivos JPG, JPEG o PNG."
            );
            clearPreview();
            return;
        }

        if (file.size > maxSize) {
            showClientError(
                "La imagen no debe superar los 5 MB."
            );
            clearPreview();
            return;
        }

        const imageUrl = URL.createObjectURL(file);

        previewImage.src = imageUrl;
        previewImage.hidden = false;

        if (previewMessage) {
            previewMessage.hidden = true;
        }

        const sizeInMB = (
            file.size / 1024 / 1024
        ).toFixed(2);

        fileName.innerHTML =
            `<strong>Archivo:</strong> ${file.name}`;

        fileType.innerHTML =
            "<strong>Estado:</strong> Imagen lista para análisis";

        fileSize.innerHTML =
            `<strong>Tamaño:</strong> ${sizeInMB} MB`;

        analyzeButton.disabled = false;
        analyzeButton.textContent = "Ejecutar análisis";

        clearResultBox();
    });

    removeButton.addEventListener("click", function () {
        clearPreview();
        clearClientError();
    });

    if (analysisForm) {
        analysisForm.addEventListener("submit", function (event) {
            if (!imageInput.files.length && !hasServerResult) {
                event.preventDefault();

                showClientError(
                    "Debe seleccionar una imagen antes de ejecutar el análisis."
                );

                return;
            }

            analyzeButton.disabled = true;
            analyzeButton.textContent = "Analizando...";

            imageInput.disabled = true;

            if (loadImageLabel) {
                loadImageLabel.classList.add("btn-disabled");
            }
        });
    }

    window.addEventListener("pageshow", function (event) {
        const navigationEntry =
            performance.getEntriesByType("navigation")[0];

        const restoredFromHistory =
            event.persisted ||
            (
                navigationEntry &&
                navigationEntry.type === "back_forward"
            );

        if (restoredFromHistory) {
            clearPreview();
            clearClientError();
        }
    });

    function clearPreview() {
        imageInput.value = "";
        imageInput.disabled = false;

        if (loadImageLabel) {
            loadImageLabel.classList.remove("btn-disabled");
        }

        previewImage.src = "";
        previewImage.hidden = true;

        if (previewMessage) {
            previewMessage.hidden = false;
        }

        fileName.innerHTML =
            "<strong>Archivo:</strong> Ninguno seleccionado";

        fileType.innerHTML =
            "<strong>Estado:</strong> —";

        fileSize.innerHTML =
            "<strong>Resultado:</strong> —";

        analyzeButton.disabled = true;
        analyzeButton.textContent = "Ejecutar análisis";

        clearResultBox();
    }

    function clearResultBox() {
        if (resultContent) {
            resultContent.innerHTML = `
                <p>
                    Seleccione una radiografía y presione
                    <strong>Ejecutar análisis</strong>.
                </p>
            `;
        }

        if (resultBox) {
            resultBox.classList.remove(
                "result-active",
                "result-active-normal",
                "result-active-pneumonia",
                "result-active-warning"
            );
        }
    }

    function showClientError(message) {
        clearClientError();

        const errorBox = document.createElement("div");
        errorBox.className = "form-error client-error";
        errorBox.innerHTML = `<p>${message}</p>`;

        imageInput.insertAdjacentElement(
            "afterend",
            errorBox
        );
    }

    function clearClientError() {
        const clientError = document.querySelector(
            ".client-error"
        );

        if (clientError) {
            clientError.remove();
        }
    }
});