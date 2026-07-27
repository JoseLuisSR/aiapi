/**
 * Small progressive-enhancement helpers for the generation form.
 *
 * Everything here is presentation-only UX (show/hide, enable/disable);
 * the server independently re-validates every field, so nothing here is
 * load-bearing for correctness. Listeners are delegated on `document` so
 * they keep working after HTMX swaps replace parts of the DOM (no manual
 * re-binding needed).
 */

/**
 * `/ui/generate` intentionally returns 400 for validation/provider errors
 * and 500 for internal errors (same semantics as the JSON API), with a
 * real HTML error fragment in the body. htmx 1.9.x only swaps 2xx/3xx
 * responses by default; for 4xx/5xx it fires `htmx:responseError` and
 * leaves the target untouched, so the alert-danger fragment would never
 * reach the DOM. Force the swap to happen regardless of status code so
 * our server-rendered error fragment is always shown; the status code
 * itself is untouched (still 400/500 on the wire).
 */
document.body.addEventListener("htmx:beforeSwap", function (evt) {
  if (evt.detail.xhr.status >= 400) {
    evt.detail.shouldSwap = true;
    evt.detail.isError = false;
  }
});

document.addEventListener("change", function (evt) {
  const target = evt.target;

  // Claude: temperature/top_p are mutually exclusive. Show only the
  // selected control and disable the other so it isn't submitted.
  if (target.matches('input[name="claude_sampling_mode"]')) {
    const form = target.closest("form") || document;
    form.querySelectorAll("[data-sampling-panel]").forEach(function (panel) {
      const isActive = panel.getAttribute("data-sampling-panel") === target.value;
      panel.classList.toggle("d-none", !isActive);
      panel.querySelectorAll("input").forEach(function (input) {
        input.disabled = !isActive;
      });
    });
  }

  // Optional numeric fields (e.g. Claude top_k): a checkbox enables the
  // paired range + number inputs; unchecked means "not sent" (unset).
  if (target.matches("[data-enable-target]")) {
    target
      .getAttribute("data-enable-target")
      .split(",")
      .forEach(function (id) {
        const el = document.getElementById(id.trim());
        if (el) {
          el.disabled = !target.checked;
        }
      });
  }
});
