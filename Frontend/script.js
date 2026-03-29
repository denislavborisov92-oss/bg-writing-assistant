const API_URL = "/process";

let currentMode = "fix";
let lastUsedMode = "fix";

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".mode-btn");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      button.classList.add("active");
      currentMode = button.dataset.mode;
      lastUsedMode = currentMode;
    });
  });
});

function getPayload(mode, text) {
  return {
    text: text,
    mode: mode,
    tone: document.getElementById("toneSelect").value,
    length: document.getElementById("lengthSelect").value,
    instruction: document.getElementById("instructionInput").value.trim(),
  };
}

async function sendCurrentMode() {
  await sendText(currentMode);
}

async function improveAgain() {
  const resultText = document.getElementById("result").textContent.trim();

  if (!resultText || resultText === "Тук ще се покаже подобреният текст.") {
    document.getElementById("status").textContent = "Няма резултат за допълнително подобрение.";
    return;
  }

  document.getElementById("textInput").value = resultText;
  await sendText(lastUsedMode);
}

async function sendText(mode) {
  const text = document.getElementById("textInput").value;
  const result = document.getElementById("result");
  const status = document.getElementById("status");
  const loader = document.getElementById("loader");

  if (!text.trim()) {
    status.textContent = "Моля, въведи текст.";
    return;
  }

  status.textContent = "Обработва се...";
  loader.classList.remove("hidden");
  result.style.opacity = "0.35";
  result.style.transform = "translateY(4px)";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(getPayload(mode, text))
    });

    const data = await response.json();
    result.textContent = data.result || "Няма резултат.";
    status.textContent = "Готово.";
    lastUsedMode = mode;
  } catch (error) {
    console.error(error);
    result.textContent = "Възникна проблем при обработката.";
    status.textContent = "Грешка при връзката със сървъра.";
  } finally {
    loader.classList.add("hidden");
    result.style.opacity = "1";
    result.style.transform = "translateY(0)";
  }
}

function copyResult() {
  const resultText = document.getElementById("result").textContent.trim();
  const status = document.getElementById("status");

  if (!resultText || resultText === "Тук ще се покаже подобреният текст.") {
    status.textContent = "Няма текст за копиране.";
    return;
  }

  navigator.clipboard.writeText(resultText)
    .then(() => {
      status.textContent = "Текстът е копиран.";
    })
    .catch(() => {
      status.textContent = "Неуспешно копиране.";
    });
}

function clearAll() {
  document.getElementById("textInput").value = "";
  document.getElementById("instructionInput").value = "";
  document.getElementById("toneSelect").value = "default";
  document.getElementById("lengthSelect").value = "default";
  document.getElementById("result").textContent = "Тук ще се покаже подобреният текст.";
  document.getElementById("status").textContent = "Изчистено.";
}

function pasteResultBack() {
  const resultText = document.getElementById("result").textContent.trim();
  const status = document.getElementById("status");

  if (!resultText || resultText === "Тук ще се покаже подобреният текст.") {
    status.textContent = "Няма резултат за поставяне.";
    return;
  }

  document.getElementById("textInput").value = resultText;
  status.textContent = "Резултатът е поставен обратно в полето.";
}