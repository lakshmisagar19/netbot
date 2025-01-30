document.getElementById("search-button").addEventListener("click", async () => {
    const input = document.getElementById("chat-input").value;
    if (!input) return;

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
    });

    const data = await response.json();
    document.getElementById("chat-response").innerText = data.answer;

    // Save question and answer in the right panel
    const questionList = document.getElementById("previous-questions");
    const newItem = document.createElement("li");
    newItem.innerText = input;
    questionList.appendChild(newItem);
});

async function sendMessage() {
    let userMessage = document.getElementById("user-input").value;
    if (!userMessage) return;

    let chatbox = document.getElementById("chatbox");

    // Show loading message
    chatbox.innerHTML += `<p><em>Loading...</em></p>`;

    let response = await fetch("https://chatbot-backend.azurewebsites.net/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    });

    let data = await response.json();

    // Remove loading message and show response
    chatbox.innerHTML = chatbox.innerHTML.replace(`<p><em>Loading...</em></p>`, "");
    chatbox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;
    chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;

    // Store chat history in local storage
    let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
    chatHistory.push({ user: userMessage, bot: data.response });
    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
}

// Load chat history on page load
window.onload = function () {
    let chatbox = document.getElementById("chatbox");
    let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];

    chatHistory.forEach(chat => {
        chatbox.innerHTML += `<p><strong>You:</strong> ${chat.user}</p>`;
        chatbox.innerHTML += `<p><strong>Bot:</strong> ${chat.bot}</p>`;
    });
};

// Allow sending messages with Enter key
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
