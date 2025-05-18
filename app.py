import os
import streamlit as st
from stl import mesh
import trimesh
import numpy as np
import plotly.graph_objects as go
import tempfile
from groq import Groq

# ── Groq client ──────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="AI‑Powered 3D File Analyzer", layout="wide")
st.title("🧠 AI‑Powered 3D File Analyzer")

# ── Sidebar: upload & details ────────────────────────────────
st.sidebar.header("Upload & Model Details")

uploaded_file = st.sidebar.file_uploader(
    "Upload a 3D file (OBJ)", type=["stl", "obj"]
)

# Extra metadata inputs
st.sidebar.markdown("### Additional Info")
model_desc = st.sidebar.text_area(
    "Describe your model and its use case",
    placeholder="e.g. This is a spoiler for a car prototype…",
)
material = st.sidebar.selectbox("Material", ["", "Plastic", "Metal", "Resin", "Composite", "Other"])
methods = st.sidebar.multiselect(
    "Target Manufacturing Methods",
    ["3D Printing", "CNC Machining", "Injection Molding", "Casting"],
)
goal = st.sidebar.radio(
    "Analysis Goal",
    [
        "Prototyping",
        "Mass Production",
        "General recommendations for manufacturing",
    ],
)

# ── File processing ──────────────────────────────────────────
data = None
file_info = {}
validation_message = None

if uploaded_file:
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        if uploaded_file.name.endswith(".stl"):
            stl_mesh = mesh.Mesh.from_file(tmp_path)
            vertices = stl_mesh.vectors.reshape(-1, 3)
            faces = np.arange(len(vertices)).reshape(-1, 3)
            data = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        elif uploaded_file.name.endswith(".obj"):
            data = trimesh.load(tmp_path, file_type="obj")

        if data:
            file_info = {
                "File Size (KB)": f"{uploaded_file.size / 1024:.2f}",
                "Vertices": len(data.vertices),
                "Faces": len(data.faces),
            }
            validation_message = (
                ("The mesh is watertight!", "success")
                if data.is_watertight
                else ("The mesh has holes or non‑manifold edges.", "warning")
            )
    except Exception as e:
        st.sidebar.error(f"Error processing file: {e}")

# ── Sidebar info ─────────────────────────────────────────────
if file_info:
    st.sidebar.markdown("### File Information")
    for k, v in file_info.items():
        st.sidebar.write(f"**{k}:** {v}")
if validation_message:
    getattr(st.sidebar, validation_message[1])(validation_message[0])

# ── Main area ────────────────────────────────────────────────
if data:

    # 3D viewer
    st.subheader("🖼️ 3D Model Viewer")

    # Prepare mesh3d trace for model (smooth shading)
    mesh_trace = go.Mesh3d(
        x=data.vertices[:, 0],
        y=data.vertices[:, 1],
        z=data.vertices[:, 2],
        i=data.faces[:, 0],
        j=data.faces[:, 1],
        k=data.faces[:, 2],
        color="darkgrey",
        opacity=1.0,
        flatshading=False,  # smooth shading
        showscale=False,
        lighting=dict(ambient=0.5, diffuse=0.7, fresnel=0.2, specular=0.5, roughness=0.3),
        lightposition=dict(x=100, y=200, z=0),
    )

    fig = go.Figure(data=[mesh_trace])

    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            zaxis=dict(showgrid=False, zeroline=False, visible=False),
            aspectmode="data",
            bgcolor="white",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # AI analysis
    st.subheader("🔍 AI Analysis & Manufacturing Guidance")
    if st.button("Analyze 3D File"):
        prompt = f"""
You are an expert manufacturing consultant. Based on the provided 3D model and analysis goal, provide clear, actionable guidance on the best manufacturing technology, sub-technology (if applicable), and material to use. Also discuss the manufacturing cost.
If the user has not specified manufacturing methods or material, recommend the most suitable options based on the analysis goal and model geometry.
Dont just throw words, mention specific technology name with the material name in the final recommendation based on your knowledge at the end.
If user selected manufacturing method and material is not feasible for the selected goal. mention straight forward that it is not recommended and give alternative manufacturing method and material with proper explanation.
Try to choose standard material which are popular and available.
Make headings as needed.
Focus on the chosen analysis goal: "{goal}".
Here is the provided information:
- Model Description: {model_desc or "No description provided"}
- Target Manufacturing Methods Selected: {', '.join(methods) if methods else "None selected"}
- Material Selected: {material if material else "None selected"}
- Model Geometry:
  - Vertices: {file_info.get('Vertices')}
  - Faces: {file_info.get('Faces')}
- Analysis Goal: {goal}
Provide your guidance in concise bullet points or numbered list.
"""

        output_area = st.empty()
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            full_resp = ""
            for chunk in stream:
                delta = getattr(chunk.choices[0].delta, "content", "")
                full_resp += delta or ""
                output_area.markdown(full_resp)
        except Exception as e:
            st.error(f"Error during AI analysis: {e}")
else:
    st.info("Upload a 3D STL or OBJ file to start.")
