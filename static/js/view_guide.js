
// Like button functionality
document.querySelectorAll('.like_post_btn').forEach(btn => {
    const guideId = btn.getAttribute('data-guide-id');
    const likeSpan = btn.querySelector('.like_count');
    let isLiked = btn.classList.contains('liked');

    // Handle like button clicks
    btn.addEventListener('click', () => {
        updateGuideLikes(guideId, isLiked, likeSpan, btn);
    });
});

// Update guide likes via API
async function updateGuideLikes(guideId, isLiked, likeSpan, btn) {
    try {
        const response = await fetch(`/like_guide/${guideId}`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ isLiked })
        });
        const data = await response.json();
        
        if (data.likes !== undefined) {
            likeSpan.innerText = data.likes;
            btn.classList.toggle('liked');
        }
    } catch (error) {
        console.error('Error updating likes:', error);
    }
}

// Initialize comment count display
function updateCommentCount() {
    const commentCount = document.querySelector('.comment_count');
    if (commentCount) {
        const count = document.querySelectorAll('.comment').length;
        commentCount.textContent = count;
    }
}

// Guide editing functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeGuideEditor();
    initializeReportButtons();
    initializeCommentSystem();
    updateCommentCount();
});

// Initialize CKEditor for guide editing
function initializeGuideEditor() {
    const editButton = document.getElementById('edit_guide_button');
    const guideContent = document.getElementById('guideContent');
    let editor = null;

    if (editButton && guideContent) {
        editButton.addEventListener('click', function() {
            if (!editor) {
                initializeEditor();
            } else {
                saveGuideChanges();
            }
        });
    }

    // Initialize CKEditor instance
    async function initializeEditor() {
        try {
            editor = await ClassicEditor.create(guideContent, {
                toolbar: {
                    items: [
                        'heading', '|',
                        'bold', 'italic', 'link',
                        'bulletedList', 'numberedList',
                        'blockQuote', 'insertTable',
                        'undo', 'redo'
                    ]
                }
            });
            editButton.innerHTML = '<i class="fas fa-save"></i>&nbsp;&nbsp;Save Changes';
            editButton.classList.add('editing');
        } catch (error) {
            console.error('Editor initialization failed:', error);
        }
    }

    // Save guide content changes
    async function saveGuideChanges() {
        const content = editor.getData();
        const guideId = window.location.pathname.split('/').pop();

        try {
            const response = await fetch(`/update_guide/${guideId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content }),
                credentials: 'include'
            });
            const data = await response.json();

            if (data.success) {
                editor.destroy();
                editor = null;
                guideContent.innerHTML = content;
                editButton.innerHTML = '<i class="fas fa-edit"></i>&nbsp;&nbsp;Edit Guide';
                editButton.classList.remove('editing');
            }
        } catch (error) {
            console.error('Error saving guide:', error);
        }
    }
}

// Initialize report functionality
function initializeReportButtons() {
    document.querySelectorAll('.report_cmnt_btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const overlay = document.getElementById("report_overlay");
            if (overlay) overlay.style.display = "flex";
        });
    });
}

// Handle report submission
async function option(reason) {
    if (reason === 'X') {
        closeOverlays();
        return;
    }

    try {
        const guideId = document.querySelector('.like_post_btn').getAttribute('data-guide-id');
        await submitReport(guideId, reason);
        showReportConfirmation();
    } catch (error) {
        console.error('Error submitting report:', error);
    }
}

// Close report overlays
function closeOverlays() {
    const overlay = document.getElementById("report_overlay");
    const overlay_2 = document.getElementById("message_overlay");
    if (overlay) overlay.style.display = "none";
    if (overlay_2) overlay_2.style.display = "none";
}

// Submit report to server
async function submitReport(guideId, reason) {
    const response = await fetch(`/report_guide/${guideId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report_type: reason })
    });
    return await response.json();
}

// Show report confirmation message
function showReportConfirmation() {
    const overlay = document.getElementById("report_overlay");
    const messageOverlay = document.getElementById("message_overlay");
    if (overlay) overlay.style.display = "none";
    if (messageOverlay) {
        messageOverlay.style.display = "flex";
        setTimeout(() => {
            messageOverlay.style.display = "none";
        }, 2000);
    }
}

// Initialize comment system functionality
function initializeCommentSystem() {
    setupReplyButtons();
    setupCommentForm();
    setupReplyForms();
}

// Set up reply button functionality
function setupReplyButtons() {
    document.querySelectorAll(".reply_btn").forEach(button => {
        button.addEventListener("click", () => toggleReplyForm(button));
    });
}

// Toggle reply form visibility
function toggleReplyForm(button) {
    const replyForm = button.closest('.comment').querySelector(".reply_form");
    if (replyForm) {
        const isVisible = replyForm.style.display === "block";
        replyForm.style.display = isVisible ? "none" : "block";
        if (!isVisible) replyForm.querySelector("textarea").focus();
    }
}

// Set up main comment form
function setupCommentForm() {
    const commentForm = document.getElementById("comment_form");
    if (commentForm) {
        commentForm.addEventListener("submit", handleCommentSubmit);
    }
}

// Handle comment form submission
async function handleCommentSubmit(event) {
    event.preventDefault();
    const content = document.getElementById("content").value;

    try {
        const formData = new FormData();
        formData.append("content", content);

        const response = await fetch(event.target.action, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        const data = await response.json();

        if (data.success && data.comment) {
            window.location.reload();
        } else {
            window.location.href = '/error';
        }
    } catch (error) {
        console.error("Error submitting comment:", error);
        window.location.href = '/error';
    }
}

// Set up reply forms
function setupReplyForms() {
    document.querySelectorAll("form.reply_form").forEach((replyForm) => {
        replyForm.addEventListener("submit", handleReplySubmit);
    });
}

// Handle reply form submission
async function handleReplySubmit(event) {
    event.preventDefault();
    const textarea = event.target.querySelector("textarea[name='content']");
    const content = textarea.value;

    try {
        const formData = new FormData();
        formData.append("content", content);

        const response = await fetch(event.target.action, {
            method: "POST",
            body: formData,
            credentials: "include",
        });
        const data = await response.json();

        if (data.success && data.reply) {
            window.location.reload();
        } else {
            window.location.href = "/error";
        }
    } catch (error) {
        console.error("Reply submission error:", error);
        window.location.href = "/error";
    }
}
