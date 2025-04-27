
// Get DOM elements
const editableDiv = document.getElementById("editableDiv");
const button = document.getElementById("edit_button");

// Toggle between edit and save modes
function toggleEditSave() {
    const isEditable = editableDiv.contentEditable === "true";

    if (isEditable) {
        saveDescription();
    } else {
        enableEditing();
    }
}

// Enable description editing
function enableEditing() {
    editableDiv.contentEditable = "true";
    button.innerHTML = '<i class="fas fa-save"></i>&nbsp;&nbsp;Save Changes';
    button.classList.add('editing');
    editableDiv.focus();
}

// Save description changes
async function saveDescription() {
    editableDiv.contentEditable = "false";
    button.innerHTML = '<i class="fas fa-edit"></i>&nbsp;&nbsp;Edit Description';
    button.classList.remove('editing');

    const description = editableDiv.innerHTML.trim();
    
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

// Add click event listener
button.addEventListener("click", toggleEditSave);
