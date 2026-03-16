const apiBase = "https://scriptbox.onrender.com"; 

async function googleOAuth(idToken) {
  const res = await fetch(apiBase + "/auth/oauth/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  if (!res.ok) {
    alert("Google login failed");
    return;
  }

  const data = await res.json();
  localStorage.setItem("sb_token", data.token);
  window.location.href = "../dashboard.html";
}

document.addEventListener("DOMContentLoaded", () => {
  const googleBtn = document.querySelector(".google");

  if (googleBtn) {
    googleBtn.addEventListener("click", () => {
      google.accounts.id.initialize({
        client_id: "484573911641-vepujquvvl229otcchk9k486dqgoj4bc.apps.googleusercontent.com",
        callback: (response) => googleOAuth(response.credential),
      });

      google.accounts.id.prompt();
    });
  }
});
