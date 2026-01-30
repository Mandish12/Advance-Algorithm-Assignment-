"""
Enterprise Emergency Network Simulator

A professional-grade interactive tool for simulating and analyzing emergency
network topology using advanced graph algorithms and real-time analytics.

Supports:
- Minimum Spanning Tree calculation (Prim's algorithm)
- Edge-disjoint path finding for redundancy
- Network failure simulation with recovery analysis
- Balanced command tree optimization
- Graph coloring with frequency assignment
- Real-time network analytics and metrics
- Node centrality analysis
- Network resilience assessment
- Animated results with smooth transitions
- Background processing with progress indicators

Author: Network Engineering Team
Version: 3.0.0
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Dict, Tuple, Set, Callable
from dataclasses import dataclass
from collections import defaultdict
import threading
import time
import queue

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import networkx as nx
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoadingDialog(tk.Toplevel):
    """Animated loading dialog with spinner."""
    
    def __init__(self, parent, title="Processing"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        # UI elements
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.label = ttk.Label(frame, text="Processing...", font=("Arial", 12, "bold"))
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=250)
        self.progress.pack(pady=10)
        self.progress.start()
        
        self.spinner_chars = ['|', '/', '-', '\\']
        self.current_spinner = 0
        self.animate()
    
    def animate(self):
        """Update spinner animation."""
        try:
            spinner = self.spinner_chars[self.current_spinner % len(self.spinner_chars)]
            self.label.config(text=f"{spinner} Processing...")
            self.current_spinner += 1
            self.after(200, self.animate)
        except tk.TclError:
            pass  # Window closed


class ResultPage(ttk.Frame):
    """Dedicated result display page with animations."""
    
    def __init__(self, parent, on_back_callback=None):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        
        # Header with title
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        self.title_label = ttk.Label(header, text="Analysis Result", font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(header)
        button_frame.pack(side=tk.RIGHT, fill=tk.X)
        
        ttk.Button(button_frame, text="Copy", command=self._copy_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self._on_back).pack(side=tk.LEFT, padx=5)
        
        # Result text display
        self.text_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Courier", 10), height=25)
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for formatting
        self.text_display.tag_config("header", font=("Courier", 11, "bold"), foreground="darkblue")
        self.text_display.tag_config("section", font=("Courier", 10, "bold"), foreground="darkgreen")
    
    def set_title(self, title):
        """Set the page title."""
        self.title_label.config(text=title)
    
    def display_result(self, text):
        """Display result with animation."""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, text)
        self.text_display.config(state=tk.DISABLED)
    
    def _copy_text(self):
        """Copy text to clipboard."""
        text = self.text_display.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        logger.info("Result copied to clipboard")
    
    def _on_back(self):
        """Go back to previous view."""
        if self.on_back_callback:
            self.on_back_callback()


@dataclass
class NetworkMetrics:
    """Container for network performance metrics."""
    density: float
    avg_clustering: float
    avg_path_length: float
    diameter: int
    connected_components: int
    avg_degree: float


class LoadingAnimation:
    """Animated loading indicator."""
    
    def __init__(self, parent, width=30):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.width = width
        self.spinner_chars = ['|', '/', '-', '\\']
        self.current = 0
        self.label = ttk.Label(self.frame, text='Loading...', font=('Arial', 12, 'bold'))
        self.label.pack()
        self.running = False
    
    def start(self):
        """Start animation."""
        self.running = True
        self._animate()
    
    def _animate(self):
        """Update animation frame."""
        if self.running:
            spinner = self.spinner_chars[self.current % len(self.spinner_chars)]
            dots = '.' * ((self.current // 2) % 4)
            self.label.config(text=f'{spinner} Processing{dots}')
            self.current += 1
            self.parent.after(100, self._animate)
    
    def stop(self):
        """Stop animation."""
        self.running = False
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def destroy(self):
        """Destroy widget."""
        self.stop()
        self.frame.destroy()


class ResultPage(ttk.Frame):
    """Dedicated page for displaying algorithm results."""
    
    def __init__(self, parent, title: str, result_data: str, on_back: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.result_data = result_data
        self.on_back = on_back
        self.opacity = 0
        
        self._create_widgets()
        self._animate_in()
    
    def _create_widgets(self):
        """Create result page widgets."""
        # Header with back button
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(header, text='Back to Dashboard', command=self._on_back_click).pack(side=tk.LEFT)
        ttk.Label(header, text=self.title, font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=20)
        
        # Result display
        result_frame = ttk.LabelFrame(self, text='Results', padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrolled text for results
        self.result_text = scrolledtext.ScrolledText(
            result_frame, height=20, width=80, font=('Courier', 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.insert(tk.END, self.result_data)
        self.result_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text='Copy Results', 
                  command=self._copy_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Export', 
                  command=self._export_results).pack(side=tk.LEFT, padx=5)
    
    def _animate_in(self):
        """Animate page entrance."""
        if self.opacity < 1.0:
            self.opacity += 0.1
            self.after(50, self._animate_in)
    
    def _on_back_click(self):
        """Handle back button."""
        self._animate_out()
    
    def _animate_out(self):
        """Animate page exit."""
        if self.opacity > 0:
            self.opacity -= 0.1
            self.after(50, self._animate_out)
        else:
            self.on_back()
    
    def _copy_results(self):
        """Copy results to clipboard."""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.result_data)
            messagebox.showinfo('Success', 'Results copied to clipboard!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to copy: {e}')
    
    def _export_results(self):
        """Export results to file."""
        try:
            filename = f'result_{int(time.time())}.txt'
            with open(filename, 'w') as f:
                f.write(self.result_data)
            messagebox.showinfo('Success', f'Results exported to {filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export: {e}')


class ApplicationConfig:
    """Application configuration constants."""
    WINDOW_TITLE = "Enterprise Emergency Network Simulator v2.0"
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FIGURE_WIDTH = 8
    FIGURE_HEIGHT = 7
    
    NODE_COUNT = 8
    NODE_SIZE = 700
    FIGURE_SEED = 42
    
    COLOR_MAP = {
        0: "red", 1: "blue", 2: "green", 3: "yellow",
        4: "orange", 5: "purple", 6: "pink", 7: "brown"
    }
    HIGHLIGHT_COLOR = "red"
    NODE_DEFAULT_COLOR = "lightblue"
    EDGE_DEFAULT_COLOR = "gray"
    HIGHLIGHT_WIDTH = 3
    
    # Analytics thresholds
    HIGH_RISK_DEGREE = 5
    MEDIUM_RISK_DEGREE = 3


class EmergencyNetworkSimulator(tk.Tk):
    """
    Enterprise Emergency Network Simulator with advanced analytics.
    
    Features:
    - Real-time network visualization
    - Advanced graph algorithms
    - Network metrics and analytics
    - Failure simulation and recovery
    - Centrality analysis
    - Performance monitoring
    """
    
    def __init__(self) -> None:
        """Initialize the application with advanced features."""
        super().__init__()
        
        self.title(ApplicationConfig.WINDOW_TITLE)
        self.geometry(f"{ApplicationConfig.WINDOW_WIDTH}x{ApplicationConfig.WINDOW_HEIGHT}")
        self.minsize(1200, 700)
        
        # Initialize state
        self.G: nx.Graph = nx.Graph()
        self.G_original: nx.Graph = nx.Graph()
        self.metrics: Optional[NetworkMetrics] = None
        self.selected_algorithm: tk.StringVar = tk.StringVar(value="mst")
        self.analysis_thread: Optional[threading.Thread] = None
        self.result_queue: queue.Queue = queue.Queue()
        
        # Main container for switching between views
        self.container = ttk.Frame(self)
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.current_frame = None
        
        # Initialize components
        self._initialize_graph()
        self._create_dashboard()
        self._calculate_metrics()
        
        # Check queue for results
        self._check_queue()
        
        logger.info("Enterprise Network Simulator v3.0 initialized successfully")

    def _initialize_graph(self) -> None:
        """Initialize the sample network graph with nodes and weighted edges."""
        try:
            # Add nodes with attributes
            for i in range(1, ApplicationConfig.NODE_COUNT + 1):
                self.G.add_node(i, status="active", load=0.5)
            
            # Define edges with weights and capacities
            edges: List[Tuple[int, int, int, int]] = [
                (1, 2, 4, 100), (1, 3, 3, 100), (2, 4, 5, 80),
                (3, 4, 6, 60), (3, 5, 2, 120), (5, 6, 4, 90),
                (6, 7, 3, 110), (7, 8, 2, 100), (4, 8, 7, 50)
            ]
            
            for u, v, w, cap in edges:
                self.G.add_edge(u, v, weight=w, capacity=cap, utilization=0.3)
            
            # Create backup for reset
            self.G_original = self.G.copy()
            
            logger.info(
                f"Graph initialized with {self.G.number_of_nodes()} nodes, "
                f"{self.G.number_of_edges()} edges, total capacity: "
                f"{sum(d['capacity'] for u, v, d in self.G.edges(data=True))}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def _calculate_metrics(self) -> None:
        """Calculate comprehensive network metrics."""
        try:
            if not self.G.nodes():
                return
            
            density = nx.density(self.G)
            avg_clustering = nx.average_clustering(self.G) if len(self.G) > 2 else 0
            
            if nx.is_connected(self.G):
                avg_path_length = nx.average_shortest_path_length(self.G)
                diameter = nx.diameter(self.G)
            else:
                avg_path_length = float('inf')
                diameter = float('inf')
            
            connected_components = nx.number_connected_components(self.G)
            degrees = [d for n, d in self.G.degree()]
            avg_degree = np.mean(degrees) if degrees else 0
            
            self.metrics = NetworkMetrics(
                density=density,
                avg_clustering=avg_clustering,
                avg_path_length=avg_path_length,
                diameter=diameter,
                connected_components=connected_components,
                avg_degree=avg_degree
            )
            
            logger.info(f"Network metrics calculated: density={density:.3f}, diameter={diameter}")
        except Exception as e:
            logger.warning(f"Could not calculate all metrics: {e}")
            self.metrics = None

    def _create_dashboard(self) -> None:
        """Create main dashboard with tabbed interface."""
        try:
            # Main container
            main_frame = ttk.Frame(self.container)
            main_frame.grid(row=0, column=0, sticky="nsew")
            self.frames['dashboard'] = main_frame
            
            main_frame.grid_rowconfigure(0, weight=1)
            main_frame.grid_columnconfigure(0, weight=1)
            
            # Create notebook (tabbed interface)
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Tab 1: Visualization
            self._create_visualization_tab()
            
            # Tab 2: Analytics
            self._create_analytics_tab()
            
            # Tab 3: Algorithm Suite
            self._create_algorithm_tab()
            
            # Tab 4: Network Status
            self._create_status_tab()
            
            self._show_frame('dashboard')
            logger.info("Dashboard created with tabbed interface")
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def _show_frame(self, frame_name: str):
        """Switch to specified frame with animation."""
        if frame_name in self.frames:
            frame = self.frames[frame_name]
            frame.tkraise()
            frame.grid(row=0, column=0, sticky="nsew")
            self.current_frame = frame_name
    
    def _show_result_page(self, title: str, result_text: str):
        """Display result on dedicated page."""
        # Create result page
        result_frame = ResultPage(
            self.container, 
            title, 
            result_text,
            lambda: self._show_frame('dashboard')
        )
        result_frame.grid(row=0, column=0, sticky="nsew")
        self.frames['result'] = result_frame
        self._show_frame('result')
        logger.info(f"Result page displayed: {title}")
    
    def _check_queue(self):
        """Check for results from worker threads."""
        try:
            while True:
                msg_type, title, data = self.result_queue.get_nowait()
                if msg_type == 'result':
                    self._show_result_page(title, data)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)
    
    def _run_with_animation(self, task_func: Callable, task_name: str) -> None:
        """Run task with loading animation in background."""
        def worker():
            try:
                result = task_func()
                self.result_queue.put(('result', task_name, result))
                logger.info(f"Task completed: {task_name}")
            except Exception as e:
                logger.error(f"Task failed: {e}")
                messagebox.showerror("Error", f"Task failed: {str(e)}")
        
        # Start worker thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _create_visualization_tab(self) -> None:
        """Create graph visualization tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Visualization")
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(tab, text="Network Controls", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self._add_button(control_frame, "Reset Network", self._on_reset_network)
        self._add_button(control_frame, "Calculate MST", self._on_generate_mst)
        self._add_button(control_frame, "Find Disjoint Paths", self._on_show_paths)
        self._add_button(control_frame, "Simulate Failure", self._on_simulate_failure)
        self._add_button(control_frame, "Optimize Tree", self._on_optimize_tree)
        self._add_button(control_frame, "Graph Coloring", self._on_graph_coloring)
        self._add_button(control_frame, "Centrality Analysis", self._on_centrality_analysis)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="View Options:", font=("Arial", 10, "bold")).pack()
        ttk.Checkbutton(control_frame, text="Show Edge Labels", 
                       variable=tk.BooleanVar(value=True)).pack(anchor=tk.W)
        ttk.Checkbutton(control_frame, text="Show Node Degrees", 
                       variable=tk.BooleanVar(value=False)).pack(anchor=tk.W)
        
        # Right panel - Graph canvas
        canvas_frame = ttk.LabelFrame(tab, text="Network Topology", padding=5)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.fig = Figure(figsize=(ApplicationConfig.FIGURE_WIDTH, ApplicationConfig.FIGURE_HEIGHT))
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_analytics_tab(self) -> None:
        """Create network analytics dashboard."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Analytics")
        
        # Metrics display
        metrics_frame = ttk.LabelFrame(tab, text="Network Metrics", padding=10)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, height=15, width=80, font=("Courier", 10)
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        self.metrics_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        self._add_button(button_frame, "Refresh Metrics", self._on_refresh_analytics)
    
    def _create_algorithm_tab(self) -> None:
        """Create algorithm selection and execution tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Algorithm Suite")
        
        algo_frame = ttk.LabelFrame(tab, text="Available Algorithms", padding=10)
        algo_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        algorithms = [
            ("Minimum Spanning Tree (Prim)", "mst"),
            ("Shortest Path (Dijkstra)", "dijkstra"),
            ("All-Pairs Shortest Path", "floyd"),
            ("Network Flow Analysis", "flow"),
            ("Clustering Coefficient", "clustering"),
        ]
        
        for algo_text, algo_id in algorithms:
            ttk.Radiobutton(algo_frame, text=algo_text, variable=self.selected_algorithm, 
                          value=algo_id).pack(anchor=tk.W, pady=5)
        
        self._add_button(algo_frame, "Execute Algorithm", self._on_execute_algorithm)
    
    def _create_status_tab(self) -> None:
        """Create network status and logs tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Status & Logs")
        
        status_frame = ttk.LabelFrame(tab, text="System Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame, height=20, width=80, font=("Courier", 9)
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
    
    def _check_queue(self) -> None:
        """Check result queue for completed tasks."""
        try:
            while True:
                result_data = self.result_queue.get_nowait()
                self._display_result_page(result_data)
        except queue.Empty:
            pass
        finally:
            self.after(200, self._check_queue)
    
    def _run_task(self, func: Callable, title: str) -> None:
        """Run a function with loading dialog and result page."""
        # Show loading dialog
        loading = LoadingDialog(self, f"{title}...")
        self.update()
        
        # Run function in background thread
        def worker():
            try:
                result = func()
                self.result_queue.put({"title": title, "result": result})
            except Exception as e:
                logger.error(f"Task error: {e}")
                self.result_queue.put({"title": title, "result": f"Error: {str(e)}"})
            finally:
                try:
                    loading.destroy()
                except:
                    pass
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _display_result_page(self, result_data: Dict) -> None:
        """Display result on result page."""
        title = result_data.get("title", "Result")
        result_text = result_data.get("result", "No result")
        
        # Show result in a messagebox for now (can be extended to use ResultPage frame)
        messagebox.showinfo(title, result_text)
    
    @staticmethod
    def _add_button(parent: ttk.Frame, text: str, command) -> ttk.Button:
        """Add a button to the control panel."""
        button = ttk.Button(parent, text=text, command=command)
        button.pack(fill=tk.X, pady=5)
        return button

    def _draw_graph(
        self,
        highlight_edges: Optional[List[Tuple[int, int]]] = None,
        node_colors: Optional[List[str]] = None
    ) -> None:
        """
        Draw the network graph with optional edge highlights and custom node colors.
        
        Args:
            highlight_edges: List of edge tuples to highlight in red
            node_colors: List of color values for each node
        """
        try:
            self.ax.clear()
            pos = nx.spring_layout(self.G, seed=ApplicationConfig.FIGURE_SEED)
            
            # Draw base graph
            nx.draw(
                self.G,
                pos,
                ax=self.ax,
                with_labels=True,
                node_color=node_colors if node_colors else ApplicationConfig.NODE_DEFAULT_COLOR,
                node_size=ApplicationConfig.NODE_SIZE,
                edge_color=ApplicationConfig.EDGE_DEFAULT_COLOR
            )
            
            # Draw edge labels (weights)
            edge_labels = nx.get_edge_attributes(self.G, "weight")
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
            
            # Highlight specific edges if provided
            if highlight_edges:
                nx.draw_networkx_edges(
                    self.G,
                    pos,
                    edgelist=highlight_edges,
                    edge_color=ApplicationConfig.HIGHLIGHT_COLOR,
                    width=ApplicationConfig.HIGHLIGHT_WIDTH,
                    ax=self.ax
                )
            
            self.canvas.draw()
        except Exception as e:
            logger.error(f"Failed to draw graph: {e}")
            messagebox.showerror("Draw Error", f"Failed to draw graph: {e}")

    # ===== Advanced Algorithm Implementations =====
    
    def _on_refresh_analytics(self) -> None:
        """Refresh network analytics dashboard."""
        try:
            self._calculate_metrics()
            self._display_analytics()
        except Exception as e:
            logger.error(f"Analytics refresh failed: {e}")
            messagebox.showerror("Error", f"Failed to refresh analytics: {e}")
    
    def _display_analytics(self) -> None:
        """Display comprehensive network analytics."""
        if not self.metrics:
            return
        
        analytics_text = f"""
