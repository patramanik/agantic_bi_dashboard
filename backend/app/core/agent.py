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
        # Priority columns
        priority_keywords = ["sales", "revenue", "profit", "amount", "price", "quantity", "rating", "score", "total"]
        
        found_hero_cols = []
        for col in numeric_df.columns:
            if any(key in col.lower() for key in priority_keywords):
                found_hero_cols.append(col)
        
        # Fallback to first 3 numeric if none found
        if not found_hero_cols:
            found_hero_cols = numeric_df.columns[:3].tolist()
            
        for col in found_hero_cols[:3]:
            # Guess aggregation
            agg = "sum"
            if any(key in col.lower() for key in ["rating", "score", "price", "ratio"]):
                agg = "mean"
            
            val = float(numeric_df[col].sum() if agg == "sum" else numeric_df[col].mean())
            metrics.append({
                "label": f"{agg.capitalize()} {col}",
                "value": val,
                "agg": agg
            })

        # 2. Identify Primary Visualizations
        visualizations = []
        
        # Look for time series
        time_cols = [c for c in df.columns if any(key in c.lower() for key in ["date", "year", "month", "time", "day"])]
        
        # Look for high-impact categories
        top_cats = []
        for col in cat_df.columns:
            if df[col].nunique() < 20: # Good for pie/bar
                top_cats.append(col)
        
        if time_cols and found_hero_cols:
            visualizations.append({
                "title": f"{found_hero_cols[0]} Trend Over Time",
                "viz": "area",
                "data": self._clean_data(df.groupby(time_cols[0])[found_hero_cols[0]].sum().reset_index().sort_values(time_cols[0])),
                "metadata": {"x": time_cols[0], "y": found_hero_cols[0]}
            })

        if top_cats and found_hero_cols:
            visualizations.append({
                "title": f"{found_hero_cols[0]} by {top_cats[0]}",
                "viz": "pie",
                "data": self._clean_data(df.groupby(top_cats[0])[found_hero_cols[0]].sum().reset_index().nlargest(10, found_hero_cols[0])),
                "metadata": {"x": top_cats[0], "y": found_hero_cols[0]}
            })
            
        # Add a bar chart if we have more categories
        if len(top_cats) > 1 and len(found_hero_cols) > 0:
             visualizations.append({
                "title": f"Top 10 {top_cats[1]} by {found_hero_cols[0]}",
                "viz": "bar",
                "data": self._clean_data(df.groupby(top_cats[1])[found_hero_cols[0]].sum().reset_index().nlargest(10, found_hero_cols[0])),
                "metadata": {"x": top_cats[1], "y": found_hero_cols[0]}
            })

        return {
            "metrics": metrics,
            "visualizations": visualizations
        }

    def analyze_query(self, query: str, df: pd.DataFrame) -> Dict[str, Any]:
        query_lower = query.lower()
        cols = list(df.columns)
        
        result = {}
        
        # Detect if asking for the initial summary/dashboard
        if any(word in query_lower for word in ["kpi", "metrics", "summary", "dashboard", "overall"]):
            profile = self.profile_dataset(df)
            return {
                "answer": "Dashboard synthesized. Neural profiling has identified these key insights.",
                "viz": "dashboard", # New type for the frontend to handle
                "data": profile,
                "metadata": {"rows": len(df)}
            }
        
        # Default granular query logic
        viz_type = "bar"
        if any(word in query_lower for word in ["pie", "ratio", "breakdown", "distribution"]):
            viz_type = "pie"
        elif any(word in query_lower for word in ["trend", "line", "over time", "history", "area"]):
            viz_type = "line" if "area" not in query_lower else "area"
        elif any(word in query_lower for word in ["scatter", "correlation", "relationship"]):
            viz_type = "scatter"
        elif any(word in query_lower for word in ["list", "table", "raw"]):
            viz_type = "table"

        found_cols = [c for c in cols if c.lower() in query_lower]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        
        target_cat = next((c for c in found_cols if c in cat_cols), None)
        if not target_cat and cat_cols:
            target_cat = cat_cols[0]
            
        target_num = next((c for c in found_cols if c in numeric_cols), None)
        if not target_num and numeric_cols:
            target_num = numeric_cols[0]
            
        target_num2 = next((c for c in found_cols if c in numeric_cols and c != target_num), None)
        if not target_num2 and len(numeric_cols) > 1:
            target_num2 = numeric_cols[1]

        if target_cat and target_num:
            try:
                if viz_type == "scatter" and target_num2:
                    result_df = df[[target_num, target_num2]].head(100)
                    result = {
                        "answer": f"Showing correlation between {target_num} and {target_num2}.",
                        "viz": "scatter",
                        "data": result_df,
                        "metadata": {"x": target_num, "y": target_num2}
                    }
                else:
                    result_df = df.groupby(target_cat)[target_num].sum().reset_index()
                    if viz_type == "line" or viz_type == "area":
                        result_df = result_df.sort_values(target_cat)
                    else:
                        result_df = result_df.nlargest(15, target_num)
                        
                    result = {
                        "answer": f"Analysis of {target_num} by {target_cat}.",
                        "viz": viz_type,
                        "data": result_df,
                        "metadata": {"x": target_cat, "y": target_num}
                    }
            except:
                pass

        if not result:
            result = {
                "answer": "Here is a preview of your raw data.",
                "viz": "table",
                "data": df.head(10),
                "metadata": {}
            }

        return self._clean_data(result)

agent = BIAgent()
