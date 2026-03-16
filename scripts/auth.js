const apiBase = "http://localhost:8000";

function getInputValue(selector) {
  const el = document.querySelector(selector);
  return el ? el.value : "";
}

async function signupHandler() {
  const username = getInputValue('.form-wrapper input[placeholder="Username"]');
  const email = getInputValue('.form-wrapper input[placeholder="Email"]');
  const password = getInputValue('.form-wrapper input[placeholder="Password"]');
  const dob = document.querySelector(".dob-field")?.value;
  if (!username || !email || !password || !dob) return;
  const body = {
    username,
    email,
    password,
    date_of_birth: dob,
  };
  const res = await fetch(apiBase + "/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) return;
  const data = await res.json();
  localStorage.setItem("sb_email", email);
  localStorage.setItem("sb_token", data.token || "");
  window.location.href = "verification_code.html";
}

async function sendCodeHandler() {
  const email = localStorage.getItem("sb_email");
  if (!email) return;
  await fetch(apiBase + "/auth/send-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
}

async function verifyCodeHandler() {
  const email = localStorage.getItem("sb_email");
  const codeInput = document.querySelector(".code-input");
  if (!email || !codeInput || !codeInput.value) return;
  const res = await fetch(apiBase + "/auth/verify-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, code: codeInput.value }),
  });
  if (!res.ok) return;
  const data = await res.json();
  if (data.token) localStorage.setItem("sb_token", data.token);
  window.location.href = "../dashboard.html";
}

async function loginHandler(emailSelector, passwordSelector) {
  const email = getInputValue(emailSelector);
  const password = getInputValue(passwordSelector);
  if (!email || !password) return;
  const res = await fetch(apiBase + "/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) return;
  const data = await res.json();
  if (data.token) {
    localStorage.setItem("sb_email", email);
    localStorage.setItem("sb_token", data.token);
    window.location.href = "../dashboard.html";
  }
}

async function loadMe() {
  const token = localStorage.getItem("sb_token");
  if (!token) return;
  const res = await fetch(apiBase + "/auth/me", {
    headers: { Authorization: "Bearer " + token },
  });
  if (!res.ok) return;
  const data = await res.json();
  console.log("Current user:", data);
}

document.addEventListener("DOMContentLoaded", () => {
  const signUpNext = document.querySelector(".next-btn");
  if (signUpNext) {
    signUpNext.addEventListener("click", (e) => {
      e.preventDefault();
      signupHandler();
    });
  }
  const sendBtn = document.querySelector(".send-btn");
  if (sendBtn) {
    sendBtn.addEventListener("click", (e) => {
      e.preventDefault();
      sendCodeHandler();
    });
  }
  const confirmBtn = document.querySelector(".confirm-btn");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", (e) => {
      e.preventDefault();
      verifyCodeHandler();
    });
  }
});
