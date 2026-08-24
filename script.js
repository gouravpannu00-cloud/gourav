// ---------------------------------------------
// DAY / NIGHT MODE
// ---------------------------------------------

function toggleTheme() {

    document.body.classList.toggle("night");

    const night =
        document.body.classList.contains("night");

    localStorage.setItem(
        "nightMode",
        night
    );

    updateThemeButton();

    if (night) {

        createStars();

    } else {

        removeStars();

    }
}


// ---------------------------------------------
// BUTTON TEXT
// ---------------------------------------------

function updateThemeButton() {

    const button =
        document.querySelector(".theme-button");

    if (!button) {
        return;
    }

    if (
        document.body.classList.contains("night")
    ) {

        button.innerHTML =
            "☀️ Day Mode";

    } else {

        button.innerHTML =
            "🌙 Night Mode";

    }
}


// ---------------------------------------------
// CREATE BLINKING STARS
// ---------------------------------------------

function createStars() {

    const container =
        document.getElementById("stars");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    for (
        let i = 0;
        i < 80;
        i++
    ) {

        const star =
            document.createElement("span");

        star.className = "star";

        star.innerHTML = "✦";

        star.style.left =
            Math.random() * 100 + "%";

        star.style.top =
            Math.random() * 100 + "%";

        star.style.animationDelay =
            Math.random() * 3 + "s";

        star.style.animationDuration =
            (1 + Math.random() * 2) + "s";

        container.appendChild(star);
    }
}


// ---------------------------------------------
// REMOVE STARS
// ---------------------------------------------

function removeStars() {

    const container =
        document.getElementById("stars");

    if (container) {

        container.innerHTML = "";

    }
}


// ---------------------------------------------
// ADD DOCUMENT ROW
// ---------------------------------------------

function addDocumentRow() {

    const area =
        document.getElementById(
            "document-area"
        );

    if (!area) {
        return;
    }


    const row =
        document.createElement("div");

    row.className =
        "document-row";


    row.innerHTML = `

        <input
            type="text"
            name="document_name"
            placeholder="Document Name">

        <input
            type="date"
            name="valid_until">

        <input
            type="file"
            name="documents">

    `;


    area.appendChild(row);
}


// ---------------------------------------------
// LOAD THEME
// ---------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const night =
            localStorage.getItem(
                "nightMode"
            );

        if (night === "true") {

            document.body.classList.add(
                "night"
            );

            createStars();

        }

        updateThemeButton();

    }
);