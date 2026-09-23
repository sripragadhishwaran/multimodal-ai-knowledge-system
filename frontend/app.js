// ==================================================
// MULTIMODAL AI KNOWLEDGE SYSTEM
// FRONTEND APPLICATION
// ==================================================


// ==================================================
// API CONFIGURATION
// ==================================================

const API_URL = "http://127.0.0.1:8000";


// ==================================================
// DOM ELEMENTS
// ==================================================

const questionInput =
    document.getElementById("questionInput");

const askButton =
    document.getElementById("askButton");

const chatContainer =
    document.getElementById("chatContainer");

const welcome =
    document.getElementById("welcome");

const connectionStatus =
    document.getElementById("connectionStatus");


// Upload elements

const uploadButton =
    document.getElementById("uploadButton");

const fileInput =
    document.getElementById("fileInput");

const uploadStatus =
    document.getElementById("uploadStatus");


// ==================================================
// CHECK API
// ==================================================

async function checkAPI() {

    try {

        const response =
            await fetch(
                `${API_URL}/health`
            );


        if (!response.ok) {

            throw new Error(
                "API unavailable"
            );

        }


        connectionStatus.classList.remove(
            "offline"
        );

        connectionStatus.classList.add(
            "online"
        );


        connectionStatus.innerHTML = `
            <span class="status-dot"></span>
            <span>API Connected</span>
        `;


    } catch (error) {

        console.error(
            "API health check failed:",
            error
        );


        connectionStatus.classList.remove(
            "online"
        );

        connectionStatus.classList.add(
            "offline"
        );


        connectionStatus.innerHTML = `
            <span class="status-dot"></span>
            <span>API Offline</span>
        `;

    }

}


// ==================================================
// ASK QUESTION
// ==================================================

