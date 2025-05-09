document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("profile_edit_modal");
    const editBtn = document.getElementById("edit_profile_btn");
    const closeBtn = document.getElementsByClassName("close")[0];
    const editableDiv = document.getElementById("editableDiv");
    const profileForm = document.getElementById("profile_edit_form");
    const imagePreview = document.getElementById("image_preview");
    const fileInput = document.getElementById("profile_pic");

    // Tab functionality
    const tabs = document.querySelectorAll('.tab_button');
    const contents = document.querySelectorAll('.tab_content');

    // Show first tab content by default
    if (contents.length > 0) {
        contents[0].style.display = 'block';
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));

            // Hide all content sections
            contents.forEach(c => {
                c.classList.remove('active');
                c.style.display = 'none';
            });

            // Show selected tab and content
            tab.classList.add('active');
            const selectedContent = document.getElementById(tab.dataset.tab);
            if (selectedContent) {
                selectedContent.style.display = 'block';
                selectedContent.classList.add('active');
            }
        });
    });

    // Profile modal handling
    if (editBtn) editBtn.onclick = () => modal.style.display = "block";
    if (closeBtn) closeBtn.onclick = () => modal.style.display = "none";

    // Close on outside click
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Preview image
    if (fileInput) {
        fileInput.onchange = function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                }
                reader.readAsDataURL(file);
            }
        }
    }

    // Character counter for description
    const descriptionArea = document.getElementById('description');
    const charCounter = document.querySelector('.character-count');

    if (descriptionArea && charCounter) {
        descriptionArea.addEventListener('input', function() {
            const remaining = this.value.length;
            charCounter.textContent = `${remaining}/300 characters`;
        });

        // Initialize counter
        if (descriptionArea.value) {
            charCounter.textContent = `${descriptionArea.value.length}/300 characters`;
        }
    }

    // Handle form submission
    if (profileForm) {
        profileForm.onsubmit = async function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            try {
                const response = await fetch('/update_profile', {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                });

                const data = await response.json();

                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to update profile');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
                alert('Error updating profile');
            }
        }
    }

    // Description editing functionality
    const button = document.getElementById("edit_button");

    function toggleEditSave() {
        const isEditable = editableDiv.contentEditable === "true";
        if (isEditable) {
            saveDescription();
        } else {
            enableEditing();
        }
    }

    function enableEditing() {
        editableDiv.contentEditable = "true";
        button.innerHTML = '<i class="fas fa-save"></i>&nbsp;&nbsp;Save Changes';
        button.classList.add('editing');
        editableDiv.focus();
    }

    async function saveDescription() {
        editableDiv.contentEditable = "false";
        button.innerHTML = '<i class="fas fa-edit"></i>&nbsp;&nbsp;Edit Description';
        button.classList.remove('editing');

        const description = editableDiv.textContent.trim();

        try {
            const response = await fetch('/update_description', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description }),
                credentials: 'include'
            });

            const data = await response.json();
            if (!data.success) {
                console.error('Failed to save description');
            }
        } catch (error) {
            console.error('Error updating description:', error);
        }
    }

    button.addEventListener("click", toggleEditSave);
});