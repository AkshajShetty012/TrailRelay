const DB_NAME = "trailrelay-db";
const DB_VERSION = 1;
const STORE_NAME = "reports";

const form = document.querySelector("#report-form");
const noteInput = document.querySelector("#report-note");
const submitButton = document.querySelector("#submit-button");
const connectionStatus = document.querySelector("#connection-status");
const queueCount = document.querySelector("#queue-count");
const queueMessage = document.querySelector("#queue-message");
const reportList = document.querySelector("#report-list");
const appMessage = document.querySelector("#app-message");

let db;

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onupgradeneeded = () => {
            const database = request.result;

            if (!database.objectStoreNames.contains(STORE_NAME)) {
                database.createObjectStore(STORE_NAME, {
                    keyPath: "id",
                });
            }
        };

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

function saveReport(report) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readwrite");
        const store = transaction.objectStore(STORE_NAME);

        store.add(report);

        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
        transaction.onabort = () => {
            reject(transaction.error || new Error("Saving was cancelled."));
        };
    });
}

function getAllReports() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readonly");
        const request = transaction.objectStore(STORE_NAME).getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}


function deleteReport(id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readwrite");
        transaction.objectStore(STORE_NAME).delete(id);

        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
        transaction.onabort = () => {
            reject(transaction.error || new Error("Delete was cancelled."));
        };
    });
}
function updateConnectionStatus() {
    const online = navigator.onLine;

    connectionStatus.textContent = online
        ? "Online · Reports saved locally"
        : "Offline · Reports saved locally";

    connectionStatus.setAttribute(
        "aria-label",
        online ? "Browser reports an online connection" : "Browser is offline"
    );
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function renderReports(reports) {
    queueCount.textContent = reports.length;
    queueMessage.textContent = reports.length
        ? "Saved on this device. Server syncing is not enabled yet."
        : "No reports saved on this device yet.";

    reportList.replaceChildren();

    for (const report of reports) {
        const item = document.createElement("li");
        item.className = "report-item";

        const description = document.createElement("p");
        description.textContent = report.note;

        const metadata = document.createElement("small");
        metadata.textContent = `Saved locally · ${formatDate(report.createdAt)}`;

        item.append(description, metadata);
        reportList.append(item);
    }
}

async function refreshReports() {
    const reports = await getAllReports();

    reports.sort((a, b) => b.createdAt - a.createdAt);
    renderReports(reports);
}


let isSyncing = false;

async function syncPendingReports() {
    if (!db || !navigator.onLine || isSyncing) return;

    isSyncing = true;

    try {
        const reports = await getAllReports();

        for (const report of reports) {
            if (!navigator.onLine) break;

            appMessage.textContent = "Syncing a saved report…";

            try {
                const response = await fetch(
                    "http://127.0.0.1:8000/reports",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            id: report.id,
                            note: report.note,
                        }),
                    }
                );

                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}`);
                }

                await deleteReport(report.id);
            } catch (error) {
                console.error("Report sync failed:", error);
                appMessage.textContent =
                    "A report is still saved locally. Sync will retry later.";
                break;
            }
        }

        await refreshReports();

        const remaining = (await getAllReports()).length;

        if (remaining === 0) {
            appMessage.textContent = reports.length
                ? "All saved reports have been processed successfully."
                : "No pending reports to sync.";
        }
    } finally {
        isSyncing = false;
    }
}
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const note = noteInput.value.trim();

    if (!note) {
        appMessage.textContent = "Please describe the hazard first.";
        return;
    }

    submitButton.disabled = true;
    appMessage.textContent = "Saving report on this device…";

    const report = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        note,
        createdAt: Date.now(),
        status: "pending",
    };

    try {
        await saveReport(report);
        await refreshReports();

        form.reset();
        appMessage.textContent =
            "Report saved on this device. Checking whether it can sync…";
        
        if (navigator.onLine) {
            await syncPendingReports();
        }
    } catch (error) {
        console.error("Could not save report:", error);
        appMessage.textContent =
            "Could not save the report. Please try again.";
    } finally {
        submitButton.disabled = false;
    }
});


window.addEventListener("online", () => {
    updateConnectionStatus();
    syncPendingReports();
});

window.addEventListener("offline", updateConnectionStatus);

async function initializeApp() {
    updateConnectionStatus();

    try {
        if (!("indexedDB" in window)) {
            throw new Error("IndexedDB is unavailable in this browser.");
        }

        db = await openDatabase();
        await refreshReports();
        
        if (navigator.onLine) {
            await syncPendingReports();
        }
    } catch (error) {
        console.error("Could not initialize local storage:", error);
        appMessage.textContent =
            "Local storage could not be initialized. Try opening this page through localhost.";
        submitButton.disabled = true;
    }
}

initializeApp();