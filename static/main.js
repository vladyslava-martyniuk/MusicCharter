function searchMusic() {
    const query = document.getElementById("searchInput").value;

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("musicBody");
            tbody.innerHTML = "";

            if (data.results.length === 0) {
                tbody.innerHTML = "<tr><td colspan='3'>Нічого не знайдено.</td></tr>";
            } else {
                data.results.forEach(item => {
                    const row = document.createElement("tr");

                    row.innerHTML = `
                        <td>${item.title}</td>
                        <td>${item.artist}</td>
                        <td>
                            <a href="/edit/${item.id}">Редагувати</a>
                            <form action="/delete/${item.id}" method="post" style="display:inline;">
                                <button type="submit" onclick="return confirm('Ви дійсно хочете видалити цей трек?');">
                                    Видалити
                                </button>
                            </form>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        });
}