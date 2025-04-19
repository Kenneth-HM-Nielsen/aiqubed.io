document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("sendBtn");
  const sopBtn = document.getElementById("sopBtn");
  const input = document.getElementById("userInput");
  const chatLog = document.getElementById("chat-log");

  function appendMessage(sender, text) {
    const p = document.createElement("p");
    p.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatLog.appendChild(p);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function appendSources(sourceArray) {
    const list = document.getElementById("sourceList");
    list.innerHTML = ""; // Clear previous sources

    if (!sourceArray || sourceArray.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "No sources available for this response.";
      list.appendChild(empty);
      return;
    }

    sourceArray.forEach((src, index) => {
      const li = document.createElement("li");

      // Create clickable title
      const title = document.createElement("div");
      title.className = "source-title";
      title.textContent = `${src.title}, side ${src.page}`;
      title.style.cursor = "pointer";

      // Create hidden snippet
      const snippet = document.createElement("div");
      snippet.className = "source-snippet";
      snippet.textContent = src.snippet;
      snippet.style.display = "none";
      snippet.style.fontSize = "0.95em";
      snippet.style.marginTop = "0.3em";
      snippet.style.color = "#aaa";

      // Toggle snippet on title click
      title.addEventListener("click", () => {
        snippet.style.display = snippet.style.display === "none" ? "block" : "none";
      });

      li.appendChild(title);
      li.appendChild(snippet);
      list.appendChild(li);
    });
  }

  async function sendToBackend(mode = "chat") {
    const question = input.value.trim();
    if (!question) return;

    appendMessage("You", question);
    input.value = "";

    try {
      const res = await fetch("https://aiqubed-io.onrender.com/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, mode }),
      });

      if (!res.ok) {
        appendMessage("ComplianceGPT", "Sorry, something went wrong.");
        return;
      }

      const data = await res.json();
      appendMessage("ComplianceGPT", data.answer);
      appendSources(data.sources);
    } catch (err) {
      console.error("Error:", err);
      appendMessage("ComplianceGPT", "Server error. Please try again later.");
    }
  }

  sendBtn.addEventListener("click", () => sendToBackend("chat"));
  sopBtn.addEventListener("click", () => sendToBackend("sop"));
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendToBackend("chat");
  });
});