async function askQuestion(question) {

    question =
        String(
            question || ""
        ).trim();


    if (!question) {
        return;
    }


    // Remove welcome screen

    if (welcome) {
        welcome.remove();
    }


    // Add user message

    addUserMessage(
        question
    );


    // Clear input

    questionInput.value = "";

    resizeTextarea();


    // Disable ask button

    askButton.disabled = true;


    // Show loading

    const loadingElement =
        addLoadingMessage();


    try {

        const response =
            await fetch(
                `${API_URL}/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        // --------------------------------------------------
        // API ERROR
        // --------------------------------------------------

        if (!response.ok) {

            let errorMessage =
                `Request failed (${response.status})`;


            try {

                const errorData =
                    await response.json();


                errorMessage =
                    errorData.detail ||
                    errorData.message ||
                    errorMessage;


            } catch {

                try {

                    const errorText =
                        await response.text();


                    if (errorText) {

                        errorMessage =
                            errorText;

                    }

                } catch {

                    // Ignore response parsing error

                }

            }


            throw new Error(
                errorMessage
            );

        }


        // --------------------------------------------------
        // RESPONSE
        // --------------------------------------------------

        const data =
            await response.json();


        // Remove loading

        loadingElement.remove();


        // Display answer

        addAssistantMessage(
            data
        );


    } catch (error) {

        console.error(
            "Question error:",
            error
        );


        loadingElement.remove();


        addErrorMessage(
            error.message ||
            "Unable to connect to the API."
        );


    } finally {

        askButton.disabled = false;

        questionInput.focus();

    }

}


// ==================================================
// USER MESSAGE
// ==================================================

function addUserMessage(question) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message user";


    message.innerHTML = `
        <div class="user-message">
            ${escapeHTML(question)}
        </div>
    `;


    chatContainer.appendChild(
        message
    );


    scrollToBottom();

}


// ==================================================
// SOURCE URL
// ==================================================

function getSourceURL(source) {

    if (!source) {
        return "";
    }


    let cleanPath =
        String(source)
            .trim()
            .replace(/\\/g, "/");


    // --------------------------------------------------
    // WINDOWS ABSOLUTE PATH
    // --------------------------------------------------

    const dataRawIndex =
        cleanPath
            .toLowerCase()
            .indexOf(
                "data/raw/"
            );


    if (dataRawIndex >= 0) {

        cleanPath =
            cleanPath.substring(
                dataRawIndex +
                "data/raw/".length
            );

    }


    // --------------------------------------------------
    // ./data/raw/
    // --------------------------------------------------

    if (
        cleanPath.startsWith(
            "./data/raw/"
        )
    ) {

        cleanPath =
            cleanPath.substring(
                "./data/raw/".length
            );

    }


    // --------------------------------------------------
    // data/raw/
    // --------------------------------------------------

    if (
        cleanPath.startsWith(
            "data/raw/"
        )
    ) {

        cleanPath =
            cleanPath.substring(
                "data/raw/".length
            );

    }


    cleanPath =
        cleanPath.replace(
            /^\/+/,
            ""
        );


    // --------------------------------------------------
    // URL ENCODING
    // --------------------------------------------------

    const encodedPath =
        cleanPath
            .split("/")
            .filter(Boolean)
            .map(
                part =>
                    encodeURIComponent(part)
            )
            .join("/");


    return `${API_URL}/sources/${encodedPath}`;

}


// ==================================================
// FILE NAME
// ==================================================

function getFileName(source) {

    if (!source) {
        return "Unknown source";
    }


    const normalized =
        String(source)
            .replace(
                /\\/g,
                "/"
            );


    const parts =
        normalized.split("/");


    return (
        parts[parts.length - 1] ||
        "Unknown source"
    );

}


// ==================================================
// IMAGE DETECTION
// ==================================================

function isImageSource(source) {

    const lower =
        String(source || "")
            .toLowerCase();


    return (

        lower.endsWith(".png") ||

        lower.endsWith(".jpg") ||

        lower.endsWith(".jpeg") ||

        lower.endsWith(".webp") ||

        lower.endsWith(".gif") ||

        lower.endsWith(".bmp") ||

        lower.endsWith(".svg")

    );

}


// ==================================================
// DOCUMENT DETECTION
// ==================================================

function isDocumentSource(source) {

    const lower =
        String(source || "")
            .toLowerCase();


    return (

        lower.endsWith(".pdf") ||

        lower.endsWith(".txt") ||

        lower.endsWith(".md")

    );

}


// ==================================================
// SOURCE CARD
// ==================================================

function buildSourceCard(
    source,
    type
) {

    const fileName =
        getFileName(
            source
        );


    const sourceURL =
        getSourceURL(
            source
        );


    // ==================================================
    // IMAGE SOURCE
    // ==================================================

    if (
        type === "image" ||
        isImageSource(source)
    ) {

        return `

            <div
                class="source-card image-source-card"
            >

                <div
                    class="source-header"
                >

                    <div
                        class="source-icon"
                    >
                        🖼️
                    </div>


                    <div
                        class="source-info"
                    >

                        <div
                            class="source-name"
                            title="${escapeHTML(fileName)}"
                        >
                            ${escapeHTML(fileName)}
                        </div>


                        <div
                            class="source-type"
                        >
                            IMAGE
                        </div>

                    </div>

                </div>


                <div
                    class="source-preview"
                >

                    <img
                        src="${escapeHTML(sourceURL)}"
                        alt="${escapeHTML(fileName)}"
                        loading="lazy"
                        onerror="
                            this.parentElement.style.display='none';
                        "
                    >

                </div>


                <a
                    class="source-button"
                    href="${escapeHTML(sourceURL)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    View Image
                </a>

            </div>

        `;

    }


    // ==================================================
    // DOCUMENT SOURCE
    // ==================================================

    if (
        type === "document" ||
        isDocumentSource(source)
    ) {

        const extension =
            fileName
                .split(".")
                .pop()
                .toUpperCase();


        return `

            <div
                class="source-card"
            >

                <div
                    class="source-header"
                >

                    <div
                        class="source-icon"
                    >
                        📄
                    </div>


                    <div
                        class="source-info"
                    >

                        <div
                            class="source-name"
                            title="${escapeHTML(fileName)}"
                        >
                            ${escapeHTML(fileName)}
                        </div>


                        <div
                            class="source-type"
                        >
                            ${extension} DOCUMENT
                        </div>

                    </div>

                </div>


                <a
                    class="source-button"
                    href="${escapeHTML(sourceURL)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Open Document
                </a>

            </div>

        `;

    }


    // ==================================================
    // WEB SOURCE
    // ==================================================

    return `

        <div
            class="source-card"
        >

            <div
                class="source-header"
            >

                <div
                    class="source-icon"
                >
                    🌐
                </div>


                <div
                    class="source-info"
                >

                    <div
                        class="source-name"
                        title="${escapeHTML(fileName)}"
                    >
                        ${escapeHTML(fileName)}
                    </div>


                    <div
                        class="source-type"
                    >
                        WEB SOURCE
                    </div>

                </div>

            </div>

        </div>

    `;

}


// ==================================================
// RENDER ANSWER
// ==================================================

function renderAnswer(value) {

    let text =
        String(
            value || ""
        )
        .replace(
            /\r\n/g,
            "\n"
        );


    // --------------------------------------------------
    // ESCAPE HTML
    // --------------------------------------------------

    text =
        escapeHTML(
            text
        );


    // --------------------------------------------------
    // BOLD
    // --------------------------------------------------

    text =
        text.replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        );


    // --------------------------------------------------
    // INLINE CODE
    // --------------------------------------------------

    text =
        text.replace(
            /`([^`]+)`/g,
            "<code>$1</code>"
        );


    // --------------------------------------------------
    // SOURCE CITATIONS
    // --------------------------------------------------

    text =
        text.replace(
            /\[Source\s+(\d+)\]/gi,
            '<span class="citation">[Source $1]</span>'
        );


    // --------------------------------------------------
    // MARKDOWN BULLETS
    // --------------------------------------------------

    text =
        text.replace(
            /^[ \t]*[-*]\s+(.+)$/gm,
            "<li>$1</li>"
        );


    // --------------------------------------------------
    // GROUP LIST ITEMS
    // --------------------------------------------------

    text =
        text.replace(
            /((?:<li>.*?<\/li>\s*)+)/gs,
            "<ul>$1</ul>"
        );


    // --------------------------------------------------
    // PARAGRAPHS
    // --------------------------------------------------

    const blocks =
        text
            .split(/\n{2,}/)
            .map(
                block =>
                    block.trim()
            )
            .filter(Boolean);


    return blocks
        .map(
            block => {

                if (
                    block.startsWith(
                        "<ul>"
                    ) &&
                    block.endsWith(
                        "</ul>"
                    )
                ) {

                    return block;

                }


                return `
                    <p>
                        ${block.replace(
                            /\n/g,
                            "<br>"
                        )}
                    </p>
                `;

            }
        )
        .join("");

}


// ==================================================
// ASSISTANT MESSAGE
// ==================================================

function addAssistantMessage(data) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message";


    // --------------------------------------------------
    // ANSWER
    // --------------------------------------------------

    const answer =
        renderAnswer(
            data?.answer || ""
        );


    // --------------------------------------------------
    // SOURCE ARRAYS
    // --------------------------------------------------

    const imageSources =
        Array.isArray(
            data?.image_sources
        )
            ? data.image_sources
            : [];


    const documentSources =
        Array.isArray(
            data?.document_sources
        )
            ? data.document_sources
            : [];


    const webSources =
        Array.isArray(
            data?.web_sources
        )
            ? data.web_sources
            : [];


    const sourceCards = [];


    // --------------------------------------------------
    // IMAGE SOURCES
    // --------------------------------------------------

    imageSources.forEach(
        source => {

            sourceCards.push(
                buildSourceCard(
                    source,
                    "image"
                )
            );

        }
    );


    // --------------------------------------------------
    // DOCUMENT SOURCES
    // --------------------------------------------------

    documentSources.forEach(
        source => {

            sourceCards.push(
                buildSourceCard(
                    source,
                    "document"
                )
            );

        }
    );


    // --------------------------------------------------
    // WEB SOURCES
    // --------------------------------------------------

    webSources.forEach(
        source => {

            sourceCards.push(
                buildSourceCard(
                    source,
                    "web"
                )
            );

        }
    );


    // ==================================================
    // SOURCE HTML
    // ==================================================

    let sourcesHTML = "";


    if (
        sourceCards.length > 0
    ) {

        sourcesHTML = `

            <div
                class="sources-section"
            >

                <div
                    class="sources-title"
                >
                    Sources
                </div>


                <div
                    class="source-grid"
                >

                    ${sourceCards.join("")}

                </div>

            </div>

        `;

    }


    // ==================================================
    // BADGES
    // ==================================================

    const contentTypes =
        Array.isArray(
            data?.content_types
        )
            ? data.content_types
            : [];


    let badgesHTML = "";


    contentTypes.forEach(
        type => {

            badgesHTML += `

                <span class="source-meta">

                    ${escapeHTML(type)}

                </span>

            `;

        }
    );


    if (data?.multimodal) {

        badgesHTML += `

            <span class="multimodal-badge">
                multimodal
            </span>

        `;

    }


    const sourceCount =
        Number.isFinite(
            Number(
                data?.source_count
            )
        )
            ? Number(
                data.source_count
            )
            : sourceCards.length;


    badgesHTML += `

        <span class="source-meta">

            ${sourceCount}
            source(s)

        </span>

    `;


    // ==================================================
    // FINAL MESSAGE
    // ==================================================

    message.innerHTML = `

        <div
            class="assistant-message"
        >


            <div
                class="assistant-label"
            >
                ✦ AI Knowledge Assistant
            </div>


            <div
                class="assistant-content"
            >

                ${answer}

            </div>


            ${sourcesHTML}


            <div
                class="source-meta"
            >

                ${badgesHTML}

            </div>


        </div>

    `;


    chatContainer.appendChild(
        message
    );


    scrollToBottom();

}


// ==================================================
// LOADING MESSAGE
// ==================================================

function addLoadingMessage() {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message";


    message.innerHTML = `

        <div
            class="assistant-message"
        >

            <div
                class="loading"
            >

                <div
                    class="loading-dots"
                >

                    <span></span>
                    <span></span>
                    <span></span>

                </div>


                <span>
                    Searching your knowledge base...
                </span>

            </div>

        </div>

    `;


    chatContainer.appendChild(
        message
    );


    scrollToBottom();


    return message;

}


// ==================================================
// ERROR MESSAGE
// ==================================================

function addErrorMessage(error) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message";


    message.innerHTML = `

        <div
            class="error-message"
        >

            <div
                class="error-title"
            >
                ⚠ Error
            </div>


            <div>

                Unable to process the question.

            </div>


            <div
                style="margin-top: 8px;"
            >

                ${escapeHTML(error)}

            </div>

        </div>

    `;


    chatContainer.appendChild(
        message
    );


    scrollToBottom();

}


// ==================================================
// UPLOAD FILE
// ==================================================

async function uploadKnowledgeFile(file) {

    if (!file) {
        return;
    }


    // --------------------------------------------------
    // SUPPORTED EXTENSIONS
    // --------------------------------------------------

    const allowedExtensions = [

        ".pdf",

        ".txt",

        ".md",

        ".png",

        ".jpg",

        ".jpeg",

        ".webp"

    ];


    const fileName =
        file.name.toLowerCase();


    const isAllowed =
        allowedExtensions.some(
            extension =>
                fileName.endsWith(
                    extension
                )
        );


    if (!isAllowed) {

        showUploadStatus(
            "Unsupported file type.",
            "error"
        );

        return;

    }


    // --------------------------------------------------
    // FILE SIZE
    // --------------------------------------------------

    const maxSize =
        50 * 1024 * 1024;


    if (
        file.size >
        maxSize
    ) {

        showUploadStatus(
            "File is too large. Maximum size is 50 MB.",
            "error"
        );

        return;

    }


    // --------------------------------------------------
    // BUTTON STATE
    // --------------------------------------------------

    const originalText =
        uploadButton.textContent;


    uploadButton.disabled =
        true;


    uploadButton.textContent =
        "⏳ Uploading...";


    showUploadStatus(
        `Uploading ${file.name}...`,
        "loading"
    );


    try {

        // --------------------------------------------------
        // FORM DATA
        // --------------------------------------------------

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        // --------------------------------------------------
        // SEND TO FASTAPI
        // --------------------------------------------------

        const response =
            await fetch(
                `${API_URL}/upload`,
                {
                    method: "POST",

                    body: formData
                }
            );


        // --------------------------------------------------
        // RESPONSE
        // --------------------------------------------------

        let data = null;


        try {

            data =
                await response.json();

        } catch {

            throw new Error(
                "Invalid response received from the API."
            );

        }


        // --------------------------------------------------
        // API ERROR
        // --------------------------------------------------

        if (!response.ok) {

            throw new Error(

                data?.detail ||

                data?.message ||

                `Upload failed (${response.status})`

            );

        }


        // --------------------------------------------------
        // SUCCESS
        // --------------------------------------------------

        console.log(
            "Upload successful:",
            data
        );


        uploadButton.textContent =
            "✓ Uploaded";


        showUploadStatus(
            `${file.name} uploaded and indexed successfully.`,
            "success"
        );


        // Restore button

        setTimeout(
            () => {

                uploadButton.textContent =
                    originalText;

                uploadButton.disabled =
                    false;

            },
            2000
        );


    } catch (error) {

        console.error(
            "Upload error:",
            error
        );


        uploadButton.textContent =
            "❌ Upload Failed";


        uploadButton.disabled =
            false;


        showUploadStatus(
            error.message ||
            "File upload failed.",
            "error"
        );


        setTimeout(
            () => {

                uploadButton.textContent =
                    originalText;

            },
            2500
        );

    }

}


// ==================================================
// UPLOAD STATUS
// ==================================================

function showUploadStatus(
    message,
    type
) {

    if (!uploadStatus) {
        return;
    }


    uploadStatus.textContent =
        message;


    uploadStatus.dataset.status =
        type;


    // Automatically clear success message

    if (
        type === "success"
    ) {

        setTimeout(
            () => {

                uploadStatus.textContent =
                    "";

                uploadStatus.dataset.status =
                    "";

            },
            4000
        );

    }

}


// ==================================================
// OPEN FILE PICKER
// ==================================================

if (
    uploadButton &&
    fileInput
) {

    uploadButton.addEventListener(
        "click",
        () => {

            fileInput.click();

        }
    );

}


// ==================================================
// FILE SELECTION
// ==================================================

if (fileInput) {

    fileInput.addEventListener(
        "change",
        async () => {

            const file =
                fileInput.files[0];


            if (!file) {
                return;
            }


            await uploadKnowledgeFile(
                file
            );


            // Allow same file
            // to be selected again

            fileInput.value = "";

        }
    );

}


// ==================================================
// TEXTAREA RESIZE
// ==================================================

function resizeTextarea() {

    questionInput.style.height =
        "auto";


    questionInput.style.height =
        `${questionInput.scrollHeight}px`;

}


// ==================================================
// SCROLL
// ==================================================

function scrollToBottom() {

    requestAnimationFrame(
        () => {

            chatContainer.scrollTop =
                chatContainer.scrollHeight;

        }
    );

}


// ==================================================
// ESCAPE HTML
// ==================================================

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(
            value ?? ""
        );


    return div.innerHTML;

}


// ==================================================
// ASK BUTTON
// ==================================================

askButton.addEventListener(
    "click",
    () => {

        askQuestion(
            questionInput.value
        );

    }
);


// ==================================================
// ENTER KEY
// ==================================================

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();


            askQuestion(
                questionInput.value
            );

        }

    }
);


// ==================================================
// TEXTAREA INPUT
// ==================================================

questionInput.addEventListener(
    "input",
    resizeTextarea
);


// ==================================================
// SUGGESTION BUTTONS
// ==================================================

document
    .querySelectorAll(
        ".suggestion"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const question =
                        button.dataset.question ||
                        "";


                    askQuestion(
                        question
                    );

                }
            );

        }
    );


// ==================================================
// INITIALIZE
// ==================================================

checkAPI();

resizeTextarea();

questionInput.focus();