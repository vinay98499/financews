import streamlit as st
import streamlit.components.v1 as components

st.title("WebSocket Data via JavaScript")

ws_js = """
<script>
    let output = document.getElementById("output");
    function log(msg) {
        if (output) {
            output.innerText += "\\n" + msg;
        }
        console.log(msg);
    }
    const ws = new WebSocket("ws://localhost:8000");
    ws.onopen = function() {
        log("WebSocket connection opened");
    };
    ws.onmessage = function(event) {
        log("Received from relay: " + event.data);
        try {
            const data = JSON.parse(event.data);
            output.innerText = JSON.stringify(data, null, 2);
        } catch (e) {
            log("Error parsing data: " + e);
        }
    };
    ws.onerror = function(error) {
        log("WebSocket error: " + error);
    };
    ws.onclose = function() {
        log("WebSocket connection closed.");
    };
</script>
<div id="output">Waiting for data...</div>
"""

components.html(ws_js, height=300)