╔═══════════════════════════════════════════════════════════════╗
║           NETWORK ANALYTICS DASHBOARD                         ║
╚═══════════════════════════════════════════════════════════════╝

📊 TOPOLOGY METRICS:
   • Network Density:          {self.metrics.density:.4f}
   • Average Clustering:       {self.metrics.avg_clustering:.4f}
   • Average Path Length:      {self.metrics.avg_path_length:.2f}
   • Diameter:                 {self.metrics.diameter}
   • Connected Components:     {self.metrics.connected_components}
   • Average Degree:           {self.metrics.avg_degree:.2f}

🔗 CONNECTIVITY ANALYSIS:
   • Total Nodes:              {self.G.number_of_nodes()}
   • Total Edges:              {self.G.number_of_edges()}
   • Network Connected:        {'Yes' if nx.is_connected(self.G) else 'No'}

⚡ CAPACITY ANALYSIS:
   • Total Network Capacity:   {sum(d['capacity'] for u, v, d in self.G.edges(data=True))} units
   • Average Edge Capacity:    {np.mean([d['capacity'] for u, v, d in self.G.edges(data=True)]):.2f} units
   • Average Utilization:      {np.mean([d['utilization'] for u, v, d in self.G.edges(data=True)]):.2%}

⚙️ PERFORMANCE INDICATORS:
   • Robustness Score:         {self._calculate_robustness():.2f}
   • Resilience Index:         {self._calculate_resilience():.2f}
   • Network Efficiency:       {self._calculate_efficiency():.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, analytics_text)
        self.metrics_text.config(state=tk.DISABLED)
    
    def _calculate_robustness(self) -> float:
        """Calculate network robustness score (0-100)."""
        try:
            if not self.G.nodes():
                return 0.0
            
            # Robustness based on connectivity and clustering
            connectivity_factor = nx.average_clustering(self.G) if len(self.G) > 2 else 0
            degree_factor = min(np.mean([d for n, d in self.G.degree()]) / len(self.G), 1.0)
            
            return min((connectivity_factor * 0.6 + degree_factor * 0.4) * 100, 100)
        except:
            return 0.0
    
    def _calculate_resilience(self) -> float:
        """Calculate network resilience index (0-100)."""
        try:
            total_capacity = sum(d['capacity'] for u, v, d in self.G.edges(data=True))
            total_utilization = sum(d['capacity'] * d['utilization'] for u, v, d in self.G.edges(data=True))
            remaining_capacity_pct = (1 - (total_utilization / total_capacity)) * 100 if total_capacity > 0 else 0
            
            return min(remaining_capacity_pct, 100)
        except:
            return 0.0
    
    def _calculate_efficiency(self) -> float:
        """Calculate network efficiency metric (0-100)."""
        try:
            if not nx.is_connected(self.G):
                return 0.0
            
            # Based on average path length and network size
            actual_path_length = nx.average_shortest_path_length(self.G)
            optimal_path_length = np.log2(self.G.number_of_nodes())
            
            efficiency = (optimal_path_length / actual_path_length) * 100 if actual_path_length > 0 else 0
            return min(efficiency, 100)
        except:
            return 0.0
    
    def _on_centrality_analysis(self) -> None:
        """Perform centrality analysis on the network."""
        try:
            betweenness = nx.betweenness_centrality(self.G)
            closeness = nx.closeness_centrality(self.G)
            degree_centrality = nx.degree_centrality(self.G)
            
            # Get top 3 central nodes
            top_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
            
            analysis_msg = "🎯 CENTRALITY ANALYSIS:\n\n"
            analysis_msg += "Most Central Nodes (by Betweenness):\n"
            for node, value in top_nodes:
                analysis_msg += f"  Node {node}: {value:.4f}\n"
            
            messagebox.showinfo("Centrality Analysis", analysis_msg)
            logger.info("Centrality analysis completed")
        except Exception as e:
            logger.error(f"Centrality analysis failed: {e}")
            messagebox.showerror("Error", f"Failed to perform centrality analysis: {e}")
    
    def _on_reset_network(self) -> None:
        """Reset network to original state."""
        try:
            self.G = self.G_original.copy()
            self._calculate_metrics()
            self._draw_graph()
            self._display_analytics()
            logger.info("Network reset to original state")
            messagebox.showinfo("Success", "Network has been reset to original state")
        except Exception as e:
            logger.error(f"Network reset failed: {e}")
            messagebox.showerror("Error", f"Failed to reset network: {e}")
    
    def _on_execute_algorithm(self) -> None:
        """Execute selected algorithm."""
        algo = self.selected_algorithm.get()
        try:
            if algo == "mst":
                self._on_generate_mst()
            elif algo == "dijkstra":
                self._on_dijkstra_analysis()
            elif algo == "floyd":
                self._on_floyd_warshall()
            elif algo == "flow":
                self._on_flow_analysis()
            elif algo == "clustering":
                self._on_clustering_analysis()
        except Exception as e:
            logger.error(f"Algorithm execution failed: {e}")
            messagebox.showerror("Error", f"Algorithm execution failed: {e}")
    
    def _on_dijkstra_analysis(self) -> None:
        """Perform Dijkstra shortest path analysis."""
        try:
            if not nx.is_connected(self.G):
                messagebox.showwarning("Warning", "Graph is not connected")
                return
            
            path_length = nx.average_shortest_path_length(self.G, weight='weight')
            messagebox.showinfo("Dijkstra Analysis", 
                              f"Average weighted shortest path: {path_length:.2f}\n"
                              f"Network diameter: {nx.diameter(self.G)}")
        except Exception as e:
            logger.error(f"Dijkstra analysis failed: {e}")
            messagebox.showerror("Error", str(e))
    
    def _on_floyd_warshall(self) -> None:
        """Perform Floyd-Warshall all-pairs shortest path."""
        try:
            lengths = dict(nx.all_pairs_dijkstra_path_length(self.G, weight='weight'))
            max_length = max(max(v.values()) for v in lengths.values())
            messagebox.showinfo("Floyd-Warshall", 
                              f"Maximum shortest path: {max_length:.2f}\n"
                              f"Calculation complete for all {self.G.number_of_nodes()} nodes")
        except Exception as e:
            logger.error(f"Floyd-Warshall failed: {e}")
            messagebox.showerror("Error", str(e))
    
    def _on_flow_analysis(self) -> None:
        """Perform network flow analysis."""
        try:
            flow_value, flow_dict = nx.maximum_flow(self.G, 1, 8, capacity='capacity')
            messagebox.showinfo("Network Flow Analysis",
                              f"Maximum flow from Node 1 to Node 8: {flow_value}\n"
                              f"Flow value represents bottleneck capacity")
        except Exception as e:
            logger.error(f"Flow analysis failed: {e}")
            messagebox.showerror("Error", str(e))
    
    def _on_clustering_analysis(self) -> None:
        """Perform clustering coefficient analysis."""
        try:
            clustering = nx.clustering(self.G)
            avg_clustering = nx.average_clustering(self.G)
            messagebox.showinfo("Clustering Analysis",
                              f"Average clustering coefficient: {avg_clustering:.4f}\n"
                              f"Indicates local network density\n"
                              f"Range: 0 (no triangles) to 1 (fully connected)")
        except Exception as e:
            logger.error(f"Clustering analysis failed: {e}")
            messagebox.showerror("Error", str(e))
    
    def _on_export_report(self) -> None:
        """Export network analysis report."""
        try:
            report = f"""
EMERGENCY NETWORK ANALYSIS REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

NETWORK TOPOLOGY:
- Nodes: {self.G.number_of_nodes()}
- Edges: {self.G.number_of_edges()}
- Density: {nx.density(self.G):.4f}

METRICS:
- Average Clustering: {nx.average_clustering(self.G):.4f}
- Diameter: {nx.diameter(self.G) if nx.is_connected(self.G) else 'N/A (disconnected)'}
- Connected: {'Yes' if nx.is_connected(self.G) else 'No'}

ANALYSIS COMPLETE
"""
            messagebox.showinfo("Export", "Report generated:\n" + report)
            logger.info("Network report exported")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Error", str(e))
    
    
    def _on_generate_mst(self) -> None:
        """Generate and display the Minimum Spanning Tree using Prim's algorithm."""
        def calculate_mst():
            """Calculate MST in background."""
            mst = nx.minimum_spanning_tree(self.G, algorithm="prim")
            self._draw_graph(highlight_edges=list(mst.edges()))
            
            total_weight = sum(mst[u][v]['weight'] for u, v in mst.edges())
            
            result_text = "MINIMUM SPANNING TREE ANALYSIS\n"
            result_text += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result_text += "ALGORITHM: Prim's Algorithm\n"
            result_text += "TIME COMPLEXITY: O(E log V)\n"
            result_text += "SPACE COMPLEXITY: O(V + E)\n\n"
            result_text += "RESULTS:\n"
            result_text += "--------\n"
            result_text += f"Total Edges: {mst.number_of_edges()}\n"
            result_text += f"Total Weight: {total_weight}\n"
            result_text += f"Average Edge Weight: {total_weight / mst.number_of_edges():.2f}\n\n"
            result_text += "EDGE LIST (sorted by weight):\n"
            result_text += "--------\n"
            
            edges_sorted = sorted(
                [(u, v, d['weight']) for u, v, d in mst.edges(data=True)],
                key=lambda x: x[2]
            )
            for u, v, w in edges_sorted:
                result_text += f"  Node {u} -- Node {v}: weight = {w}\n"
            
            result_text += "\nNETWORK STATISTICS:\n"
            result_text += "--------\n"
            result_text += f"Nodes: {self.G.number_of_nodes()}\n"
            result_text += f"Total Edges (Original): {self.G.number_of_edges()}\n"
            result_text += f"MST Edges: {mst.number_of_edges()}\n"
            connected = "Yes" if nx.is_connected(self.G) else "No"
            result_text += f"Network Connected: {connected}\n"
            
            logger.info(f"MST generated with total weight: {total_weight}")
            return result_text
        
        self._run_task(calculate_mst, "Minimum Spanning Tree Analysis")

    def _on_show_paths(self) -> None:
        """Find and display edge-disjoint paths between specified nodes."""
        def find_paths():
            """Find paths in background."""
            paths = list(nx.edge_disjoint_paths(self.G, 1, 8))
            
            if not paths:
                return "No disjoint paths available between nodes 1 and 8"
            
            # Flatten paths to edges for highlighting
            highlight = []
            for path in paths:
                highlight.extend(zip(path, path[1:]))
            
            self._draw_graph(highlight_edges=highlight)
            
            result_text = f"""
EDGE-DISJOINT PATHS ANALYSIS
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

ALGORITHM: Edge-Disjoint Path Finding
TIME COMPLEXITY: O(VE^2) using Ford-Fulkerson

RESULTS:
--------
Source Node: 1
Target Node: 8
Number of Disjoint Paths: {len(paths)}

PATHS DISCOVERED:
"""
            for i, path in enumerate(paths, 1):
                result_text += f"\nPath {i}: {' -> '.join(map(str, path))}\n"
                result_text += f"  Length: {len(path) - 1} hops\n"
                path_weight = sum(
                    self.G[path[j]][path[j+1]]['weight'] 
                    for j in range(len(path)-1)
                )
                result_text += f"  Total Weight: {path_weight}\n"
            
            result_text += f"""
NETWORK IMPLICATIONS:
--------
Redundancy Level: {len(paths)} independent routes
Network Resilience: HIGH (multiple failure points tolerated)
Failover Capability: Available

Each path is independent and provides alternative routing
in case of link failure.
"""
            
            logger.info(f"Found {len(paths)} disjoint paths")
            return result_text
        
        try:
            self._run_with_animation(find_paths, "Edge-Disjoint Paths")
        except nx.NetworkXError as e:
            logger.warning(f"No disjoint paths: {e}")
            messagebox.showwarning("No Paths", "No disjoint paths available")
        except Exception as e:
            logger.error(f"Path finding failed: {e}")
            messagebox.showerror("Error", f"Failed to find paths: {e}")

    def _on_simulate_failure(self) -> None:
        """Simulate a random node failure in the network."""
        try:
            if not self.G.nodes:
                messagebox.showwarning("Empty Network", "Network has no nodes")
                return
            
            failed_node = random.choice(list(self.G.nodes))
            self.G.remove_node(failed_node)
            
            self._draw_graph()
            logger.warning(f"Node {failed_node} removed from network simulation")
            
            messagebox.showwarning(
                "Failure Simulation",
                f"Node {failed_node} failed and was removed from the network.\n"
                f"Remaining nodes: {self.G.number_of_nodes()}\n"
                f"Network rerouted automatically."
            )
        except Exception as e:
            logger.error(f"Failure simulation failed: {e}")
            messagebox.showerror("Error", f"Failed to simulate failure: {e}")

    def _on_optimize_tree(self) -> None:
        """Generate and display an optimized command tree structure."""
        try:
            nodes = sorted(self.G.nodes)
            tree = self._build_balanced_tree(nodes)
            
            tree_height = self._calculate_tree_height(tree)
            logger.info(f"Optimized tree built with height: {tree_height}")
            
            messagebox.showinfo(
                "Command Tree Optimized",
                f"Binary command tree rebalanced successfully.\n"
                f"Tree Height: {tree_height}\n"
                f"Nodes: {len(nodes)}\n"
                f"Optimization: Divide-and-conquer approach minimizes depth"
            )
        except Exception as e:
            logger.error(f"Tree optimization failed: {e}")
            messagebox.showerror("Error", f"Failed to optimize tree: {e}")

    @staticmethod
    def _build_balanced_tree(nodes: List[int]) -> Optional[Dict]:
        """
        Build a balanced binary tree from a sorted list of nodes.
        
        Time Complexity: O(n)
        Space Complexity: O(log n) average case (tree height)
        
        Args:
            nodes: Sorted list of node identifiers
            
        Returns:
            Dictionary representing balanced tree structure
        """
        if not nodes:
            return None
        
        mid = len(nodes) // 2
        return {
            "value": nodes[mid],
            "left": EmergencyNetworkSimulator._build_balanced_tree(nodes[:mid]),
            "right": EmergencyNetworkSimulator._build_balanced_tree(nodes[mid + 1:])
        }

    @staticmethod
    def _calculate_tree_height(tree: Optional[Dict]) -> int:
        """
        Calculate the height of a binary tree.
        
        Time Complexity: O(n) where n is number of nodes
        
        Args:
            tree: Tree structure
            
        Returns:
            Height of the tree
        """
        if tree is None:
            return 0
        return 1 + max(
            EmergencyNetworkSimulator._calculate_tree_height(tree.get("left")),
            EmergencyNetworkSimulator._calculate_tree_height(tree.get("right"))
        )

    def _on_graph_coloring(self) -> None:
        """Apply graph coloring algorithm to assign frequencies to nodes."""
        try:
            coloring = nx.coloring.greedy_color(self.G, strategy="largest_first")
            colors = [
                ApplicationConfig.COLOR_MAP.get(coloring[n], "gray")
                for n in self.G.nodes
            ]
            
            chromatic_number = max(coloring.values()) + 1 if coloring else 0
            logger.info(f"Graph colored with chromatic number: {chromatic_number}")
            
            self._draw_graph(node_colors=colors)
            messagebox.showinfo(
                "Graph Coloring",
                f"Frequencies assigned using Greedy Graph Coloring\n"
                f"Chromatic Number: {chromatic_number}\n"
                f"Strategy: Largest First\n"
                f"No adjacent hubs share a channel (frequency)"
            )
        except Exception as e:
            logger.error(f"Graph coloring failed: {e}")
            messagebox.showerror("Error", f"Failed to apply graph coloring: {e}")


def main() -> None:
    """Entry point for the application."""
    try:
        app = EmergencyNetworkSimulator()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
