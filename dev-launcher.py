#!/usr/bin/env python3
"""
ASU1-Loom Development Launcher
One-click script to start the entire development environment
"""

import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path
from typing import List, Optional

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProcessManager:
    """Manages multiple subprocesses"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.is_windows = platform.system() == "Windows"
    
    def start_process(self, name: str, command: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None) -> subprocess.Popen:
        """Start a subprocess and track it"""
        print(f"{Colors.OKCYAN}[START] Starting {name}...{Colors.ENDC}")
        
        try:
            # Merge environment variables
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Start process - don't redirect output so servers can print normally
            if self.is_windows:
                # Windows: Use CREATE_NEW_PROCESS_GROUP to allow Ctrl+C handling
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=process_env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0
                )
            else:
                # Unix: Use process group
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=process_env,
                    preexec_fn=os.setsid
                )
            
            self.processes.append(process)
            print(f"{Colors.OKGREEN}[OK] {name} started (PID: {process.pid}){Colors.ENDC}")
            return process
            
        except Exception as e:
            print(f"{Colors.FAIL}[ERROR] Failed to start {name}: {e}{Colors.ENDC}")
            raise
    
    def stop_all(self):
        """Stop all tracked processes"""
        print(f"\n{Colors.WARNING}[STOP] Stopping all services...{Colors.ENDC}")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    if self.is_windows:
                        # Windows: Send CTRL_BREAK_EVENT
                        process.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        # Unix: Send SIGTERM to process group
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        print(f"{Colors.OKGREEN}[OK] Process {process.pid} stopped gracefully{Colors.ENDC}")
                    except subprocess.TimeoutExpired:
                        # Force kill if not stopped
                        process.kill()
                        print(f"{Colors.WARNING}[WARN] Process {process.pid} force killed{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}[ERROR] Error stopping process {process.pid}: {e}{Colors.ENDC}")
        
        self.processes.clear()
        print(f"{Colors.OKGREEN}[OK] All services stopped{Colors.ENDC}")


class DevLauncher:
    """Main launcher class"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.process_manager = ProcessManager()
        self.is_windows = platform.system() == "Windows"
    
    def print_banner(self):
        """Print startup banner"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         [THREAD]  ASU1-Loom Dev Launcher  [THREAD]        ║
║                                                           ║
║          Hybrid Container Orchestration Platform          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print(f"{Colors.OKBLUE}[SEARCH] Checking prerequisites...{Colors.ENDC}\n")
        
        checks = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 11):
            print(f"{Colors.OKGREEN}[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.ENDC}")
            checks.append(True)
        else:
            print(f"{Colors.FAIL}[ERROR] Python 3.11+ required (found {python_version.major}.{python_version.minor}){Colors.ENDC}")
            checks.append(False)
        
        # Check if backend directory exists
        if self.backend_dir.exists():
            print(f"{Colors.OKGREEN}[OK] Backend directory found{Colors.ENDC}")
            checks.append(True)
        else:
            print(f"{Colors.FAIL}[ERROR] Backend directory not found{Colors.ENDC}")
            checks.append(False)
        
        # Check if frontend directory exists
        if self.frontend_dir.exists():
            print(f"{Colors.OKGREEN}[OK] Frontend directory found{Colors.ENDC}")
            checks.append(True)
        else:
            print(f"{Colors.FAIL}[ERROR] Frontend directory not found{Colors.ENDC}")
            checks.append(False)
        
        # Check if .env file exists
        env_file = self.root_dir / ".env"
        if env_file.exists():
            print(f"{Colors.OKGREEN}[OK] .env file found{Colors.ENDC}")
            checks.append(True)
        else:
            print(f"{Colors.WARNING}[WARN] .env file not found (optional){Colors.ENDC}")
            checks.append(True)  # Not critical
        
        # Check if backend requirements are installed
        try:
            import fastapi
            import strawberry
            import sqlalchemy
            print(f"{Colors.OKGREEN}[OK] Backend dependencies installed{Colors.ENDC}")
            checks.append(True)
        except ImportError as e:
            print(f"{Colors.WARNING}[WARN] Some backend dependencies missing: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}   Run: pip install -r backend/requirements.txt{Colors.ENDC}")
            checks.append(False)
        
        print()
        return all(checks)
    
    def start_backend(self):
        """Start the backend server"""
        print(f"\n{Colors.HEADER}[PACKAGE] Starting Backend Server...{Colors.ENDC}")
        
        # Determine Python command
        python_cmd = "python" if self.is_windows else "python3"
        
        # Start backend
        backend_process = self.process_manager.start_process(
            "Backend Server",
            [python_cmd, "serve.py"] if (self.backend_dir / "serve.py").exists() else [python_cmd, "main.py"],
            cwd=self.backend_dir
        )
        
        # Wait longer for backend to start
        print(f"{Colors.OKCYAN}[WAIT] Waiting for backend to initialize...{Colors.ENDC}")
        time.sleep(3)
        
        if backend_process.poll() is None:
            print(f"{Colors.OKGREEN}[OK] Backend server running at http://localhost:8000{Colors.ENDC}")
            print(f"{Colors.OKGREEN}   GraphQL endpoint: http://localhost:8000/graphql{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[ERROR] Backend server failed to start{Colors.ENDC}")
            print(f"{Colors.FAIL}   Check backend logs for errors{Colors.ENDC}")
            raise Exception("Backend startup failed")
    
    def start_frontend(self):
        """Start the frontend server"""
        print(f"\n{Colors.HEADER}[WEB] Starting Frontend Server...{Colors.ENDC}")
        
        # Determine Python command
        python_cmd = "python" if self.is_windows else "python3"
        
        # Start frontend
        frontend_process = self.process_manager.start_process(
            "Frontend Server",
            [python_cmd, "serve.py"],
            cwd=self.frontend_dir
        )
        
        # Wait longer for frontend to start
        print(f"{Colors.OKCYAN}[WAIT] Waiting for frontend to initialize...{Colors.ENDC}")
        time.sleep(3)
        
        if frontend_process.poll() is None:
            print(f"{Colors.OKGREEN}[OK] Frontend server running at http://localhost:3000{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[ERROR] Frontend server failed to start{Colors.ENDC}")
            print(f"{Colors.FAIL}   Port 3000 may be in use or frontend/dist/ missing{Colors.ENDC}")
            raise Exception("Frontend startup failed")
    
    def print_status(self):
        """Print current status"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}[CELEBRATE] ASU1-Loom Development Environment Ready!{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.OKCYAN}[LOCATION] Access Points:{Colors.ENDC}")
        print(f"   [WEB] Frontend:  {Colors.BOLD}http://localhost:3000{Colors.ENDC}")
        print(f"   [PACKAGE] Backend:   {Colors.BOLD}http://localhost:8000{Colors.ENDC}")
        print(f"   [SEARCH] GraphQL:   {Colors.BOLD}http://localhost:8000/graphql{Colors.ENDC}")
        
        print(f"\n{Colors.OKCYAN}[GAME] Features Available:{Colors.ENDC}")
        print(f"   [OK] Container Management")
        print(f"   [OK] Template System (13 templates)")
        print(f"   [OK] Modal-based UI")
        print(f"   [OK] Minecraft Servers (Vanilla, Paper, Spigot, Forge, NeoForge, Fabric)")
        print(f"   [CONSTRUCTION] Modpack Automation (Backend ready, frontend pending)")
        
        print(f"\n{Colors.OKCYAN}[KEYBOARD]  Controls:{Colors.ENDC}")
        print(f"   Press {Colors.BOLD}Ctrl+C{Colors.ENDC} to stop all services")
        
        print(f"\n{Colors.WARNING}[LIGHTBULB] Tips:{Colors.ENDC}")
        print(f"   • Check backend logs for API errors")
        print(f"   • Frontend auto-reloads on file changes")
        print(f"   • Configure API keys in .env for modpack features")
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def monitor_processes(self):
        """Monitor running processes and handle output"""
        print(f"{Colors.OKCYAN}[CHART] Monitoring services... (Ctrl+C to stop){Colors.ENDC}\n")
        
        try:
            while True:
                # Check if any process has died
                for process in self.process_manager.processes:
                    if process.poll() is not None:
                        print(f"{Colors.FAIL}[ERROR] Process {process.pid} has stopped unexpectedly{Colors.ENDC}")
                        return
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[WARN]  Received shutdown signal{Colors.ENDC}")
    
    def run(self):
        """Main run method"""
        try:
            # Print banner
            self.print_banner()
            
            # Check prerequisites
            if not self.check_prerequisites():
                print(f"\n{Colors.FAIL}[ERROR] Prerequisites check failed. Please fix the issues above.{Colors.ENDC}")
                return 1
            
            # Start services
            self.start_backend()
            self.start_frontend()
            
            # Print status
            self.print_status()
            
            # Monitor processes
            self.monitor_processes()
            
            return 0
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[WARN]  Received shutdown signal{Colors.ENDC}")
            return 0
            
        except Exception as e:
            print(f"\n{Colors.FAIL}[ERROR] Error: {e}{Colors.ENDC}")
            return 1
            
        finally:
            # Always cleanup
            self.process_manager.stop_all()
            print(f"\n{Colors.OKGREEN}[WAVE] Goodbye!{Colors.ENDC}\n")


def main():
    """Entry point"""
    launcher = DevLauncher()
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
