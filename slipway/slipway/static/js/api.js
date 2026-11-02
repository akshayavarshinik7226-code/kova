/* Minimal API client. Keeps the CSRF token in memory and attaches it to writes. */
window.Api = (function () {
  let csrf = "";
  async function request(method, path, body) {
    const headers = { Accept: "application/json" };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (method !== "GET") headers["X-CSRF-Token"] = csrf;
    const res = await fetch(path, {
      method, headers, credentials: "same-origin",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    let data = {};
    try { data = await res.json(); } catch (_) { /* non-JSON error */ }
    if (data.csrf) csrf = data.csrf;
    if (!res.ok) {
      const err = new Error(data.error || "Something went wrong. Try again.");
      err.status = res.status;
      throw err;
    }
    return data;
  }
  return {
    get: (p) => request("GET", p),
    post: (p, b) => request("POST", p, b === undefined ? {} : b),
    init: () => request("GET", "/api/auth/me"),
  };
})();
