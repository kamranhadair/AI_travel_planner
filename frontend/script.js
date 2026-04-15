"use strict";

const API_BASE = "";  // served by FastAPI — relative URL works on any host

const form       = document.getElementById("plan-form");
const btnText    = document.getElementById("btn-text");
const btnLoader  = document.getElementById("btn-loader");
const submitBtn  = document.getElementById("submit-btn");
const result     = document.getElementById("result");
const resultTitle    = document.getElementById("result-title");
const resultBadge    = document.getElementById("result-badge");
const itineraryContent = document.getElementById("itinerary-content");
const errorMsg   = document.getElementById("error-msg");

function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.classList.toggle("hidden", loading);
    btnLoader.classList.toggle("hidden", !loading);
}

let currentSessionId = "";
let currentDestination = "";

function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.remove("hidden");
    result.classList.add("hidden");
}

function prepareResultUI(destination, days, budget) {
    const budgetLabel = { low: "🪙 Low Budget", moderate: "💳 Moderate Budget", high: "💎 High Budget" };
    resultTitle.textContent = `${destination} · ${days} Days`;
    resultBadge.textContent = budgetLabel[budget] ?? budget;
    itineraryContent.textContent = ""; // Clear existing content
    result.classList.remove("hidden");
    errorMsg.classList.add("hidden");
    result.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Start a fresh session for each new plan
    currentSessionId = self.crypto.randomUUID();
    
    currentDestination = document.getElementById("destination").value.trim();
    const destination = currentDestination;
    const days        = parseInt(document.getElementById("days").value, 10);
    const budget      = document.getElementById("budget").value;
    
    const interests   = document.getElementById("interests").value.trim() || undefined;
    const dietary_requirements = document.getElementById("diet").value.trim() || undefined;
    const pace        = document.getElementById("pace").value || undefined;

    if (!destination) {
        showError("Please enter a destination.");
        return;
    }

    setLoading(true);
    errorMsg.classList.add("hidden");
    result.classList.add("hidden");

    try {
        const payload = { 
            session_id: currentSessionId,
            destination, 
            days, 
            budget, 
            interests, 
            dietary_requirements, 
            pace 
        };
        
        const response = await fetch(`${API_BASE}/plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            
            // Handle FastAPI validation errors (422) cleanly
            if (response.status === 422 && Array.isArray(err.detail)) {
                const messages = err.detail.map(e => `${e.loc.join('.')}: ${e.msg}`);
                throw new Error(messages.join('\n'));
            }
            // Handle HTTPExceptions or other string details
            throw new Error(err.detail ?? `Server error (${response.status})`);
        }

        // Setup UI for incoming stream
        prepareResultUI(destination, days, budget);
        document.getElementById("chat-history").innerHTML = "";

        // Read stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            // Parse Markdown and render as HTML
            itineraryContent.innerHTML = marked.parse(fullText);
        }
        
    } catch (err) {
        showError(err.message || "Something went wrong. Is the backend running?");
    } finally {
        setLoading(false);
    }
});

// ── Chat Refiner Logic ──
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");
const chatHistory = document.getElementById("chat-history");

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message || !currentSessionId) return;

    // Append User message UI
    const userDiv = document.createElement("div");
    userDiv.className = "chat-msg chat-user";
    userDiv.textContent = message;
    chatHistory.appendChild(userDiv);
    
    chatInput.value = "";
    chatSend.disabled = true;

    // Append AI bubble placeholder
    const aiDiv = document.createElement("div");
    aiDiv.className = "chat-msg chat-ai";
    chatHistory.appendChild(aiDiv);

    try {
        const payload = { session_id: currentSessionId, destination: currentDestination, message };
        
        const response = await fetch(`${API_BASE}/refine`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to refine itinerary");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            aiDiv.innerHTML = marked.parse(fullText);
        }
    } catch (err) {
        aiDiv.textContent = "Error: " + err.message;
        aiDiv.style.color = "var(--error)";
    } finally {
        chatSend.disabled = false;
        aiDiv.scrollIntoView({ behavior: "smooth" });
    }
});
