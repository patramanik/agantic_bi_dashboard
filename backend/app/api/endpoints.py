from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import DataSnapshot, QueryLog, User
from ..core.agent import agent
from ..core.auth import get_current_user
from ..utils.helpers import to_json_safe_dict
import pandas as pd
import io
import shutil
import os
from pathlib import Path
from typing import List

router = APIRouter(tags=["Neural Synthesis & Data"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Shared memory cache for DataFrames - partitioned by (user_id, filename)
df_cache = {}

@router.post("/upload", summary="Ingest Data Infrastructure")
async def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingest a CSV or Excel file into the authenticated operative's matrix.
    The system will autonomously profile the data upon successful connection.
    """
    try:
        # Create user-specific upload path
        user_dir = UPLOAD_DIR / str(current_user.id)
        user_dir.mkdir(exist_ok=True)
        
        file_path = user_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        contents = file_path.read_bytes()
        df = None
        
        if file.filename.endswith('.csv'):
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for enc in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding=enc)
                    break
                except:
                    continue
            if df is None:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8', encoding_errors='replace')
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))

        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="The uploaded file is empty or invalid.")

        # Cache using user context
        df_cache[(current_user.id, file.filename)] = df
        
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.filename == file.filename,
            DataSnapshot.user_id == current_user.id
        ).first()
        
        if not snapshot:
            snapshot = DataSnapshot(
                filename=file.filename,
                file_path=str(file_path),
                columns=",".join(df.columns.astype(str).tolist()),
                rows_count=int(len(df)),
                user_id=current_user.id
            )
            db.add(snapshot)
        else:
            snapshot.file_path = str(file_path)
            snapshot.columns = ",".join(df.columns.astype(str).tolist())
            snapshot.rows_count = int(len(df))
        
        db.commit()
        
        return to_json_safe_dict({
            "filename": file.filename,
            "columns": df.columns.astype(str).tolist(),
            "rows": int(len(df)),
            "sample": df.head(5)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/query", summary="Neural Query Synthesis")
async def process_query(
    query: str, 
    file_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Synthesize natural language queries into data insights and visualizations.
    - **query**: The operative's question.
    - **file_id**: Target dataset identifier.
    """
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.filename == file_id,
            DataSnapshot.user_id == current_user.id
        ).first()

        if not snapshot or not snapshot.file_path:
            raise HTTPException(status_code=404, detail="Data not found for this user.")

        cache_key = (current_user.id, file_id)
        if cache_key not in df_cache:
            p = Path(snapshot.file_path)
            if p.suffix == '.csv':
                try:
                    df_cache[cache_key] = pd.read_csv(p, encoding='utf-8')
                except:
                    df_cache[cache_key] = pd.read_csv(p, encoding='latin-1')
            else:
                df_cache[cache_key] = pd.read_excel(p)
        
        df = df_cache[cache_key]
        analysis = agent.analyze_query(query, df)
        
        log = QueryLog(
            query=query,
            response=analysis.get("answer", ""),
            viz_type=analysis.get("viz", "table"),
            user_id=current_user.id,
            snapshot_id=snapshot.id
        )
        db.add(log)
        db.commit()
        
        return to_json_safe_dict(analysis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/me", summary="Retrieve Operative Profile")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the authenticated profile of the active neural operative.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email
    }

@router.get("/history", summary="Access Neural Signal History")
async def get_history(
    file_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve history synthesized for a specific dataset or all datasets.
    """
    query = db.query(QueryLog).filter(QueryLog.user_id == current_user.id)
    
    if file_id:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.filename == file_id,
            DataSnapshot.user_id == current_user.id
        ).first()
        if snapshot:
            query = query.filter(QueryLog.snapshot_id == snapshot.id)
    
    logs = query.order_by(QueryLog.created_at.desc()).limit(50).all()
    return logs

@router.get("/datasets", summary="List Connected Matrix Assets")
async def get_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all data assets connected to the operative's neural identity.
    """
    snapshots = db.query(DataSnapshot).filter(DataSnapshot.user_id == current_user.id).all()
    return snapshots

@router.delete("/datasets/{filename}", summary="Decommission Matrix Asset")
async def delete_dataset(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Terminate a data connection and purge all associated history and physical records.
    """
    snapshot = db.query(DataSnapshot).filter(
        DataSnapshot.filename == filename,
        DataSnapshot.user_id == current_user.id
    ).first()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    try:
        # File removal
        if snapshot.file_path and os.path.exists(snapshot.file_path):
            os.remove(snapshot.file_path)
            
        # Cache removal
        if (current_user.id, filename) in df_cache:
            del df_cache[(current_user.id, filename)]
            
        db.delete(snapshot)
        db.commit()
        return {"message": "Dataset and history deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")

@router.get("/suggestions/{file_id}", summary="Generate Dynamic Neural Prompts")
async def get_suggestions(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate diverse, insightful prompt suggestions tailored to the specific dataset matrix.
    """
    try:
        cache_key = (current_user.id, file_id)
        if cache_key not in df_cache:
            snapshot = db.query(DataSnapshot).filter(
                DataSnapshot.filename == file_id,
                DataSnapshot.user_id == current_user.id
            ).first()
            
            if not snapshot or not snapshot.file_path:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            p = Path(snapshot.file_path)
            if p.suffix == '.csv':
                try: df_cache[cache_key] = pd.read_csv(p, encoding='utf-8')
                except: df_cache[cache_key] = pd.read_csv(p, encoding='latin-1')
            else:
                df_cache[cache_key] = pd.read_excel(p)
        
        df = df_cache[cache_key]
        suggestions = agent.generate_suggestions(df)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")
