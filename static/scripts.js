document.getElementById("search-button").addEventListener("click", async () => {
    const input = document.getElementById("chat-input").value;
    if (!input) return;

    // Use full backend URL for the fetch request
    const BACKEND_URL = "https://chatbot-backend-1.azurewebsites.net"; // Correct backend URL
    const response = await fetch(`${BACKEND_URL}/ask`, {  // Use backend URL and endpoint
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
    });

    if (!response.ok) {
        console.error("Error:", response.statusText);
        return;
    }

    const data = await response.json();
    document.getElementById("chat-response").innerText = data.answer;

    // Save question and answer in the right panel
    const questionList = document.getElementById("previous-questions");
    const newItem = document.createElement("li");
    newItem.innerText = input;
    questionList.appendChild(newItem);
});
