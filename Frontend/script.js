// =============================================
// WAIT FOR DOM — fixes cache-related failures
// =============================================

document.addEventListener("DOMContentLoaded", function () {

    // =============================================
    // COLLECT ALL ITEM DATA FROM CARDS
    // =============================================

    function getAllItemData() {
        var cards = document.querySelectorAll(".dash-item-card");
        var items = [];
        cards.forEach(function (card) {
            items.push({
                card:        card,
                name:        (card.dataset.name   || "").toLowerCase(),
                status:      (card.dataset.status || "").toLowerCase(),
                type:        (card.dataset.type   || "").toLowerCase(),
                desc:        (card.dataset.desc   || "").toLowerCase(),
                nameDisplay: (card.dataset.name   || ""),
                descDisplay: (card.dataset.desc   || ""),
            });
        });
        return items;
    }


    // =============================================
    // HIGHLIGHT MATCHING TEXT
    // =============================================

    function highlightMatch(text, keyword) {
        if (!keyword) return text;
        var escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        var regex   = new RegExp("(" + escaped + ")", "gi");
        return text.replace(regex, "<mark>$1</mark>");
    }


    // =============================================
    // ELEMENTS — safe to query now, DOM is ready
    // =============================================

    var searchBox      = document.getElementById("searchBox");
    var searchDropdown = document.getElementById("searchDropdown");
    var filterStatus   = document.getElementById("filterStatus");
    var visibleCount   = document.getElementById("visibleCount");


    // =============================================
    // DROPDOWN SUGGESTIONS
    // =============================================

    function showDropdown(keyword) {
        if (!searchDropdown) return;

        if (!keyword || keyword.length === 0) {
            searchDropdown.style.display = "none";
            searchDropdown.innerHTML     = "";
            return;
        }

        var allItems = getAllItemData();
        var matches  = allItems.filter(function (item) {
            return item.name.includes(keyword) || item.desc.includes(keyword);
        });

        searchDropdown.innerHTML = "";

        if (matches.length === 0) {
            searchDropdown.innerHTML     = '<div class="search-no-results">No items found for "' + keyword + '"</div>';
            searchDropdown.style.display = "block";
            return;
        }

        matches.slice(0, 6).forEach(function (item) {
            var div       = document.createElement("div");
            div.className = "search-dropdown-item";

            var typeBadge = item.type
                ? '<span class="search-dropdown-badge search-dropdown-badge--' + item.type + '">' + item.type + '</span>'
                : '';

            var statusBadge = item.status
                ? '<span class="search-dropdown-badge search-dropdown-badge--' + item.status + '">' + item.status.replace("-", " ") + '</span>'
                : '';

            var shortDesc = item.descDisplay.length > 60
                ? item.descDisplay.substring(0, 60) + "..."
                : item.descDisplay;

            div.innerHTML =
                '<span class="search-dropdown-name">' + highlightMatch(item.nameDisplay, keyword) + '</span>' +
                '<span class="search-dropdown-desc">' + highlightMatch(shortDesc, keyword)        + '</span>' +
                '<div  class="search-dropdown-meta">' + typeBadge + statusBadge                   + '</div>';

            div.addEventListener("click", function () {
                searchBox.value              = item.nameDisplay;
                searchDropdown.style.display = "none";
                applyFilters();
            });

            searchDropdown.appendChild(div);
        });

        searchDropdown.style.display = "block";
    }


    // =============================================
    // UPDATE VISIBLE COUNT
    // =============================================

    function updateCount() {
        var count = 0;
        document.querySelectorAll(".dash-item-card").forEach(function (card) {
            if (card.style.display !== "none") count++;
        });
        if (visibleCount) visibleCount.textContent = count;
    }


    // =============================================
    // APPLY SEARCH + FILTER
    // ✅ Removed item.type check — filter is
    //    Collected / Not Collected only now
    // =============================================

    function applyFilters() {
        var keyword  = searchBox    ? searchBox.value.toLowerCase().trim()    : "";
        var selected = filterStatus ? filterStatus.value.toLowerCase().trim() : "all";

        getAllItemData().forEach(function (item) {

            var matchesSearch =
                keyword === ""              ||
                item.name.includes(keyword) ||
                item.desc.includes(keyword);

            var matchesFilter =
                selected === "all"       ||
                item.status === selected;   // ✅ status only, no type check

            item.card.style.display = (matchesSearch && matchesFilter) ? "flex" : "none";
        });

        updateCount();
    }


    // =============================================
    // WIRE UP SEARCH BOX
    // =============================================

    if (searchBox) {

        searchBox.addEventListener("keyup", function () {
            var keyword = this.value.toLowerCase().trim();
            showDropdown(keyword);
            applyFilters();
        });

        // Hide dropdown on outside click
        document.addEventListener("click", function (e) {
            if (
                searchDropdown &&
                !searchBox.contains(e.target) &&
                !searchDropdown.contains(e.target)
            ) {
                searchDropdown.style.display = "none";
            }
        });

        // Keyboard navigation
        searchBox.addEventListener("keydown", function (e) {
            if (!searchDropdown) return;

            var dropItems = searchDropdown.querySelectorAll(".search-dropdown-item");
            var active    = searchDropdown.querySelector(".search-dropdown-item.active");

            if (e.key === "ArrowDown") {
                e.preventDefault();
                if (!active && dropItems.length > 0) {
                    dropItems[0].classList.add("active");
                    dropItems[0].style.background = "#f5eeee";
                } else if (active && active.nextElementSibling) {
                    active.classList.remove("active");
                    active.style.background                     = "";
                    active.nextElementSibling.classList.add("active");
                    active.nextElementSibling.style.background  = "#f5eeee";
                }
            }

            if (e.key === "ArrowUp") {
                e.preventDefault();
                if (active && active.previousElementSibling) {
                    active.classList.remove("active");
                    active.style.background                         = "";
                    active.previousElementSibling.classList.add("active");
                    active.previousElementSibling.style.background  = "#f5eeee";
                }
            }

            if (e.key === "Enter") {
                if (active) {
                    active.click();
                } else {
                    searchDropdown.style.display = "none";
                    applyFilters();
                }
            }

            if (e.key === "Escape") {
                searchDropdown.style.display = "none";
            }
        });
    }


    // =============================================
    // WIRE UP FILTER DROPDOWN
    // =============================================

    if (filterStatus) {
        filterStatus.addEventListener("change", applyFilters);
    }

    // Set correct count on page load
    updateCount();


    // =============================================
    // SUBMISSION TYPE TOGGLE (add_item page only)
    // =============================================

    var submissionType = document.querySelector("[name='submission_type']");
    var locationField  = document.getElementById("locationField");

    if (submissionType && locationField) {
        function toggleLocation() {
            locationField.style.display =
                submissionType.value === "desk" ? "block" : "none";
        }
        toggleLocation();
        submissionType.addEventListener("change", toggleLocation);
    }

}); // end DOMContentLoaded


// =============================================
// IMAGE ZOOM MODAL
// (outside DOMContentLoaded — uses window.onclick
//  which fires after full load anyway)
// =============================================

function openImage(src) {
    var modal    = document.getElementById("imageModal");
    var modalImg = document.getElementById("modalImg");
    if (!modal || !modalImg) return;
    modalImg.src        = src;
    modal.style.display = "flex";
}

function closeImage() {
    var modal = document.getElementById("imageModal");
    if (!modal) return;
    modal.style.display = "none";
    document.getElementById("modalImg").src = "";
}

window.addEventListener("click", function (e) {
    var modal = document.getElementById("imageModal");
    if (modal && e.target === modal) closeImage();
});

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeImage();
});