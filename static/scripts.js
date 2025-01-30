const BACKEND_URL = "https://chatbot-backend-1.azurewebsites.net"; // Ensure this is correct

document.addEventListener("DOMContentLoaded", () => {
    const chatbox = document.getElementById("chatbox");
    const chatInput = document.getElementById("chat-input");
    const userInput = document.getElementById("user-input");
    const searchButton = document.getElementById("search-button");

    // Load chat history on page load
    let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
    chatHistory.forEach(chat => {
        chatbox.innerHTML += `<p><strong>You:</strong> ${chat.user}</p>`;
        chatbox.innerHTML += `<p><strong>Bot:</strong> ${chat.bot}</p>`;
    });

    // Handle search button click
    if (searchButton) {
        searchButton.addEventListener("click", async () => {
            const input = chatInput.value.trim();
            if (!input) return;

            const response = await fetch(`${BACKEND_URL}/ask`, {
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
    }

    // Send message function
    async function sendMessage() {
        let userMessage = userInput.value.trim();
        if (!userMessage) return;

        // Show loading message
        chatbox.innerHTML += `<p><em>Loading...</em></p>`;

        try {
            let response = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage }),
            });

            let data = await response.json();

            // Remove loading message and show response
            chatbox.innerHTML = chatbox.innerHTML.replace(`<p><em>Loading...</em></p>`, "");
            chatbox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;
            chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;

            // Store chat history in local storage
            chatHistory.push({ user: userMessage, bot: data.response });
            localStorage.setItem("chatHistory", JSON.stringify(chatHistory));

            // Clear input field
            userInput.value = "";
        } catch (error) {
            console.error("Error fetching chat response:", error);
            chatbox.innerHTML += `<p><strong>Bot:</strong> Sorry, there was an error.</p>`;
        }
    }

    // Allow sending messages with Enter key
    if (userInput) {
        userInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault(); // Prevent form submission
                sendMessage();
            }
        });
    }
});
