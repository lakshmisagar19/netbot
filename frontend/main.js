// When the "Search" button is clicked
document.getElementById("send-btn").addEventListener("click", function() {
    const questionInput = document.getElementById("chat-input");
    const question = questionInput.value.trim();
    if (!question) return;
    
    addChatMessage("You: " + question);
    questionInput.value = "";
    
    // Call the backend chat API using your provided backend URL
    fetch("https://chatbot-backend-1.azurewebsites.net/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
      if (data.answer) {
        addChatMessage("Bot: " + data.answer);
        addHistoryItem(question, data.answer);
      } else {
        addChatMessage("Error: " + data.error);
      }
    })
    .catch(error => {
      addChatMessage("Error: " + error);
    });
  });
  
  // Append a message to the chat box
  function addChatMessage(message) {
    const chatBox = document.getElementById("chat-box");
    const messageElem = document.createElement("p");
    messageElem.innerText = message;
    chatBox.appendChild(messageElem);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  
  // Add an item to the chat history sidebar
  function addHistoryItem(question, answer) {
    const historyList = document.getElementById("chat-history");
    const item = document.createElement("li");
    item.innerText = question;
    historyList.appendChild(item);
  }
  
  // Optionally, load existing chat history on page load
  window.onload = function() {
    fetch("https://chatbot-backend-1.azurewebsites.net/api/history")
      .then(response => response.json())
      .then(data => {
        const historyList = document.getElementById("chat-history");
        data.forEach(item => {
          const li = document.createElement("li");
          li.innerText = item.question;
          historyList.appendChild(li);
        });
      });
  };
  