import streamlit as st
import streamlit.components.v1 as components

st.title("WebSocket Data via JavaScript")

ws_js = """
<script>
    // Connect to relay server (no /ws path)
    const ws = new WebSocket("ws://localhost:8000");
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    };
    ws.onopen = function() {
        console.log("WebSocket connection opened");
    };
    ws.onerror = function(error) {
        document.getElementById("output").innerText = "WebSocket error: " + error;
        console.log("WebSocket error: ", error);
    };
    ws.onclose = function() {
        document.getElementById("output").innerText = "WebSocket connection closed.";
    };
</script>
<div id="output">Waiting for data...</div>
"""

components.html(ws_js, height=300)
