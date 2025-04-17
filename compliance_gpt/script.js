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
    if (!sourceArray || sourceArray.length === 0) return;

    const container = document.createElement("div");
    container.classList.add("sources");

    const title = document.createElement("em");
    title.textContent = "Sources:";
    container.appendChild(title);

    const list = document.createElement("ul");
    sourceArray.forEach(src => {
      const li = document.createElement("li");
      li.textContent = src + "...";
      list.appendChild(li);
    });

    container.appendChild(list);
    chatLog.appendChild(container);
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
