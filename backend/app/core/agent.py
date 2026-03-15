import pandas as pd
import openai
import os
from typing import Dict, Any

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
        
        # Time Series
        time_cols = [c for c in df.columns if any(key in c.lower() for key in ["date", "year", "month", "time", "day", "orderdate"])]
        # Category tracking
        top_cats = [c for c in cat_df.columns if df[c].nunique() < 30]
        
        # Trend over time (Area/Line)
        if time_cols and found_hero_cols:
            for i, t_col in enumerate(time_cols[:2]):
                if i < len(found_hero_cols):
                    visualizations.append({
                        "title": f"{found_hero_cols[i]} Trend by {t_col}",
                        "viz": "area" if i == 0 else "line",
                        "data": self._clean_data(df.groupby(t_col)[found_hero_cols[i]].sum().reset_index().sort_values(t_col)),
                        "metadata": {"x": t_col, "y": found_hero_cols[i]}
                    })

        # Distribution/Composition (Pie)
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
            
        # Comparisons (Bar)
        if len(top_cats) > 2 and found_hero_cols:
            c_col = top_cats[2]
            h_col = found_hero_cols[0]
            visualizations.append({
                "title": f"Top segments in {c_col} by {h_col}",
                "viz": "bar",
                "data": self._clean_data(df.groupby(c_col)[h_col].sum().reset_index().nlargest(12, h_col)),
                "metadata": {"x": c_col, "y": h_col}
            })

        # Correlation (Scatter)
        if len(found_hero_cols) >= 2:
            visualizations.append({
                "title": f"Correlation: {found_hero_cols[0]} vs {found_hero_cols[1]}",
                "viz": "scatter",
                "data": self._clean_data(df[[found_hero_cols[0], found_hero_cols[1]]].dropna().head(200)),
                "metadata": {"x": found_hero_cols[0], "y": found_hero_cols[1]}
            })

        return {
            "metrics": metrics,
            "visualizations": visualizations
        }

    def analyze_query(self, query: str, df: pd.DataFrame) -> Dict[str, Any]:
        query_lower = query.lower()
        cols = list(df.columns)
        
        # Detect if asking for the initial summary/dashboard
        if any(word in query_lower for word in ["kpi", "metrics", "summary", "dashboard", "overall", "full profile"]):
            profile = self.profile_dataset(df)
            return {
                "answer": "Dashboard synthesized. Neural profiling has identified these key insights and trends across your dataset.",
                "viz": "dashboard",
                "data": profile,
                "metadata": {"rows": len(df)}
            }
        
        # Viz detection
        viz_type = "bar"
        if any(word in query_lower for word in ["pie", "ratio", "breakdown", "distribution", "proportion"]):
            viz_type = "pie"
        elif any(word in query_lower for word in ["trend", "line", "over time", "history", "area", "growth"]):
            viz_type = "line" if "area" not in query_lower else "area"
        elif any(word in query_lower for word in ["scatter", "correlation", "relationship", "versus", "vs"]):
            viz_type = "scatter"
        elif any(word in query_lower for word in ["list", "table", "raw", "data"]):
            viz_type = "table"

        # Column identification
        found_cols = [c for c in cols if c.lower() in query_lower]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        
        # Logic to find the best match for X and Y axes
        target_cat = next((c for c in found_cols if c in cat_cols), None)
        target_num = next((c for c in found_cols if c in numeric_cols), None)
        
        # Fallbacks
        if not target_cat:
            time_cols = [c for c in cat_cols if any(k in c.lower() for k in ["date", "year", "month", "time"])]
            target_cat = time_cols[0] if time_cols else (cat_cols[0] if cat_cols else None)
        
        if not target_num:
            target_num = numeric_cols[0] if numeric_cols else None

        result = {}
        if target_cat and target_num:
            try:
                if viz_type == "scatter":
                    target_num2 = next((c for c in found_cols if c in numeric_cols and c != target_num), None)
                    if not target_num2 and len(numeric_cols) > 1:
                        target_num2 = numeric_cols[1]
                    
                    if target_num2:
                        result_df = df[[target_num, target_num2]].dropna().head(300)
                        result = {
                            "answer": f"Displaying correlation between {target_num} and {target_num2}.",
                            "viz": "scatter",
                            "data": result_df,
                            "metadata": {"x": target_num, "y": target_num2}
                        }
                else:
                    # Grouping logic
                    result_df = df.groupby(target_cat)[target_num].sum().reset_index()
                    if viz_type in ["line", "area"]:
                        result_df = result_df.sort_values(target_cat)
                    else:
                        result_df = result_df.nlargest(20, target_num)
                        
                    result = {
                        "answer": f"Synthesized analysis of {target_num} by {target_cat}.",
                        "viz": viz_type,
                        "data": result_df,
                        "metadata": {"x": target_cat, "y": target_num}
                    }
            except Exception as e:
                print(f"Agent error: {e}")

        if not result:
            result = {
                "answer": "Processing failure for specific dimensions. Providing raw data projection instead.",
                "viz": "table",
                "data": df.head(15),
                "metadata": {"rows": len(df)}
            }

        return self._clean_data(result)

agent = BIAgent()
