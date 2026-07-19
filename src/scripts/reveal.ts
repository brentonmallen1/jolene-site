// Adds .in-view to [data-reveal] elements as they enter the viewport.
const els = document.querySelectorAll("[data-reveal]");
if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
  els.forEach((el) => el.classList.add("in-view"));
} else {
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add("in-view");
          io.unobserve(e.target);
        }
      }
    },
    { rootMargin: "0px 0px 50% 0px" }
  );
  els.forEach((el) => io.observe(el));
}
