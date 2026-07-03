document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("image-input");
    const previewImage = document.getElementById("preview-image");
    const previewMessage = document.getElementById("preview-message");
    const removeButton = document.getElementById("remove-image");
    const analyzeButton = document.getElementById("analyze-button");
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

    const navigationEntry =
    performance.getEntriesByType("navigation")[0];

    if ( navigationEntry &&  navigationEntry.type === "back_forward" )   {
        clearPreview();
        clearClientError();
    }   

    /* */
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

    const allowedTypes = [
        "image/jpeg",
        "image/png"
    ];

    const maxSize = 5 * 1024 * 1024;

    analyzeButton.disabled = true;

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
            `<strong>Tipo:</strong> ${file.type}`;

        fileSize.innerHTML =
            `<strong>Tamaño:</strong> ${sizeInMB} MB`;

        analyzeButton.disabled = false;
    });

    removeButton.addEventListener("click", function () {
        clearPreview();
        clearClientError();
    });

    if (analysisForm) {
        analysisForm.addEventListener("submit", function (event) {
            if (!imageInput.files.length) {
                event.preventDefault();

                showClientError(
                    "Debe seleccionar una imagen antes de ejecutar el análisis."
                );

                return;
            }

            analyzeButton.disabled = true;
            analyzeButton.textContent = "Analizando...";
        });
    }

    function clearPreview() {
    imageInput.value = "";

    previewImage.src = "";
    previewImage.hidden = true;

    if (previewMessage) {
        previewMessage.hidden = false;
    }

    fileName.innerHTML =
        "<strong>Archivo:</strong> Ninguno seleccionado";

    fileType.innerHTML =
        "<strong>Tipo:</strong> —";

    fileSize.innerHTML =
        "<strong>Tamaño:</strong> —";

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Ejecutar análisis";

    if (resultContent) {
        resultContent.innerHTML = `
            <p>
                Seleccione una radiografía y presione
                <strong>Ejecutar análisis</strong>.
            </p>
        `;
    }
    if (resultBox) {
        resultBox.classList.remove("result-active");
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