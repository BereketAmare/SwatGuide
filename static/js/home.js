
document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sort_by');
    const timeSelect = document.getElementById('time_filter');

    function updateFilters() {
        const sortBy = sortSelect.value;
        const timeFilter = timeSelect.value;
        window.location.href = `/?sort_by=${sortBy}&time_filter=${timeFilter}`;
    }

    sortSelect.addEventListener('change', updateFilters);
    timeSelect.addEventListener('change', updateFilters);
});
