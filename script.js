const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");


const API_KEY = ""; // Replace with your OpenRouter API key
let knowledge = [];


// Keywords to check if query is agriculture-related
const agricultureKeywords = [
    // Crops
    "rice", "wheat", "maize", "corn", "cotton", "sugarcane", "groundnut",
    "millets", "pulses", "vegetable", "fruit", "tomato", "potato", "onion",
    "cabbage", "cucumber", "banana", "mango", "orange", "apple", "tea", "coffee", "rubber", "coconut",
    
    // Soil types & properties
    "soil", "loamy", "sandy", "clay", "black soil", "red soil", "laterite", "alluvial", "fertile", "ph",
    
    // Fertilizers & nutrients
    "fertilizer", "urea", "ammonium sulfate", "dap", "ssp", "mop", "sop", "nitrogen", "phosphorus", "potassium", "organic", "manure", "compost", "vermicompost",
    
    // Farming practices
    "crop rotation", "irrigation", "drip", "sprinkler", "seeds", "sowing", "harvest", "planting", "nursery", "mulching", "green manure", "organic farming", "pesticide", "herbicide",
    
    // Farmer & support terms
    "farmer", "farm", "agriculture", "agricultural", "subsidy", "scheme", "loan", "insurance", "pm-kisan", "soil health card", "equipment", "tractor", "fertilizer recommendation",
    
    // Pests & diseases
    "pest", "insect", "disease", "fungus", "blight", "aphid", "weevil", "bollworm",
    
    // Water & climate
    "rainfall", "temperature", "humidity", "climate", "drought", "flood", "water", "moisture", "drainage"
];


// Load base knowledge JSON
fetch("knowledge.json")
    .then(response => response.json())
    .then(data => knowledge = data)
    .catch(err => console.error("Failed to load knowledge base:", err));

// Check if query is agriculture-related
function isAgricultureQuery(query) {
    const q = query.toLowerCase();
    return agricultureKeywords.some(word => q.includes(word));
}

// Find answer from base knowledge
function findAnswerFromKnowledge(query) {
    const q = query.toLowerCase();
    for (let item of knowledge) {
        if (q.includes(item.question.toLowerCase())) {
            return item.answer;
        }
    }
    return null; // Not found in knowledge base
}

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Show user message
    chatBox.innerHTML += `<div class="message user">${message}</div>`;
    userInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Step 1: Check if query is agriculture-related
    if (!isAgricultureQuery(message)) {
        const answer = "Sorry, I cannot answer that question.";
        chatBox.innerHTML += `<div class="message bot">${answer}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
        return;
    }

    // Step 2: Check base knowledge
    const knowledgeAnswer = findAnswerFromKnowledge(message);
    if (knowledgeAnswer) {
        chatBox.innerHTML += `<div class="message bot">${knowledgeAnswer}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
        return;
    }

    // Step 3: Ask OpenRouter for dynamic answer
    try {
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: "gpt-4o-mini",
                messages: [
                    { 
                        role: "system", 
                        content: "You are an assistant specialized ONLY in agriculture. Answer only agriculture-related questions. If the question is outside agriculture, reply: 'Sorry, I cannot answer that question.' Keep your answer short and precise." 
                    },
                    { role: "user", content: message }
                ],
                temperature: 0.3,
                max_tokens: 50
            })
        });

        const data = await response.json();
        const answer = data.choices[0].message.content;

        chatBox.innerHTML += `<div class="message bot">${answer}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        chatBox.innerHTML += `<div class="message bot">Error fetching response from OpenRouter.</div>`;
    }
}

// Optional: allow Enter key to send message
userInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
