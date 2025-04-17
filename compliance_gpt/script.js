document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("sendBtn");
    const input = document.getElementById("userInput");
    const chatLog = document.getElementById("chat-log");
  
    function appendMessage(sender, text) {
      const p = document.createElement("p");
      p.innerHTML = `<strong>${sender}:</strong> ${text}`;
      chatLog.appendChild(p);
      chatLog.scrollTop = chatLog.scrollHeight;
    }
  
    async function askQuestion() {
      const question = input.value.trim();
      if (!question) return;
  
      appendMessage("You", question);
      input.value = "";
  
      try {
        const res = await fetch("https://aiqubed-io.onrender.com/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });
  
        if (!res.ok) {
          appendMessage("ComplianceGPT", "Sorry, something went wrong.");
          return;
        }
  
        const data = await res.json();
        appendMessage("ComplianceGPT", data.answer);
      } catch (err) {
        console.error("Error:", err);
        appendMessage("ComplianceGPT", "Server error. Please try again later.");
      }
    }
  
    sendBtn.addEventListener("click", askQuestion);
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") askQuestion();
    });
  });
  
