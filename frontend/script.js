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

function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.remove("hidden");
    result.classList.add("hidden");
}

function showResult(data) {
    const budgetLabel = { low: "🪙 Low Budget", moderate: "💳 Moderate Budget", high: "💎 High Budget" };
    resultTitle.textContent = `${data.destination} · ${data.days} Days`;
    resultBadge.textContent = budgetLabel[data.budget] ?? data.budget;
    itineraryContent.textContent = data.itinerary;
    result.classList.remove("hidden");
    errorMsg.classList.add("hidden");
    result.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const destination = document.getElementById("destination").value.trim();
    const days        = parseInt(document.getElementById("days").value, 10);
    const budget      = document.getElementById("budget").value;

    if (!destination) {
        showError("Please enter a destination.");
        return;
    }

    setLoading(true);
    errorMsg.classList.add("hidden");

    try {
        const response = await fetch(`${API_BASE}/plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ destination, days, budget }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail ?? `Server error (${response.status})`);
        }

        const data = await response.json();
        showResult(data);
    } catch (err) {
        showError(err.message || "Something went wrong. Is the backend running?");
    } finally {
        setLoading(false);
    }
});
