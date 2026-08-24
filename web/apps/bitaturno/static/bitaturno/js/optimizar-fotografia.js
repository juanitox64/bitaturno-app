(() => {
    "use strict";

    const formulario = document.querySelector("[data-form-novedad]");
    const entrada = formulario?.querySelector('input[type="file"][name="fotografia"]');
    const estado = document.getElementById("estado-optimizacion-fotografia");

    if (!formulario || !entrada || !estado) {
        return;
    }

    const maximoOriginal = Number(entrada.dataset.maxOriginalBytes);
    const maximoFinal = Number(entrada.dataset.maxFinalBytes);
    const maximaDimension = Number(entrada.dataset.maxDimension);
    const minimaDimension = 640;
    const calidades = [0.85, 0.82, 0.78, 0.74, 0.70];
    const tiposPermitidos = new Set(["image/jpeg", "image/png", "image/webp"]);
    let procesando = false;

    const formatoMB = (bytes) => `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

    const informar = (mensaje, tipo = "") => {
        estado.textContent = mensaje;
        estado.className = `estado-fotografia ${tipo}`.trim();
    };

    const bloquearEnvio = (bloquear) => {
        formulario.querySelectorAll('button[type="submit"]').forEach((boton) => {
            boton.disabled = bloquear;
        });
    };

    const cargarImagen = async (archivo) => {
        if ("createImageBitmap" in window) {
            try {
                return await createImageBitmap(archivo, { imageOrientation: "from-image" });
            } catch (error) {
                return createImageBitmap(archivo);
            }
        }

        return new Promise((resolver, rechazar) => {
            const imagen = new Image();
            const url = URL.createObjectURL(archivo);
            imagen.onload = () => {
                URL.revokeObjectURL(url);
                resolver(imagen);
            };
            imagen.onerror = () => {
                URL.revokeObjectURL(url);
                rechazar(new Error("No se pudo leer la imagen."));
            };
            imagen.src = url;
        });
    };

    const generarBlob = (canvas, tipo, calidad) =>
        new Promise((resolver) => canvas.toBlob(resolver, tipo, calidad));

    const optimizar = async (archivo) => {
        const imagen = await cargarImagen(archivo);
        const anchoOriginal = imagen.width || imagen.naturalWidth;
        const altoOriginal = imagen.height || imagen.naturalHeight;
        const escalaInicial = Math.min(1, maximaDimension / Math.max(anchoOriginal, altoOriginal));
        let ancho = Math.max(1, Math.round(anchoOriginal * escalaInicial));
        let alto = Math.max(1, Math.round(altoOriginal * escalaInicial));
        let mejorBlob = null;

        while (true) {
            const canvas = document.createElement("canvas");
            canvas.width = ancho;
            canvas.height = alto;
            const contexto = canvas.getContext("2d", { alpha: true });
            contexto.drawImage(imagen, 0, 0, ancho, alto);

            for (const calidad of calidades) {
                let blob = await generarBlob(canvas, "image/webp", calidad);
                if (!blob || blob.type !== "image/webp") {
                    contexto.save();
                    contexto.globalCompositeOperation = "destination-over";
                    contexto.fillStyle = "#ffffff";
                    contexto.fillRect(0, 0, ancho, alto);
                    contexto.restore();
                    blob = await generarBlob(canvas, "image/jpeg", calidad);
                }
                if (blob && (!mejorBlob || blob.size < mejorBlob.size)) {
                    mejorBlob = blob;
                }
                if (blob && blob.size <= maximoFinal) {
                    imagen.close?.();
                    return blob;
                }
            }

            if (Math.max(ancho, alto) <= minimaDimension) {
                imagen.close?.();
                return mejorBlob;
            }
            ancho = Math.max(1, Math.round(ancho * 0.85));
            alto = Math.max(1, Math.round(alto * 0.85));
        }
    };

    entrada.addEventListener("change", async () => {
        entrada.setCustomValidity("");
        informar("");
        const archivo = entrada.files?.[0];
        if (!archivo) {
            return;
        }
        if (archivo.size > maximoOriginal) {
            entrada.value = "";
            entrada.setCustomValidity("La fotografía original no puede superar 25 MB.");
            informar("La fotografía original no puede superar 25 MB.", "error");
            entrada.reportValidity();
            return;
        }
        if (!tiposPermitidos.has(archivo.type)) {
            return;
        }

        procesando = true;
        bloquearEnvio(true);
        informar("Optimizando la fotografía…");

        try {
            const blob = await optimizar(archivo);
            if (!blob) {
                throw new Error("El navegador no generó una imagen optimizada.");
            }
            const extension = blob.type === "image/webp" ? "webp" : "jpg";
            const nombreBase = archivo.name.replace(/\.[^.]+$/, "") || "fotografia";
            const optimizada = new File(
                [blob],
                `${nombreBase}.${extension}`,
                { type: blob.type, lastModified: Date.now() },
            );
            const transferencia = new DataTransfer();
            transferencia.items.add(optimizada);
            entrada.files = transferencia.files;
            informar(
                `Fotografía optimizada: ${formatoMB(archivo.size)} → ${formatoMB(optimizada.size)}.`,
                "exito",
            );
        } catch (error) {
            informar(
                "El navegador no pudo optimizarla; el servidor lo intentará al guardar.",
                "advertencia",
            );
        } finally {
            procesando = false;
            bloquearEnvio(false);
        }
    });

    formulario.addEventListener("submit", (evento) => {
        if (procesando) {
            evento.preventDefault();
            informar("Espere a que termine la optimización de la fotografía.", "advertencia");
        }
    });
})();
