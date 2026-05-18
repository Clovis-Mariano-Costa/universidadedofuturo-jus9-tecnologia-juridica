document.querySelectorAll(".nav a").forEach((link) => {
  const current = location.pathname.split("/").pop() || "index.html";
  if (link.getAttribute("href") === current) link.classList.add("active");
});
