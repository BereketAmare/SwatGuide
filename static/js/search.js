
// Initialize search functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupSearchForm();
});

// Set up search form handler
function setupSearchForm() {
    const searchForm = document.querySelector("form");
    if (searchForm) {
        searchForm.addEventListener("submit", handleSearch);
    }
}

// Handle search form submission
function handleSearch(event) {
    event.preventDefault();
    
    const searchQuery = document.getElementById("search_input").value;
    updateSearchQueryDisplay(searchQuery);
    performSearch();
}

// Update search query display
function updateSearchQueryDisplay(query) {
    const searchQueryElement = document.getElementById("search_query");
    if (searchQueryElement) {
        searchQueryElement.innerText = query;
    }
}

// Perform search and display results
function performSearch() {
    const resultsContainer = document.getElementById("search_results");
    if (!resultsContainer) return;

    // Clear previous results
    resultsContainer.innerHTML = '';

    // Display search results
    fakeResults.forEach(result => {
        const resultElement = createResultElement(result);
        resultsContainer.appendChild(resultElement);
    });
}

// Create result element
function createResultElement(result) {
    const div = document.createElement("div");
    div.className = "list-group-item";
    
    const title = document.createElement("h4");
    title.innerText = result.title;
    div.appendChild(title);

    return div;
}

// Sample search results (for demonstration)
const fakeResults = [
    { id: 1, title: 'Fake Guide 1' },
    { id: 2, title: 'Fake Guide 2' },
    { id: 3, title: 'Fake Guide 3' }
];
