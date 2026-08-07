document.querySelectorAll(".nav a").forEach((link) => {
  const current = location.pathname.split("/").pop() || "index.html";
  if (link.getAttribute("href") === current) link.classList.add("active");
});

(() => {
  const current = location.pathname.split("/").pop() || "index.html";
  if (current !== "aulas.html") return;

  const grid = document.querySelector("main.doc .grid");
  if (!grid || document.getElementById("estudo-mvp-charlie-echo")) return;

  const section = document.createElement("section");
  section.className = "card";
  section.id = "estudo-mvp-charlie-echo";
  section.innerHTML = `
    <span class="badge">MATERIAL DE ESTUDO · RASCUNHO</span>
    <h3>MVPs tecno-jurídicos: núcleo comum, missões distintas</h3>
    <p>Material pedagógico para Charlie Echo da Costa sobre diferenças entre MVP Advogado e MVP Defensoria Pública, contexto governado, segregação de tenants, limites de competência e revisão humana.</p>
    <p>Derivado de TCC ainda em construção: não é obra final aprovada e não concede titulação.</p>
    <p><a class="btn" href="aulas/materiais/charlie-echo/MATERIAL_ESTUDO_MVP_TECNO_JURIDICO_V0_1.md">Abrir material de estudo</a></p>`;
  grid.append(section);
})();
