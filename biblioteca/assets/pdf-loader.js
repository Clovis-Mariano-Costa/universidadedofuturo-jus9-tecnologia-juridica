(() => {
  async function openPdf(button) {
    const original = button.textContent;
    button.disabled = true;
    button.textContent = "Preparando PDF…";
    try {
      const packUrl = button.dataset.pdfPack;
      const cache = openPdf.packCache || (openPdf.packCache = new Map());
      let pack = cache.get(packUrl);
      if (!pack) {
        const response = await fetch(packUrl, { cache: "force-cache" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        pack = await response.json();
        cache.set(packUrl, pack);
      }
      const encoded = pack[button.dataset.pdfKey];
      if (!encoded) throw new Error("PDF ausente do pacote público");
      const binary = atob(encoded);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      const url = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" }));
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (!opened) {
        const link = document.createElement("a");
        link.href = url;
        link.download = button.dataset.pdfName || "obra.pdf";
        link.click();
      }
      setTimeout(() => URL.revokeObjectURL(url), 120000);
    } catch (error) {
      console.error(error);
      alert("Não foi possível abrir o PDF. Tente novamente ou informe a Biblioteca.");
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }
  document.querySelectorAll("[data-pdf-pack]").forEach((button) => {
    button.addEventListener("click", () => openPdf(button));
  });
})();
