#!/bin/bash

echo "🛑 Shutting down Internal Assistant Platform..."
echo ""

# Function to kill processes by port
kill_process_by_port() {
    local port=$1
    local process_name=$2
    
    echo "🔍 Looking for $process_name on port $port..."
    
    # Find PID by port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pid" ]; then
        echo "💀 Killing $process_name (PID: $pid) on port $port..."
        
        # Send SIGTERM first for graceful shutdown
        kill -TERM $pid 2>/dev/null
        
        # Wait for graceful shutdown (up to 10 seconds)
        local count=0
        while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "⚡ Force killing $process_name (PID: $pid)..."
            kill -KILL $pid 2>/dev/null
            sleep 1
        else
            echo "✅ $process_name shut down gracefully"
        fi
    else
        echo "ℹ️  No $process_name found running on port $port"
    fi
}

# Function to kill processes by name pattern
kill_process_by_name() {
    local name_pattern=$1
    local process_description=$2
    
    echo "🔍 Looking for $process_description..."
    
    # Find PIDs by process name pattern
    local pids=$(pgrep -f "$name_pattern" 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo "💀 Killing $process_description (PIDs: $pids)..."
        
        # Send SIGTERM first for graceful shutdown
        echo $pids | xargs kill -TERM 2>/dev/null
        
        # Wait for graceful shutdown (up to 10 seconds)
        local count=0
        local still_running=true
        while [ "$still_running" = true ] && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
            still_running=false
            for pid in $pids; do
                if kill -0 $pid 2>/dev/null; then
                    still_running=true
                    break
                fi
            done
        done
        
        # Force kill if still running
        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                echo "⚡ Force killing $process_description (PID: $pid)..."
                kill -KILL $pid 2>/dev/null
            fi
        done
        sleep 1
    else
        echo "ℹ️  No $process_description found running"
    fi
}

# Function to cleanup multiprocessing resources
cleanup_multiprocessing() {
    echo "🧹 Cleaning up multiprocessing resources..."
    
    # Kill any remaining Python multiprocessing processes
    local python_pids=$(pgrep -f "python.*multiprocessing" 2>/dev/null)
    if [ ! -z "$python_pids" ]; then
        echo "💀 Killing multiprocessing processes (PIDs: $python_pids)..."
        echo $python_pids | xargs kill -KILL 2>/dev/null
    fi
    
    # Clean up any semaphore files (macOS specific)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Cleaning up macOS semaphore files..."
        # Remove any leftover semaphore files in /tmp
        find /tmp -name "*.sem" -user $(whoami) -delete 2>/dev/null || true
    fi
}

# Kill processes by port (most reliable method)
echo "📡 Stopping services by port..."
kill_process_by_port 5000 "Backend (Flask)"
kill_process_by_port 3000 "Frontend (Vite)"

# Kill processes by name pattern (backup method)
echo ""
echo "🔍 Stopping services by process name..."
kill_process_by_name "python.*app.py" "Backend Python process"
kill_process_by_name "yarn.*dev" "Frontend Yarn process"
kill_process_by_name "vite" "Vite dev server"
kill_process_by_name "flask" "Flask server"

# Kill any remaining node processes that might be related
echo ""
echo "🧹 Cleaning up any remaining Node.js processes..."
kill_process_by_name "node.*frontend" "Node.js frontend processes"

# Clean up multiprocessing resources
echo ""
cleanup_multiprocessing

echo ""
echo "✅ Shutdown complete!"
echo "🌐 All Internal Assistant services have been stopped."
echo ""
echo "💡 To restart the services, run: ./start-all.sh"
