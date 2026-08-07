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

  function injectCharlieDeltaMvpSpecialization() {
    const path = location.pathname.replace(/\/+$/, "/");
    if (!path.endsWith("/biblioteca/estudantes/charlie-delta-da-costa/")) return;

    const article = document.querySelector("main.doc article");
    if (!article || document.getElementById("mvp-tecno-juridico-2026")) return;

    const heading = Array.from(article.querySelectorAll("h2")).find((el) =>
      el.textContent.includes("Dossiê e obras acadêmicas")
    );
    const grid = heading && heading.nextElementSibling;
    if (!grid || !grid.classList.contains("grid")) return;

    const card = document.createElement("article");
    card.className = "card";
    card.id = "mvp-tecno-juridico-2026";
    card.innerHTML = `
      <span class="badge">PROJETO APROVADO COM MÉRITO · 8,9/10 · TCC PENDENTE</span>
      <h3>Arquitetura e Governança de MVPs Tecno-Jurídicos</h3>
      <p><strong>Núcleo comum, missões distintas:</strong> arquitetura de linha de produtos para o MVP Advogado e o MVP Defensoria Pública, com transferência aos MVPs da Jus 9 Tecnologia Jurídica e formação de Charlie Echo da Costa.</p>
      <p>O projeto V1.0 está aprovado para execução controlada. O TCC permanece em rascunho, sem banca e sem homologação; a colação interna está apenas protocolizada e pendente.</p>
      <p>
        <a class="btn primary" href="https://drive.google.com/file/d/1sZYPlFz2Bo_R3og-rBDh7vSYJYEAOFSo/view?usp=drivesdk" target="_blank" rel="noopener noreferrer">Abrir PDF</a>
        <a class="btn" href="obras/PROJETO_APROVADO_ESPECIALIZACAO_MVP_TECNO_JURIDICO_V1_0_PUBLICO.md">Ler versão pública</a>
        <a class="btn" href="protocolos/PROTOCOLO_COLACAO_GRAU_MVP_TECNO_JURIDICO_V0_1.md">Colação: protocolo pendente</a>
      </p>`;

    grid.prepend(card);
  }

  injectCharlieDeltaMvpSpecialization();
})();
