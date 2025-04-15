function toggleProfile(profileElement) {
    const bio = profileElement.querySelector(".bio");
    if (bio.style.display === "block") {
        bio.style.display = "none";
    } else {
        bio.style.display = "block";
    }
}
