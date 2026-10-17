document.addEventListener("DOMContentLoaded", function () {

    let isTyping = false;

    // ================= SCROLL =================
    function scrollBottom() {
        let box = document.getElementById("chatBox");
        if (box) box.scrollTop = box.scrollHeight;
    }

    scrollBottom();

    // ================= TYPING DETECTION =================
    document.addEventListener("focusin", function(e) {
        if (e.target.tagName === "INPUT") {
            isTyping = true;
        }
    });

    document.addEventListener("focusout", function(e) {
        if (e.target.tagName === "INPUT") {
            isTyping = false;
        }
    });

    let messageBox = document.getElementById("messageBox");

    if (messageBox) {
        messageBox.addEventListener("input", () => {
            let typing = document.getElementById("typing");

            if (typing) {
                typing.style.display = "block";

                clearTimeout(window.typingTimer);
                window.typingTimer = setTimeout(() => {
                    typing.style.display = "none";
                }, 1000);
            }
        });
    }

    // ================= DECRYPT =================
    function attachDecryptEvents() {
        document.querySelectorAll(".decrypt-form").forEach(form => {

            // Avoid duplicate listeners
            if (form.dataset.bound) return;
            form.dataset.bound = "true";

            form.addEventListener("submit", function (e) {
                e.preventDefault();

                let formData = new FormData(this);
                let resultBox = this.parentElement.querySelector(".result");

                if (resultBox) resultBox.innerText = "Decrypting...";

                fetch("/decrypt", {
                    method: "POST",
                    body: formData
                })
                .then(res => res.json())
                .then(data => {
                    if (resultBox) resultBox.innerText = data.message;
                })
                .catch(() => {
                    if (resultBox) resultBox.innerText = "Error!";
                });
            });
        });
    }

    attachDecryptEvents();

    // ================= IMAGE MODAL =================
    function attachImagePreview() {
        document.querySelectorAll(".chat-img").forEach(img => {

            if (img.dataset.bound) return;
            img.dataset.bound = "true";

            img.onclick = function () {
                let modal = document.getElementById("imgModal");
                let modalImg = document.getElementById("modalImg");

                if (modal && modalImg) {
                    modal.style.display = "block";
                    modalImg.src = this.src;
                }
            };

        });
    }

    attachImagePreview();

    // Close modal
    window.closeModal = function () {
        let modal = document.getElementById("imgModal");
        if (modal) modal.style.display = "none";
    };

    // ================= DARK MODE =================
    window.toggleDarkMode = function () {
        document.body.classList.toggle("dark");
    };

    // ================= SAFE REAL-TIME REFRESH =================
    function refreshChat() {

        // Stop refresh if user is typing
        if (isTyping) return;

        fetch(window.location.href)
            .then(res => res.text())
            .then(html => {

                let parser = new DOMParser();
                let doc = parser.parseFromString(html, "text/html");

                let newChat = doc.getElementById("chatBox");

                if (newChat) {
                    document.getElementById("chatBox").innerHTML = newChat.innerHTML;

                    // Reattach events after refresh
                    attachDecryptEvents();
                    attachImagePreview();

                    scrollBottom();
                }
            });
    }

    // Refresh every 5 seconds
    setInterval(refreshChat, 5000);

});
