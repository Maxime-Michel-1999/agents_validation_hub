#!/bin/bash

# Start FastAPI server in the background
echo "Starting FastAPI server..."
uvicorn backend.app.main:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 2

# Start Streamlit in the background
echo "Starting Streamlit frontend..."
streamlit run frontend/main.py --server.port 8501 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
sleep 2

# Run the test agent
echo "Running test agent..."
python tests/test_agent.py

# Cleanup on script exit
cleanup() {
    echo "Cleaning up processes..."
    kill $FASTAPI_PID
    kill $STREAMLIT_PID
}

trap cleanup EXIT 