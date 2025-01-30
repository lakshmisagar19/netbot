document.getElementById("search-button").addEventListener("click", async () => {
    const input = document.getElementById("chat-input").value.trim();
    if (!input) return;

    const BACKEND_URL = "https://chatbot-backend-1.azurewebsites.net"; // Backend URL

    try {
        const response = await fetch(`${BACKEND_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question: input }),
            mode: "cors",  // Ensure CORS mode is enabled
            credentials: "include", // Allow credentials if needed
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(`Server Error: ${data.error}`);
        }

        document.getElementById("chat-response").innerText = data.answer;

        // Save question and answer in the right panel
        const questionList = document.getElementById("previous-questions");
        const newItem = document.createElement("li");
        newItem.innerText = input;
        questionList.appendChild(newItem);
    } catch (error) {
        console.error("Fetch Error:", error);
        document.getElementById("chat-response").innerText = "An error occurred. Please try again.";
    }
});
