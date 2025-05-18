# 🧠 AI‑Powered 3D File Analyzer

A Streamlit-based web app that lets users upload 3D files (STL/OBJ), visualize the model interactively, and receive manufacturing recommendations using AI (Groq LLaMA 3.3 70B). Ideal for designers, engineers, and prototypers looking for quick manufacturability analysis and guidance.

---

## 🚀 Features

- 📂 Upload `.stl` or `.obj` 3D files
- 🔍 Display key mesh info: vertices, faces, watertightness
- 🎨 Interactive 3D model viewer using Plotly
- 🧠 AI-powered analysis via Groq API (LLaMA 3.3 70B):
  - Manufacturing recommendations
  - Material suggestions
  - Cost guidance
- 📝 User input for model description, material, and manufacturing methods

---

## 📸 Screenshot

![3D Analyzer Demo](assets/demo.png) <!-- Replace with your own screenshot path -->

---

## 🧰 Tech Stack

- [Streamlit](https://streamlit.io/)
- [Trimesh](https://trimsh.org/)
- [NumPy-STL](https://pypi.org/project/numpy-stl/)
- [Plotly](https://plotly.com/python/)
- [Groq SDK](https://github.com/groq/groq-python)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/3d-file-analyzer.git
cd 3d-file-analyzer
