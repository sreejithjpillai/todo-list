// Fetch and display all active tasks
async function fetchTasks() {
  try {
    let res = await fetch("/tasks");
    if (!res.ok) throw new Error("Failed to fetch tasks");
    let tasks = await res.json();

    let list = document.getElementById("taskList");
    list.innerHTML = "";

    tasks.forEach(t => {
      let li = document.createElement("li");
      li.innerHTML = `
        <span>${t.task}</span>
        <button onclick="markComplete(${t.id})">Complete</button>
        <button onclick="deleteTask(${t.id})">Delete</button>
      `;
      list.appendChild(li);
    });
  } catch (err) {
    console.error(err);
  }
}

// Fetch and display history tasks
async function fetchHistory() {
  try {
    let res = await fetch("/history");
    if (!res.ok) throw new Error("Failed to fetch history");
    let history = await res.json();

    let list = document.getElementById("historyList");
    list.innerHTML = "";

    history.forEach(h => {
      let li = document.createElement("li");
      li.innerHTML = `
        ${h.task} (${h.status}) - Deleted at ${h.deleted_at}
        <button onclick="deleteHistory(${h.id})">Delete</button>
      `;
      list.appendChild(li);
    });
  } catch (err) {
    console.error(err);
  }
}

// Add new task
async function addTask() {
  let taskInput = document.getElementById("taskInput");
  let task = taskInput.value.trim();
  if (!task) return alert("Please enter a task!");

  try {
    let res = await fetch("/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task })
    });
    if (!res.ok) throw new Error("Failed to add task");
    taskInput.value = "";
    fetchTasks();
  } catch (err) {
    console.error(err);
  }
}

// Mark task as completed and move to history
async function markComplete(id) {
  try {
    let res = await fetch(`/complete/${id}`, { method: "PUT" });
    if (!res.ok) throw new Error("Failed to complete task");
    fetchTasks();
    fetchHistory();
  } catch (err) {
    console.error(err);
  }
}

// Delete task (move to history)
async function deleteTask(id) {
  try {
    let res = await fetch(`/delete/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete task");
    fetchTasks();
    fetchHistory();
  } catch (err) {
    console.error(err);
  }
}

// Delete history permanently
async function deleteHistory(id) {
  try {
    let res = await fetch(`/history/delete/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete history item");
    fetchHistory();
  } catch (err) {
    console.error(err);
  }
}

// Load tasks and history on page load
window.onload = () => {
  fetchTasks();
  fetchHistory();
};
