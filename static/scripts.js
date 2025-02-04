document.addEventListener("DOMContentLoaded", function() {
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const chatDisplay = document.getElementById("chat-display");

  sendBtn.addEventListener("click", sendQuestion);
  
  // Optionally allow pressing Enter to send the question
  chatInput.addEventListener("keypress", function(e) {
    if (e.key === 'Enter') {
      sendQuestion();
    }
  });
  
  function sendQuestion() {
    const question = chatInput.value.trim();
    if (!question) return;
    
    // Append user's question to chat display
    const userDiv = document.createElement("div");
    userDiv.textContent = "You: " + question;
    chatDisplay.appendChild(userDiv);
    
    // Clear input
    chatInput.value = "";
    
    // Send AJAX request to backend /chat endpoint
    fetch("https://chatbot-backend-1.azurewebsites.net/chat", {  // Use your backend Azure Web App URL here
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({question: question})
    })
    .then(response => response.json())
    .then(data => {
      const botDiv = document.createElement("div");
      botDiv.textContent = "Bot: " + data.answer;
      chatDisplay.appendChild(botDiv);
      
      // Optionally, scroll to the bottom of chatDisplay
      chatDisplay.scrollTop = chatDisplay.scrollHeight;
    })
    .catch(error => {
      console.error("Error:", error);
    });
  }
});
