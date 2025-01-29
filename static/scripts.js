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

