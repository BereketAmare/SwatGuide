
// Initialize CKEditor instance
let editor;

// Create and configure CKEditor
ClassicEditor
    .create(document.querySelector('#editor'), {
        toolbar: {
            items: [
                'heading', '|',
                'bold', 'italic', 'link',
                'bulletedList', 'numberedList',
                'blockQuote', 'insertTable',
                'undo', 'redo'
            ]
        }
    })
    .then(newEditor => {
        editor = newEditor;
    })
    .catch(error => {
        console.error('Editor initialization error:', error);
    });

// Handle guide form submission
document.getElementById("guide_form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const guideData = {
        title: document.getElementById("title").value,
        content: editor.getData()
    };

    try {
        const response = await fetch('/create_guide', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(guideData),
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success && data.guide && data.guide.id) {
            window.location.href = `/view_guide/${data.guide.id}`;
        } else {
            window.location.href = '/error';
        }
    } catch (error) {
        console.error("Guide creation error:", error);
        window.location.href = '/error';
    }
});
