
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const sendButton = chatForm.querySelector(".send-button");
const suggestionButtons = document.querySelectorAll(".suggestion");

function addMessage(text, sender) {
    const message = document.createElement("div");
    message.className = `message ${sender}-message`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "bot" ? "🐶" : "💚";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const name = document.createElement("span");
    name.className = "message-name";
    name.textContent = sender === "bot" ? "PawPal" : "You";

    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    bubble.appendChild(name);
    bubble.appendChild(paragraph);
    message.appendChild(avatar);
    message.appendChild(bubble);

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typing = document.createElement("div");
    typing.className = "typing";
    typing.textContent = "PawPal is preparing a reply...";
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return typing;
}

async function sendMessage(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || sendButton.disabled) {
        return;
    }

    addMessage(cleanQuestion, "user");
    chatInput.value = "";
    sendButton.disabled = true;

    const typing = showTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: cleanQuestion
            })
        });

        const data = await response.json();

        if (!response.ok) {
            addMessage(
                data.reply || "Sorry, something went wrong.",
                "bot"
            );
        } else {
            addMessage(
                data.reply || "Sorry, I couldn't generate a reply.",
                "bot"
            );
        }
    } catch (error) {
        console.error("Chat request failed:", error);

        addMessage(
            "I couldn't connect to the server. Please check that PawPal is running and try again.",
            "bot"
        );
    } finally {
        typing.remove();
        sendButton.disabled = false;
        chatInput.focus();
    }
}

chatForm.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(chatInput.value);
});

suggestionButtons.forEach((button) => {
    button.addEventListener("click", function () {
        sendMessage(button.dataset.question);
    });
});
