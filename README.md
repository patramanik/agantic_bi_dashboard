# Neural BI - AI-Powered Analytics Dashboard

This project is an AI-powered conversational business intelligence dashboard named **Neural BI**, developed for the GfG HackFest 2024.

## Project Structure
```text
/backend  - FastAPI server with AI logic and database
/frontend - React JS (Vite) application with Neural glassmorphic UI
```

## 1. Backend Setup (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   - **For PowerShell**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **For Git Bash / MINGW64**:
     ```bash
     python -m venv venv
     source venv/Scripts/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python run.py
   ```
   *The API will be available at `http://localhost:8000`*

## 2. Frontend Setup (React/Vite)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *The dashboard will be available at `http://localhost:3000`*

## 3. Usage Instructions
1. Upload a CSV or Excel file using the **Upload Data** button.
2. Once processed, use the **Chat Interface** to ask questions like:
   - "Show me total sales by category"
   - "What are the top 5 products by revenue?"
   - "Give me a trend line of monthly profits"
3. View the instant visualizations generated in the dashboard panels.

## 4. Sample Data
A file named `sample_data.csv` has been provided in the root directory. You can use this to quickly test the dashboard features!
