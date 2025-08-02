# utils/task_automation.py
import os
import subprocess
import psutil
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import socket
from pathlib import Path

class TaskAutomationEngine:
    def __init__(self):
        self.active_tasks = {}
        self.task_queue = []
        self.automation_rules = {}
        self.system_monitor = SystemMonitor()
        self.load_automation_rules()
        
        # Start background task processor
        self.task_processor = threading.Thread(target=self._process_tasks, daemon=True)
        self.task_processor.start()
    
    def load_automation_rules(self):
        """Load automation rules from file"""
        rules_file = "data/automation_rules.json"
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r') as f:
                    self.automation_rules = json.load(f)
            except Exception as e:
                print(f"[Automation] Error loading rules: {e}")
                self.automation_rules = {}
        else:
            self.automation_rules = self._create_default_rules()
            self.save_automation_rules()
    
    def save_automation_rules(self):
        """Save automation rules to file"""
        os.makedirs("data", exist_ok=True)
        try:
            with open("data/automation_rules.json", 'w') as f:
                json.dump(self.automation_rules, f, indent=2)
        except Exception as e:
            print(f"[Automation] Error saving rules: {e}")
    
    def _create_default_rules(self):
        """Create default automation rules"""
        return {
            "productivity_boost": {
                "trigger": "focus_mode",
                "actions": [
                    {"type": "close_distracting_apps", "apps": ["firefox", "discord", "steam"]},
                    {"type": "start_app", "app": "code"},
                    {"type": "set_do_not_disturb", "duration": 120}
                ]
            },
            "morning_routine": {
                "trigger": "time_based",
                "time": "09:00",
                "actions": [
                    {"type": "system_info", "display": True},
                    {"type": "weather_check", "location": "auto"},
                    {"type": "calendar_summary", "days": 1}
                ]
            },
            "battery_low": {
                "trigger": "system_condition",
                "condition": "battery_below_20",
                "actions": [
                    {"type": "notification", "message": "Battery low! Consider charging."},
                    {"type": "reduce_performance", "mode": "power_saver"}
                ]
            }
        }
    
    def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific task"""
        task_id = f"{task_type}_{int(time.time())}"
        
        task = {
            "id": task_id,
            "type": task_type,
            "params": kwargs,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "result": None
        }
        
        self.active_tasks[task_id] = task
        
        try:
            if task_type == "system_cleanup":
                result = self._system_cleanup(**kwargs)
            elif task_type == "file_organization":
                result = self._organize_files(**kwargs)
            elif task_type == "network_diagnostics":
                result = self._network_diagnostics(**kwargs)
            elif task_type == "performance_optimization":
                result = self._optimize_performance(**kwargs)
            elif task_type == "automated_backup":
                result = self._automated_backup(**kwargs)
            elif task_type == "smart_scheduling":
                result = self._smart_scheduling(**kwargs)
            elif task_type == "resource_monitoring":
                result = self._resource_monitoring(**kwargs)
            elif task_type == "security_scan":
                result = self._security_scan(**kwargs)
            else:
                result = {"error": f"Unknown task type: {task_type}"}
            
            task["status"] = "completed" if "error" not in result else "failed"
            task["result"] = result
            task["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            task["status"] = "failed"
            task["result"] = {"error": str(e)}
            task["completed_at"] = datetime.now().isoformat()
        
        return task
    
    def _system_cleanup(self, **kwargs) -> Dict[str, Any]:
        """Perform system cleanup tasks"""
        results = {"cleaned": [], "errors": []}
        
        try:
            # Clean temporary files
            temp_dirs = ["/tmp", "/var/tmp", os.path.expanduser("~/.cache")]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.getmtime(file_path) < time.time() - 86400:  # 1 day old
                                    os.remove(file_path)
                                    results["cleaned"].append(file_path)
                            except Exception as e:
                                results["errors"].append(f"Could not remove {file_path}: {e}")
            
            # Clean package cache (Ubuntu/Debian)
            try:
                subprocess.run(["sudo", "apt", "autoremove", "-y"], 
                             capture_output=True, timeout=60)
                subprocess.run(["sudo", "apt", "autoclean"], 
                             capture_output=True, timeout=60)
                results["cleaned"].append("Package cache cleaned")
            except:
                pass
            
            return results
            
        except Exception as e:
            return {"error": f"System cleanup failed: {e}"}
    
    def _organize_files(self, directory: str = None, **kwargs) -> Dict[str, Any]:
        """Organize files in a directory"""
        if not directory:
            directory = os.path.expanduser("~/Downloads")
        
        if not os.path.exists(directory):
            return {"error": f"Directory {directory} does not exist"}
        
        results = {"organized": [], "created_folders": []}
        
        file_types = {
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".go", ".rs"]
        }
        
        try:
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    for folder_name, extensions in file_types.items():
                        if file_ext in extensions:
                            folder_path = os.path.join(directory, folder_name)
                            if not os.path.exists(folder_path):
                                os.makedirs(folder_path)
                                results["created_folders"].append(folder_path)
                            
                            old_path = os.path.join(directory, filename)
                            new_path = os.path.join(folder_path, filename)
                            
                            # Handle duplicate names
                            counter = 1
                            while os.path.exists(new_path):
                                name, ext = os.path.splitext(filename)
                                new_filename = f"{name}_{counter}{ext}"
                                new_path = os.path.join(folder_path, new_filename)
                                counter += 1
                            
                            os.rename(old_path, new_path)
                            results["organized"].append(f"{filename} -> {folder_name}/")
                            break
            
            return results
            
        except Exception as e:
            return {"error": f"File organization failed: {e}"}
    
    def _network_diagnostics(self, **kwargs) -> Dict[str, Any]:
        """Perform network diagnostics"""
        results = {}
        
        try:
            # Check internet connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                results["internet_status"] = "Connected"
            except OSError:
                results["internet_status"] = "No connection"
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            results["interfaces"] = {}
            
            for interface_name, interface_addresses in interfaces.items():
                results["interfaces"][interface_name] = []
                for address in interface_addresses:
                    if address.family == socket.AF_INET:  # IPv4
                        results["interfaces"][interface_name].append({
                            "ip": address.address,
                            "netmask": address.netmask
                        })
            
            # Network usage statistics
            net_io = psutil.net_io_counters()
            results["network_stats"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_received": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_received": net_io.packets_recv
            }
            
            # Speed test (basic ping)
            try:
                ping_result = subprocess.run(
                    ["ping", "-c", "4", "8.8.8.8"], 
                    capture_output=True, text=True, timeout=10
                )
                if ping_result.returncode == 0:
                    lines = ping_result.stdout.split('\n')
                    for line in lines:
                        if "avg" in line:
                            results["ping_avg"] = line.split('/')[-2] + "ms"
                            break
            except:
                results["ping_avg"] = "Unable to measure"
            
            return results
            
        except Exception as e:
            return {"error": f"Network diagnostics failed: {e}"}
    
    def _optimize_performance(self, **kwargs) -> Dict[str, Any]:
        """Optimize system performance"""
        results = {"optimizations": [], "warnings": []}
        
        try:
            # Clear RAM cache
            try:
                subprocess.run(["sudo", "sync"], timeout=30)
                subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], timeout=30)
                results["optimizations"].append("RAM cache cleared")
            except Exception as e:
                results["warnings"].append(f"Could not clear RAM cache: {e}")
            
            # Check for memory-heavy processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 5.0:  # More than 5% RAM
                        processes.append(proc.info)
                except:
                    continue
            
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            results["memory_heavy_processes"] = processes[:10]
            
            # CPU optimization suggestions
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                results["warnings"].append("High CPU usage detected. Consider closing unnecessary applications.")
            
            # Disk usage check
            disk_usage = psutil.disk_usage('/')
            if disk_usage.percent > 90:
                results["warnings"].append("Disk space is running low. Consider cleaning up files.")
            
            return results
            
        except Exception as e:
            return {"error": f"Performance optimization failed: {e}"}
    
    def _automated_backup(self, source_dir: str = None, backup_dir: str = None, **kwargs) -> Dict[str, Any]:
        """Perform automated backup"""
        if not source_dir:
            source_dir = os.path.expanduser("~/Documents")
        
        if not backup_dir:
            backup_dir = os.path.expanduser("~/Backups")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        full_backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Use rsync for efficient backup
            result = subprocess.run([
                "rsync", "-av", "--progress", 
                source_dir + "/", full_backup_path + "/"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "backup_location": full_backup_path,
                    "timestamp": timestamp,
                    "details": result.stdout
                }
            else:
                return {"error": f"Backup failed: {result.stderr}"}
                
        except Exception as e:
            return {"error": f"Backup process failed: {e}"}
    
    def _smart_scheduling(self, **kwargs) -> Dict[str, Any]:
        """Implement smart scheduling based on system resources and user patterns"""
        current_time = datetime.now()
        hour = current_time.hour
        
        recommendations = []
        
        # System resource-based recommendations
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent < 30 and memory_percent < 60:
            if 9 <= hour <= 17:  # Work hours
                recommendations.append("Good time for resource-intensive tasks")
            else:
                recommendations.append("System resources are available for background tasks")
        
        if hour < 9 or hour > 22:  # Early morning or late night
            recommendations.append("Quiet hours - good for automated maintenance")
        
        # Battery-based recommendations (for laptops)
        try:
            battery = psutil.sensors_battery()
            if battery:
                if battery.percent < 20:
                    recommendations.append("Low battery - defer non-essential tasks")
                elif battery.percent > 80 and not battery.power_plugged:
                    recommendations.append("Good battery level for mobile tasks")
        except:
            pass
        
        return {
            "current_time": current_time.isoformat(),
            "system_load": {"cpu": cpu_percent, "memory": memory_percent},
            "recommendations": recommendations
        }
    
    def _resource_monitoring(self, duration: int = 60, **kwargs) -> Dict[str, Any]:
        """Monitor system resources over time"""
        monitoring_data = {
            "start_time": datetime.now().isoformat(),
            "duration": duration,
            "samples": []
        }
        
        try:
            interval = min(5, duration // 12)  # Sample every 5 seconds or 12 times total
            
            for _ in range(duration // interval):
                sample = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": psutil.disk_io_counters()._asdict(),
                    "network_io": psutil.net_io_counters()._asdict()
                }
                
                # Add temperature if available
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        sample["temperatures"] = {
                            name: [temp.current for temp in temp_list]
                            for name, temp_list in temps.items()
                        }
                except:
                    pass
                
                monitoring_data["samples"].append(sample)
                time.sleep(interval)
            
            # Calculate averages
            if monitoring_data["samples"]:
                avg_cpu = sum(s["cpu_percent"] for s in monitoring_data["samples"]) / len(monitoring_data["samples"])
                avg_memory = sum(s["memory_percent"] for s in monitoring_data["samples"]) / len(monitoring_data["samples"])
                
                monitoring_data["averages"] = {
                    "cpu_percent": round(avg_cpu, 2),
                    "memory_percent": round(avg_memory, 2)
                }
            
            return monitoring_data
            
        except Exception as e:
            return {"error": f"Resource monitoring failed: {e}"}
    
    def _security_scan(self, **kwargs) -> Dict[str, Any]:
        """Perform basic security scan"""
        results = {
            "checks": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Check for suspicious processes
            suspicious_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 90:  # High CPU usage
                        suspicious_processes.append(proc.info)
                except:
                    continue
            
            if suspicious_processes:
                results["warnings"].append(f"High CPU processes detected: {suspicious_processes}")
            else:
                results["checks"].append("No suspicious high-CPU processes found")
            
            # Check network connections
            connections = psutil.net_connections()
            external_connections = [
                conn for conn in connections 
                if conn.status == 'ESTABLISHED' and conn.raddr
            ]
            
            results["checks"].append(f"Active network connections: {len(external_connections)}")
            
            # Check disk permissions for sensitive directories
            sensitive_dirs = ["/etc", "/usr/bin", "/usr/sbin"]
            for dir_path in sensitive_dirs:
                if os.path.exists(dir_path):
                    stat_info = os.stat(dir_path)
                    if stat_info.st_mode & 0o002:  # World writable
                        results["warnings"].append(f"World-writable sensitive directory: {dir_path}")
                    else:
                        results["checks"].append(f"Permissions OK for {dir_path}")
            
            # General recommendations
            results["recommendations"].extend([
                "Keep system updated",
                "Use strong passwords",
                "Enable firewall",
                "Regular security updates"
            ])
            
            return results
            
        except Exception as e:
            return {"error": f"Security scan failed: {e}"}
    
    def _process_tasks(self):
        """Background task processor"""
        while True:
            if self.task_queue:
                task = self.task_queue.pop(0)
                self.execute_task(**task)
            time.sleep(1)
    
    def schedule_task(self, task_type: str, delay_seconds: int = 0, **kwargs):
        """Schedule a task for later execution"""
        def delayed_execution():
            time.sleep(delay_seconds)
            self.execute_task(task_type, **kwargs)
        
        thread = threading.Thread(target=delayed_execution, daemon=True)
        thread.start()
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue)
        }

class SystemMonitor:
    def __init__(self):
        self.alerts = []
        self.monitoring_active = False
    
    def start_monitoring(self):
        """Start continuous system monitoring"""
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > 90:
                    self.alerts.append({
                        "type": "high_cpu",
                        "value": cpu_percent,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check memory usage
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > 90:
                    self.alerts.append({
                        "type": "high_memory",
                        "value": memory_percent,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check disk usage
                disk_percent = psutil.disk_usage('/').percent
                if disk_percent > 95:
                    self.alerts.append({
                        "type": "disk_full",
                        "value": disk_percent,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Limit alerts to last 100
                if len(self.alerts) > 100:
                    self.alerts = self.alerts[-50:]
                
            except Exception as e:
                print(f"[Monitor] Error: {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        return self.alerts[-10:]  # Return last 10 alerts
