import streamlit as st
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Cognivis OS | Dual Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling to make Streamlit feel like a dark OS
st.markdown("""
    <style>
        .stApp {
            background-color: #020617;
            color: #f8fafc;
        }
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        .zatca-card {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(34, 197, 94, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 3D Scene HTML/JS String
three_js_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; overflow: hidden; background: transparent; }
        canvas { width: 100vw; height: 400px; display: block; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <script>
        let scene, camera, renderer, core, shield;
        
        function init() {
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, window.innerWidth / 400, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, 400);
            document.body.appendChild(renderer.domElement);

            // The Core
            const coreGeo = new THREE.IcosahedronGeometry(1.5, 1);
            const coreMat = new THREE.MeshPhongMaterial({ 
                color: 0x22d3ee, 
                wireframe: true,
                transparent: true,
                opacity: 0.4
            });
            core = new THREE.Mesh(coreGeo, coreMat);
            scene.add(core);

            // The Shield
            const shieldGeo = new THREE.SphereGeometry(2.2, 32, 32);
            const shieldMat = new THREE.MeshPhongMaterial({
                color: 0x059669,
                transparent: true,
                opacity: 0.1,
                side: THREE.BackSide
            });
            shield = new THREE.Mesh(shieldGeo, shieldMat);
            scene.add(shield);

            const light = new THREE.PointLight(0x22d3ee, 2, 100);
            light.position.set(5, 5, 5);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x404040));

            camera.position.z = 6;
            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            core.rotation.y += 0.005;
            core.rotation.x += 0.002;
            shield.rotation.y -= 0.001;
            renderer.render(scene, camera);
        }
        
        init();
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / 400;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, 400);
        });
    </script>
</body>
</html>
"""

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("COGNIVIS OS")
st.sidebar.markdown("---")
selection = st.sidebar.radio(
    "Navigation",
    ["🛡️ ZATCA Shield", "🧠 Profit Insights", "⚙️ Settings"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("System Status: **Secure**")

# --- MAIN CONTENT LOGIC ---

if selection == "🛡️ ZATCA Shield":
    st.title("ZATCA Regulatory Shield")
    st.subheader("Real-time Compliance Monitoring")
    
    # Embed the 3D Scene at the top of the ZATCA section
    components.html(three_js_code, height=400)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Phase 2 Readiness", "100%", delta="Verified")
    with col2:
        st.metric("Sequence Integrity", "Valid", delta="0 Errors")
    with col3:
        st.metric("Pending Uploads", "0", delta="-12", delta_color="normal")
    
    st.markdown("### Recent Transactions")
    st.table([
        {"Invoice ID": "INV-2024-001", "Status": "Success", "ZATCA Hash": "9a8b...2c1d"},
        {"Invoice ID": "INV-2024-002", "Status": "Success", "ZATCA Hash": "4f5e...8g9h"},
        {"Invoice ID": "INV-2024-003", "Status": "Verifying...", "ZATCA Hash": "Pending"},
    ])

elif selection == "🧠 Profit Insights":
    st.title("The Brain: Profit Intelligence")
    st.markdown("### Mistral AI Business Advisory")
    
    with st.chat_message("assistant"):
        st.write("Ahmed, I noticed your **Chicken Burger** margins dropped by 12% in Riyadh Branch. This coincides with a 15% increase in poultry supplier costs. Recommend adjusting price to 24 SAR.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="zatca-card">
            <h4>Stock Velocity</h4>
            <p>Your <b>Almarai Milk (1L)</b> is moving 4x faster than last week. Suggest increasing order volume by 20%.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class="zatca-card">
            <h4>Micro-Theft Alert</h4>
            <p>Shift B shows 4 'Void' transactions at the same terminal between 2PM-3PM. Investigating patterns...</p>
        </div>
        """, unsafe_allow_html=True)

elif selection == "⚙️ Settings":
    st.title("System Configuration")
    st.text_input("ZATCA API Key", type="password")
    st.text_input("Store Location ID")
    st.toggle("Enable Mistral AI Real-time Advice", value=True)
    st.button("Run Compliance Audit")
