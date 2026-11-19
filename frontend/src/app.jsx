import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

function App() {
    const [user, setUser] = useState(null);
    const [devices, setDevices] = useState([]);
    const [hostname, setHostname] = useState("");
    const [ipAddress, setIpAddress] = useState("");

    useEffect(() => {
        fetch(`${API_URL}/auth/me`, { credentials: "include" })
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                setUser(data);
                if (data) fetchDevices();});}, []);

    const fetchDevices = async () => {
        const res = await fetch(`${API_URL}/api/devices`, { credentials: "include" });
        if (res.ok) setDevices(await res.json());};

    const handleAdd = async (e) => {
        e.preventDefault();
        if (!hostname || !ipAddress) return;
        await fetch(`${API_URL}/api/devices`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ hostname, ip_address: ipAddress }),});
        setHostname("");
        setIpAddress("");
        fetchDevices();};

    const handleDelete = async (id) => {
        await fetch(`${API_URL}/api/devices/${id}`, {
            method: "DELETE",
            credentials: "include",});
        fetchDevices();};

    const handleLogout = async () => {
        await fetch(`${API_URL}/auth/logout`, { credentials: "include" });
        setUser(null);
        setDevices([]);};

    if (!user) {
        return (
            <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
                <h1>Network Lab Tracker</h1>
                <p>Authenticate via OAuth 2.0 to manage your lab inventory.</p>
                <a href={`${API_URL}/auth/login`}>
                    <button style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}>
                        Sign in with Google
                    </button>
                </a>
            </div>);}

    return (
        <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "600px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h2>Welcome, {user.name}</h2>
                <button onClick={handleLogout}>Logout</button>
            </div>
            <form onSubmit={handleAdd} style={{ margin: "1.5rem 0", display: "flex", gap: "10px" }}>
                <input
                    placeholder="Hostname (e.g., Core-SW1)"
                    value={hostname}
                    onChange={(e) => setHostname(e.target.value)}
                />
                <input
                    placeholder="IP Address (e.g., 192.168.10.1)"
                    value={ipAddress}
                    onChange={(e) => setIpAddress(e.target.value)}
                />
                <button type="submit">Add Device</button>
            </form>
            <ul>
                {devices.map((d) => (
                    <li key={d.id} style={{ marginBottom: "8px" }}>
                        <strong>{d.hostname}</strong> — {d.ip_address}{" "}
                        <button onClick={() => handleDelete(d.id)} style={{ marginLeft: "10px" }}>
                            Delete
                        </button>
                    </li>))}
            </ul>
        </div>);}

export default App;