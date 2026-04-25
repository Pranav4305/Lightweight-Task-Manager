import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
import time

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")

        # Add Tabs
        tab_notebook = ttk.Notebook(self.root)

        # Tasks Tab
        tasks_tab = ttk.Frame(tab_notebook)
        tab_notebook.add(tasks_tab, text="Tasks")

        # Performance Tab
        performance_tab = ttk.Frame(tab_notebook)
        tab_notebook.add(performance_tab, text="Performance")

        # Benchmarking Tab
        benchmarking_tab = ttk.Frame(tab_notebook)
        tab_notebook.add(benchmarking_tab, text="Benchmarking")

        # Pack the Notebook
        tab_notebook.pack(fill=tk.BOTH, expand=True)

        # Create Treeview in the Tasks Tab
        self.process_tree = ttk.Treeview(tasks_tab, columns=("serial_no", "name", "intensity", "pid"), show="headings")
        self.process_tree.heading("serial_no", text="Serial No")
        self.process_tree.heading("name", text="Name")
        self.process_tree.heading("intensity", text="Intensity")
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Set xscrollcommand for all columns
        for col in ("serial_no", "name", "intensity"):
            self.process_tree.heading(col, text=col, anchor=tk.W)
            self.process_tree.column(col, anchor=tk.W, width=100)
            self.process_tree.xview_moveto(0)

        # Create Vertical Scrollbar for the Treeview
        y_scrollbar = ttk.Scrollbar(tasks_tab, orient="vertical", command=self.process_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure Treeview to use the vertical scrollbar
        self.process_tree.configure(yscrollcommand=y_scrollbar.set)

        # Create labels for Performance Tab
        self.cpu_label = tk.Label(performance_tab, text="CPU Usage:")
        self.cpu_label.pack(pady=5)

        self.cpu_var = tk.StringVar()
        self.cpu_usage_label = tk.Label(performance_tab, textvariable=self.cpu_var)
        self.cpu_usage_label.pack(pady=5)

        self.memory_label = tk.Label(performance_tab, text="Memory Usage:")
        self.memory_label.pack(pady=5)

        self.memory_var = tk.StringVar()
        self.memory_usage_label = tk.Label(performance_tab, textvariable=self.memory_var)
        self.memory_usage_label.pack(pady=5)

        self.gpu_label = tk.Label(performance_tab, text="GPU Usage:")
        self.gpu_label.pack(pady=5)

        self.gpu_var = tk.StringVar()
        self.gpu_usage_label = tk.Label(performance_tab, textvariable=self.gpu_var)
        self.gpu_usage_label.pack(pady=5)

        self.disk_label = tk.Label(performance_tab, text="Disk Usage:")
        self.disk_label.pack(pady=5)

        self.disk_var = tk.StringVar()
        self.disk_usage_label = tk.Label(performance_tab, textvariable=self.disk_var)
        self.disk_usage_label.pack(pady=5)

        # Create End Task button
        self.end_task_button = tk.Button(tasks_tab, text="End Task", command=self.end_selected_task)
        self.end_task_button.pack(side=tk.BOTTOM, pady=10)

        # Create Start Benchmark button and labels in Benchmarking Tab
        self.start_benchmark_button = tk.Button(benchmarking_tab, text="Start Benchmark", command=self.start_benchmark)
        self.start_benchmark_button.pack(pady=10)

        self.cpu_benchmark_label = tk.Label(benchmarking_tab, text="CPU Benchmark: N/A")
        self.cpu_benchmark_label.pack(pady=5)

        self.gpu_benchmark_label = tk.Label(benchmarking_tab, text="GPU Benchmark: N/A")
        self.gpu_benchmark_label.pack(pady=5)

        self.ram_benchmark_label = tk.Label(benchmarking_tab, text="RAM Benchmark: N/A")
        self.ram_benchmark_label.pack(pady=5)

        # Initialize variable to store the current tab
        self.current_tab = tasks_tab

        # Bind the tab change event to update the current tab
        tab_notebook.bind("<<NotebookTabChanged>>", self.update_current_tab)

        # Schedule the initial update and periodic updates every 5000 milliseconds (5 seconds)
        self.root.after(0, self.update_performance, 5000)
        self.root.after(0, self.update_task_manager)

    def end_selected_task(self):
        # Get the selected item from the Treeview
        selected_item = self.process_tree.selection()
        if selected_item:
            # Get the PID from the selected item
            pid_str = self.process_tree.item(selected_item, "values")[-1]

            try:
                # Convert PID to an integer
                pid = int(pid_str)

                # Try to terminate the process
                process = psutil.Process(pid)
                process.terminate()
            except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def update_current_tab(self, event):
        # Update the current tab when the tab is changed
        selected_index = event.widget.index("current")
        self.current_tab = event.widget.winfo_children()[selected_index]

    def categorize_intensity(self, cpu_percent):
        # Categorize intensity based on CPU usage
        if cpu_percent < 30:
            return "Low"
        elif cpu_percent < 70:
            return "Medium"
        else:
            return "High"

    def update_task_manager(self):
        # Get the list of running processes
        processes = psutil.process_iter(['pid', 'cpu_percent', 'username', 'name'])
        processes = list(processes)

        # Filter out system processes and sort by CPU percentage
        user_processes = [p for p in processes if p.info['username'] != 'SYSTEM']
        user_processes.sort(key=lambda x: x.info['cpu_percent'], reverse=True)

        # Clear existing items in the Treeview
        self.process_tree.delete(*self.process_tree.get_children())

        # Display up to 150 user processes in the Treeview
        for index, process in enumerate(user_processes[:150], start=1):
            pid = process.info['pid']
            cpu_percent = process.info['cpu_percent']

            # Check if the values are strings
            if isinstance(cpu_percent, str):
                cpu_percent = 0.0

            # Convert percentage values to floats before formatting
            cpu_percent = float(cpu_percent)

            # Get the program name based on the process ID
            try:
                name = process.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                name = "Unknown"

            # Categorize intensity
            intensity = self.categorize_intensity(cpu_percent)

            # Insert values with dynamically updated serial_no
            item_id = self.process_tree.insert("", "end", values=(index, name, intensity, pid))
            self.process_tree.set(item_id, "serial_no", index)

        # Schedule the next update after a longer interval
        self.root.after(2000, self.update_task_manager)

    def update_performance(self, interval):
        # Get CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_var.set(f"CPU: {cpu_percent}%")

        # Get memory usage
        memory_percent = psutil.virtual_memory().percent
        self.memory_var.set(f"Memory: {memory_percent}%")

        try:
            # Get GPU usage
            gpu_percent = GPUtil.getGPUs()[0].load * 100
            self.gpu_var.set(f"GPU: {gpu_percent:.2f}%")
        except Exception as e:
            # Handle the case when GPUtil is not available or GPU information cannot be retrieved
            self.gpu_var.set("GPU: N/A")

        # Get disk usage
        disk_percent = psutil.disk_usage('/').percent
        self.disk_var.set(f"Disk: {disk_percent}%")

        # Schedule the next update after the specified interval
        self.root.after(interval, self.update_performance, interval)

    def start_benchmark(self):
        # Simulate benchmarking tasks for CPU, GPU, and RAM
        cpu_benchmark_score = self.run_cpu_benchmark()
        gpu_benchmark_score = self.run_gpu_benchmark()
        ram_benchmark_score = self.run_ram_benchmark()

        # Update the labels with the benchmark scores
        self.cpu_benchmark_label.config(text=f"CPU Benchmark: {cpu_benchmark_score} points")
        self.gpu_benchmark_label.config(text=f"GPU Benchmark: {gpu_benchmark_score} points")
        self.ram_benchmark_label.config(text=f"RAM Benchmark: {ram_benchmark_score} points")

    def run_cpu_benchmark(self):
        # Simulate CPU benchmarking
        start_time = time.time()
        # Perform a simple operation, e.g., calculating prime numbers
        for _ in range(500):
            _ = self.calculate_prime_numbers(100)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Score calculation based on the speed of completion
        score = int(100 / elapsed_time)
        return score

    def calculate_prime_numbers(self, n):
        # Helper function for CPU benchmarking
        primes = []
        for num in range(2, n + 1):
            is_prime = all(num % i != 0 for i in range(2, int(num**0.5) + 1))
            if is_prime:
                primes.append(num)
        return primes

    def run_gpu_benchmark(self):
        # Simulate GPU benchmarking
        try:
            # Get GPU usage
            gpu_percent = GPUtil.getGPUs()[0].load * 100
            if gpu_percent == 0:
                # If GPU utilization is still 0, perform a simple GPU operation
                _ = self.matrix_multiplication(5)
        except Exception as e:
            # Log the exception for debugging
            print(f"GPU Benchmark Exception: {e}")
            pass

        # Score calculation (simulated GPU operation)
        score = 50
        return score

    def matrix_multiplication(self, size):
        # Helper function for GPU benchmarking (simulated)
        matrix_a = [[1] * size for _ in range(size)]
        matrix_b = [[2] * size for _ in range(size)]
        result_matrix = [[0] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                for k in range(size):
                    result_matrix[i][j] += matrix_a[i][k] * matrix_b[k][j]

        return result_matrix

    def run_ram_benchmark(self):
        # Simulate RAM benchmarking
        start_time = time.time()
        # Allocate and deallocate memory to simulate RAM usage
        _ = [0] * 100000
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Score calculation based on the speed of completion
        score = int(100 / elapsed_time)
        return score

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()
