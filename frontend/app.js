const API = "http://127.0.0.1:8000";

const ticketsContainer = document.querySelector("#tickets");
const message = document.querySelector("#message");
const filter = document.querySelector("#filter");
const PAGE_SIZE = 20;

let currentOffset = 0;
let totalTickets = 0;
let displayedStatus = filter.value;
let activeTicketsRequest = null;

const previousPage = document.querySelector("#previous-page");
const nextPage = document.querySelector("#next-page");
const pageInfo = document.querySelector("#page-info");


function updatePagination() {
    const currentPage =
        Math.floor(currentOffset / PAGE_SIZE) + 1;

    const totalPages = Math.max(
        1,
        Math.ceil(totalTickets / PAGE_SIZE)
    );

    pageInfo.textContent =
        `Страница ${currentPage} из ${totalPages}`;

    previousPage.disabled = currentOffset === 0;

    nextPage.disabled =
        currentOffset + PAGE_SIZE >= totalTickets;
}
const statuses = [
    "NEW",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED"
];

function showMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? "crimson" : "green";
}

async function apiRequest(path, options = {}) {
    let response;

    try {
        response = await fetch(API + path, options);
    } catch {
        throw new Error("Нет соединения с сервером HelpDesk");
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = typeof data?.detail === "string"
            ? data.detail
            : `HTTP ${response.status}`;

        throw new Error(detail);
    }

    return data;
}

async function loadTickets(offset = currentOffset) {
    const status = filter.value;
    if (status !== displayedStatus) {
        offset = 0;
    }

    const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(offset)
    });

    if (status) {
        params.set("status", status);
    }

    const request = apiRequest(`/tickets?${params}`);
    activeTicketsRequest = request;

    let page;
    try {
        page = await request;
    } catch (error) {
        if (activeTicketsRequest === request) {
            activeTicketsRequest = null;
            throw error;
        }
        return;
    }

    if (activeTicketsRequest !== request) {
        return;
    }
    activeTicketsRequest = null;

    const lastOffset = Math.max(
        0,
        Math.floor((page.total - 1) / PAGE_SIZE) * PAGE_SIZE
    );
    if (offset > lastOffset) {
        return loadTickets(lastOffset);
    }

    currentOffset = offset;
    totalTickets = page.total;
    displayedStatus = status;
    updatePagination();
    ticketsContainer.replaceChildren();

    if (page.items.length === 0) {
        ticketsContainer.textContent = "Заявок не найдено";
        return;
    }

    for (const ticket of page.items) {
        const card = document.createElement("article");

        const title = document.createElement("h3");
        title.textContent = ticket.title;

        const info = document.createElement("p");
        info.textContent =
            `ID: ${ticket.id} | Статус: ${ticket.status}`;

        const select = document.createElement("select");

        for (const status of statuses) {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            select.append(option);
        }

        select.value = ticket.status;

        const button = document.createElement("button");
        button.textContent = "Сохранить статус";

        button.addEventListener("click", async () => {
            const userId = document
                .querySelector("#operator")
                .value.trim();

            if (!userId) {
                showMessage("Укажите пользователя", true);
                return;
            }

            button.disabled = true;

            try {
                await apiRequest(
                    `/tickets/${encodeURIComponent(ticket.id)}`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            status: select.value,
                            user_id: userId
                        })
                    }
                );

                await loadTickets();
                showMessage("Статус обновлён");
            } catch (error) {
                showMessage(error.message, true);
            } finally {
                button.disabled = false;
            }
        });

        card.append(title, info, select, button);
        ticketsContainer.append(card);
    }
}

document.querySelector("#ticket-form")
    .addEventListener("submit", async (event) => {
        event.preventDefault();

        const form = event.currentTarget;
        const data = Object.fromEntries(
            new FormData(form).entries()
        );

        try {
            const ticket = await apiRequest("/tickets", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            await loadTickets();
            showMessage(`Создана заявка ${ticket.id}`);
        } catch (error) {
            showMessage(error.message, true);
        }
    });

function refreshTickets(offset) {
    loadTickets(offset).catch(error => {
        showMessage(error.message, true);
    });
}

function changePage(offset) {
    if (!activeTicketsRequest && offset >= 0 && offset < totalTickets) {
        refreshTickets(offset);
    }
}

document.querySelector("#refresh")
    .addEventListener("click", () => refreshTickets());

filter.addEventListener("change", () => refreshTickets(0));

previousPage.addEventListener("click", () => changePage(currentOffset - PAGE_SIZE));
nextPage.addEventListener("click", () => changePage(currentOffset + PAGE_SIZE));

refreshTickets();
