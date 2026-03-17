import pandas as pd
import openai
import os
import json
import re
from typing import Dict, Any, List

class BIAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def _clean_data(self, data: Any) -> Any:
        """Sanitize data for JSON serialization (Replace NaN/Inf with None)."""
        if isinstance(data, pd.DataFrame):
            return data.where(pd.notnull(data), None).to_dict(orient='records')
        elif isinstance(data, list):
            return [self._clean_data(i) for i in data]
        elif isinstance(data, dict):
            return {k: self._clean_data(v) for k, v in data.items()}
        elif isinstance(data, float):
            import math
            if math.isnan(data) or math.isinf(data):
                return None
        return data

    def profile_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Autonomously identify best KPIs and Visualizations for a new dataset."""
        numeric_df = df.select_dtypes(include=['number'])
        cat_df = df.select_dtypes(exclude=['number'])
        
        # 1. Identify Hero Metrics (KPIs)
        metrics = []
        priority_keywords = ["sales", "revenue", "profit", "amount", "price", "quantity", "rating", "score", "total", "cost"]
        
        found_hero_cols = []
        for col in numeric_df.columns:
            if any(key in col.lower() for key in priority_keywords):
                found_hero_cols.append(col)
        
        if not found_hero_cols:
            found_hero_cols = numeric_df.columns[:5].tolist()
            
        for col in found_hero_cols[:4]:
            agg = "sum"
            if any(key in col.lower() for key in ["rating", "score", "price", "ratio", "percent"]):
                agg = "mean"
            
            val = float(numeric_df[col].sum() if agg == "sum" else numeric_df[col].mean())
            metrics.append({
                "label": f"{agg.capitalize()} {col}",
                "value": val,
                "agg": agg
            })

        # 2. Identify Primary Visualizations
        visualizations = []
        time_cols = [c for c in df.columns if any(key in c.lower() for key in ["date", "year", "month", "time", "day", "orderdate"])]
        top_cats = [c for c in cat_df.columns if df[c].nunique() < 30]
        
        if time_cols and found_hero_cols:
            for i, t_col in enumerate(time_cols[:2]):
                if i < len(found_hero_cols):
                    visualizations.append({
                        "title": f"{found_hero_cols[i]} Trend by {t_col}",
                        "viz": "area" if i == 0 else "line",
                        "data": self._clean_data(df.groupby(t_col)[found_hero_cols[i]].sum().reset_index().sort_values(t_col)),
                        "metadata": {"x": t_col, "y": found_hero_cols[i]}
                    })

        if top_cats and found_hero_cols:
            for i, c_col in enumerate(top_cats[:2]):
                viz_type = "pie" if df[c_col].nunique() <= 10 else "bar"
                h_col = found_hero_cols[min(i + 1, len(found_hero_cols)-1)]
                visualizations.append({
                    "title": f"{h_col} Breakdown by {c_col}",
                    "viz": viz_type,
                    "data": self._clean_data(df.groupby(c_col)[h_col].sum().reset_index().nlargest(10, h_col)),
                    "metadata": {"x": c_col, "y": h_col}
                })
            
        return {
            "metrics": metrics,
            "visualizations": visualizations
        }

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call LLM to get structured insight strategy."""
        if not self.api_key:
            return None
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional Data Analyst. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"} if hasattr(openai, 'ChatCompletion') else None
            )
            content = response.choices[0].message.content
            # Basic JSON extraction in case it's wrapped in markdown
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def analyze_query(self, query: str, df: pd.DataFrame) -> Dict[str, Any]:
        query_lower = query.lower()
        
        # More robust keyword matching for profiling fallback (includes typos like 'dashbord')
        kpi_keywords = ["kpi", "metrics", "summary", "dashboard", "dashbord", "overall", "profile", "overview"]
        if any(word in query_lower for word in kpi_keywords):
            profile = self.profile_dataset(df)
            return {
                "answer": "Dashboard synthesized. Neural profiling has identified these key insights and trends across your dataset.",
                "viz": "dashboard",
                "data": profile,
                "metadata": {"rows": len(df)}
            }

        # Context for LLM
        cols_info = {col: str(df[col].dtype) for col in df.columns}
        cat_samples = {col: df[col].dropna().unique()[:5].tolist() for col in df.select_dtypes(exclude=['number']).columns[:10]}
        
        prompt = f"""
        User Question: "{query}"
        Dataset Columns: {cols_info}
        Category Samples: {cat_samples}
        
        Act as a Data Scientist. Plan a multi-visualization dashboard to answer this question.
        Return a JSON object with:
        "summary": A brief textual answer to the query.
        "vizzes": A list of objects, each with:
          - "type": "bar", "line", "area", "pie", "scatter", or "table"
          - "title": A descriptive title
          - "x": The column for X-axis
          - "y": The column for Y-axis (numeric)
          - "agg": "sum", "mean", or "count"
          - "filter": Optional string for filtering (e.g. "Region == 'West'")
        """
        
        intent = self._call_llm(prompt)
        
        if not intent or "vizzes" not in intent:
            # Fallback to legacy logic or simple table
            return {
                "answer": "I've processed your request. Here is a view of the relevant data.",
                "viz": "table",
                "data": df.head(15),
                "metadata": {"rows": len(df)}
            }

        visualizations = []
        for v in intent["vizzes"][:4]:  # Max 4 vizzes for clarity
            try:
                working_df = df.copy()
                # Simple filter application if provided (e.g. "Region == 'West'")
                # We use a very cautious approach to avoid invalid code execution
                if v.get("filter"):
                    try:
                        # Only support simple equality or inequality for now
                        # LLM might return "Region == 'West'" or "Year == 2023"
                        f = v["filter"]
                        if '==' in f:
                            f_col, f_val = [x.strip() for x in f.split('==')]
                            f_val = f_val.strip("'\"")
                            if f_col in working_df.columns:
                                # Convert to numeric if possible for comparison
                                if pd.api.types.is_numeric_dtype(working_df[f_col]):
                                    try: f_val = float(f_val)
                                    except: pass
                                working_df = working_df[working_df[f_col] == f_val]
                    except:
                        pass
                
                x, y, agg = v.get("x"), v.get("y"), v.get("agg", "sum")
                
                if x not in df.columns or (y not in df.columns and agg != "count"):
                    continue

                if agg == "count":
                    viz_data = working_df.groupby(x).size().reset_index(name="Count").nlargest(15, "Count")
                    y = "Count"
                else:
                    viz_data = working_df.groupby(x)[y].agg(agg).reset_index()
                    if v["type"] in ["line", "area"]:
                        viz_data = viz_data.sort_values(x)
                    else:
                        viz_data = viz_data.nlargest(15, y)
                
                visualizations.append({
                    "title": v["title"],
                    "viz": v["type"],
                    "data": self._clean_data(viz_data),
                    "metadata": {"x": x, "y": y}
                })
            except:
                continue

        if not visualizations:
            return {
                "answer": "I understood your request but could not map it to visual dimensions. Here is a data projection.",
                "viz": "table",
                "data": df.head(15)
            }

        return {
            "answer": intent.get("summary", "Synthesis complete."),
            "viz": "dashboard", # Trigger multi-viz mode
            "data": {
                "metrics": [], # Could be populated by LLM too
                "visualizations": visualizations
            }
        }

    def generate_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Generate dynamic suggestion prompts based on the dataset schema."""
        cols_info = {col: str(df[col].dtype) for col in df.columns}
        cat_samples = {col: df[col].dropna().unique()[:5].tolist() for col in df.select_dtypes(exclude=['number']).columns[:5]}
        
        prompt = f"""
        Dataset Columns: {cols_info}
        Category Samples: {cat_samples}
        
        Act as a Data Analyst. Based on this dataset schema, suggest 5 diverse and insightful natural language questions a user might want to ask.
        The questions should cover:
        1. A high-level summary (e.g., "Give me a summary of...")
        2. A trend over time (if date columns exist)
        3. A comparison between categories
        4. Performance of top items
        5. A correlation or breakdown question.
        
        Return a JSON object with:
        "suggestions": ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        """
        
        intent = self._call_llm(prompt)
        if intent and "suggestions" in intent:
            return intent["suggestions"]
        
        # Fallback suggestions based on profiling
        profile = self.profile_dataset(df)
        fallbacks = ["Show me a dashboard of overall metrics"]
        for viz in profile.get("visualizations", []):
            fallbacks.append(viz["title"])
        return fallbacks[:5]

agent = BIAgent()
