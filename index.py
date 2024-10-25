import random
import matplotlib.pyplot as plt
from collections import deque


class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid  # Process ID
        self.arrival_time = arrival_time  # Arrival time of the process
        self.burst_time = burst_time  # Total CPU time required
        self.remaining_time = burst_time  # Time left for the process to run
        self.completion_time = 0  # Time when process finishes
        self.turnaround_time = 0  # Total time from arrival to completion
        self.waiting_time = 0  # Time spent waiting in the queue
        self.priority = priority  # Priority of the process


def generate_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = random.randint(0, 20)
        burst_time = random.randint(1, 10)
        priority = random.randint(1, 5)  # Priority from 1 (highest) to 5 (lowest)
        processes.append(Process(i, arrival_time, burst_time, priority))
    return processes


def print_results(results, algorithm_name):
    print(f"\n{algorithm_name} Scheduling:")
    for process in results:
        print(f"P{process.pid}: TAT={process.turnaround_time}, WT={process.waiting_time}")


def fcfs(processes):
    processes.sort(key=lambda x: x.arrival_time)  # Sort by arrival time
    time = 0
    results = []

    for process in processes:
        if time < process.arrival_time:
            time = process.arrival_time  # Wait for the process to arrive
        time += process.burst_time  # Update current time
        process.completion_time = time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        results.append(process)

    return results


def sjf_non_preemptive(processes):
    time = 0
    results = []
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time))

    while processes:
        ready_queue = [p for p in processes if p.arrival_time <= time]
        if ready_queue:
            shortest = min(ready_queue, key=lambda x: x.burst_time)
            processes.remove(shortest)  # Remove from the list
            time += shortest.burst_time  # Update current time
            shortest.completion_time = time
            shortest.turnaround_time = shortest.completion_time - shortest.arrival_time
            shortest.waiting_time = shortest.turnaround_time - shortest.burst_time
            results.append(shortest)
        else:
            time += 1  # Increment time if CPU is idle

    return results


def sjf_preemptive(processes):
    time = 0
    results = []

    while any(p.remaining_time > 0 for p in processes):
        ready_queue = [p for p in processes if p.arrival_time <= time and p.remaining_time > 0]
        if ready_queue:
            shortest = min(ready_queue, key=lambda x: x.remaining_time)
            shortest.remaining_time -= 1  # Process runs for 1 time unit
            time += 1
            if shortest.remaining_time == 0:
                shortest.completion_time = time
                shortest.turnaround_time = shortest.completion_time - shortest.arrival_time
                shortest.waiting_time = shortest.turnaround_time - shortest.burst_time
                results.append(shortest)
        else:
            time += 1  # Increment time if CPU is idle

    return results


def round_robin(processes, time_quantum):
    time = 0
    results = []
    queue = deque(processes)  # Create a queue for processes

    while queue:
        process = queue.popleft()
        if process.arrival_time > time:
            time = process.arrival_time  # Wait for the process to arrive

        if process.remaining_time > 0:
            if process.remaining_time > time_quantum:
                time += time_quantum  # Process runs for the time quantum
                process.remaining_time -= time_quantum
                queue.append(process)  # Re-add to the end of the queue
            else:
                time += process.remaining_time  # Process finishes
                process.completion_time = time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                results.append(process)

    return results


def priority_scheduling(processes, preemptive=False):
    time = 0
    results = []

    if preemptive:
        while any(p.burst_time > 0 for p in processes):
            ready_queue = [p for p in processes if p.arrival_time <= time and p.burst_time > 0]
            if ready_queue:
                highest_priority = min(ready_queue, key=lambda x: x.priority)
                highest_priority.burst_time -= 1  # Process runs for 1 time unit
                time += 1
                if highest_priority.burst_time == 0:
                    highest_priority.completion_time = time
                    highest_priority.turnaround_time = highest_priority.completion_time - highest_priority.arrival_time
                    highest_priority.waiting_time = highest_priority.turnaround_time - highest_priority.remaining_time
                    results.append(highest_priority)
            else:
                time += 1  # Increment time if CPU is idle
    else:
        processes.sort(key=lambda x: (x.arrival_time, x.priority))  # Sort by arrival and priority
        while processes:
            ready_queue = [p for p in processes if p.arrival_time <= time]
            if ready_queue:
                highest_priority = min(ready_queue, key=lambda x: x.priority)
                time += highest_priority.burst_time  # Process runs to completion
                highest_priority.completion_time = time
                highest_priority.turnaround_time = highest_priority.completion_time - highest_priority.arrival_time
                highest_priority.waiting_time = highest_priority.turnaround_time - highest_priority.burst_time
                processes.remove(highest_priority)  # Remove from the list
                results.append(highest_priority)
            else:
                time += 1  # Increment time if CPU is idle

    return results


def calculate_metrics(results):
    total_tat = sum(p.turnaround_time for p in results)
    total_wt = sum(p.waiting_time for p in results)
    total_processes = len(results)
    avg_tat = total_tat / total_processes if total_processes > 0 else 0
    avg_wt = total_wt / total_processes if total_processes > 0 else 0
    cpu_utilization = (total_processes * (sum(p.burst_time for p in results) / total_tat)) * 100 if total_tat > 0 else 0
    return avg_tat, avg_wt, cpu_utilization


def plot_metrics(metrics, ax, algorithm_name):
    avg_tat, avg_wt, cpu_utilization = metrics
    labels = ['Average TAT', 'Average WT', 'CPU Utilization']
    values = [avg_tat, avg_wt, cpu_utilization]

    ax.bar(labels, values, color=['blue', 'orange', 'green'])
    ax.set_title(algorithm_name)
    ax.set_ylabel('Value')
    ax.set_ylim(0, max(values) + 20)
    ax.grid(axis='y')


def run_simulation():
    num_processes = 20  # Total number of processes to simulate

    original_processes = generate_processes(num_processes)  # Generate processes

    algorithms = {
        "FCFS": fcfs,
        "SJF Non-Preemptive": sjf_non_preemptive,
        "SJF Preemptive": sjf_preemptive,
        "Round Robin": round_robin,
        "Priority Scheduling (Non-Preemptive)": lambda p: priority_scheduling(p, preemptive=False),
        "Priority Scheduling (Preemptive)": lambda p: priority_scheduling(p, preemptive=True),
    }

    metrics_dict = {}

    # Create subplots for each algorithm
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
    axes = axes.flatten()  # Flatten for easy iteration

    for idx, (name, algorithm) in enumerate(algorithms.items()):
        if name == "Round Robin":
            time_quantum = 3
            results = algorithm(original_processes.copy(), time_quantum)
        else:
            results = algorithm(original_processes.copy())

        metrics_dict[name] = calculate_metrics(results)
        plot_metrics(metrics_dict[name], axes[idx], name)

        print_results(results, name)  # Print results for each algorithm

    plt.tight_layout()  # Adjust layout
    plt.show()  # Display the plots


if __name__ == "__main__":
    run_simulation()  # Start the simulation
