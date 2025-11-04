"""
Reports and Analytics View - FIXED VERSION
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.exporters import ReportExporter
from utils.visualization import ModernDataVisualizer  # Updated import
import os

logger = logging.getLogger(__name__)

class ReportsView(ttk.Frame):
    """Reports and analytics interface."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.exporter = ReportExporter()
        self.visualizer = ModernDataVisualizer()  # Updated class name
        self.current_charts = []
        
        self.create_widgets()
        self.apply_styling()
    
    def create_widgets(self):
        """Create reports and analytics widgets."""
        # Title
        title_label = ttk.Label(
            self,
            text="Reports & Analytics",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Export buttons frame
        export_frame = ttk.LabelFrame(self, text="Export Reports", padding=15)
        export_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_export_buttons(export_frame)
        
        # Charts frame
        charts_frame = ttk.LabelFrame(self, text="Data Visualization", padding=15)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.create_charts_interface(charts_frame)
    
    def create_export_buttons(self, parent):
        """Create export report buttons."""
        # Button definitions: (text, command, tooltip)
        export_buttons = [
            ("📊 Current Rentals", self.export_current_rentals, 
             "Export currently rented movies to Excel"),
            ("⚠️ Overdue Rentals", self.export_overdue_rentals,
             "Export overdue rentals with late fees"),
            ("🎬 Genre Statistics", self.export_genre_stats,
             "Export rental statistics by genre"),
            ("📈 Monthly Trends", self.export_monthly_trends,
             "Export monthly rental trends"),
            ("📋 Comprehensive Report", self.export_comprehensive,
             "Export all reports in one Excel file")
        ]
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        for i, (text, command, tooltip) in enumerate(export_buttons):
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                style='Export.TButton',
                width=20
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Simple tooltip implementation
            self.create_tooltip(btn, tooltip)
    
    def create_charts_interface(self, parent):
        """Create charts and visualization interface."""
        # Chart controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        chart_types = [
            ("📊 Genre Analysis", self.show_modern_genre_chart),
            ("📈 Trends", self.show_modern_trend_chart),
            ("💰 Revenue", self.show_modern_revenue_chart),
            ("📋 Dashboard", self.show_metrics_dashboard)
        ]
        
        for text, command in chart_types:
            btn = ttk.Button(
                controls_frame,
                text=text,
                command=command,
                style='Chart.TButton',
                width=15
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_charts,
            style='Primary.TButton'
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Charts container
        self.charts_container = ttk.Frame(parent)
        self.charts_container.pack(fill=tk.BOTH, expand=True)
        
        # Show default chart
        self.show_modern_genre_chart()
    
    def create_tooltip(self, widget, text):
        """Create a simple tooltip for widgets."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def apply_styling(self):
        """Apply styling to widgets."""
        style = ttk.Style()
        
        # Export buttons
        style.configure('Export.TButton', 
                       background='#3498db',
                       foreground='white',
                       font=('Arial', 10))
        
        style.map('Export.TButton',
                 background=[('active', '#2980b9'),
                           ('pressed', '#2471a3')])
        
        # Chart buttons
        style.configure('Chart.TButton',
                       background='#9b59b6',
                       foreground='white',
                       font=('Arial', 9))
        
        style.map('Chart.TButton',
                 background=[('active', '#8e44ad'),
                           ('pressed', '#7d3c98')])
    
    def clear_charts(self):
        """Clear current charts."""
        for chart in self.current_charts:
            try:
                chart.get_tk_widget().destroy()
            except:
                pass
        self.current_charts = []
        
        # Clear container
        for widget in self.charts_container.winfo_children():
            widget.destroy()
    
    def show_modern_genre_chart(self):
        """Show modern genre chart."""
        self.clear_charts()
        
        chart_canvas = self.visualizer.create_modern_genre_chart(self.charts_container)
        if chart_canvas:
            chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.current_charts.append(chart_canvas)
    
    def show_modern_trend_chart(self):
        """Show modern trend chart."""
        self.clear_charts()
        
        chart_canvas = self.visualizer.create_modern_trend_chart(self.charts_container)
        if chart_canvas:
            chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.current_charts.append(chart_canvas)
    
    def show_modern_revenue_chart(self):
        """Show modern revenue chart."""
        self.clear_charts()
        
        chart_canvas = self.visualizer.create_modern_revenue_chart(self.charts_container)
        if chart_canvas:
            chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.current_charts.append(chart_canvas)
    
    def show_metrics_dashboard(self):
        """Show modern metrics dashboard."""
        self.clear_charts()
        
        chart_canvas = self.visualizer.create_modern_metrics_dashboard(self.charts_container)
        if chart_canvas:
            chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.current_charts.append(chart_canvas)
    
    def refresh_charts(self):
        """Refresh all charts with latest data."""
        if self.current_charts:
            # For now, just re-create the current chart type
            current_method_name = None
            if hasattr(self.visualizer, 'create_modern_genre_chart'):
                current_method_name = 'create_modern_genre_chart'
            elif hasattr(self.visualizer, 'create_modern_trend_chart'):
                current_method_name = 'create_modern_trend_chart'
            elif hasattr(self.visualizer, 'create_modern_revenue_chart'):
                current_method_name = 'create_modern_revenue_chart'
            elif hasattr(self.visualizer, 'create_modern_metrics_dashboard'):
                current_method_name = 'create_modern_metrics_dashboard'
            
            if current_method_name:
                current_method = getattr(self.visualizer, current_method_name)
                self.clear_charts()
                chart_canvas = current_method(self.charts_container)
                if chart_canvas:
                    chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                    self.current_charts.append(chart_canvas)
        
        messagebox.showinfo("Refresh", "Charts updated with latest data!")
    
    def export_current_rentals(self):
        """Export current rentals report."""
        success, message, file_path = self.exporter.export_current_rentals()
        if success:
            self.show_export_success(message, file_path)
        else:
            messagebox.showerror("Export Failed", message)
    
    def export_overdue_rentals(self):
        """Export overdue rentals report."""
        success, message, file_path = self.exporter.export_overdue_rentals()
        if success:
            self.show_export_success(message, file_path)
        else:
            messagebox.showerror("Export Failed", message)
    
    def export_genre_stats(self):
        """Export genre statistics report."""
        success, message, file_path = self.exporter.export_rental_stats_by_genre()
        if success:
            self.show_export_success(message, file_path)
        else:
            messagebox.showerror("Export Failed", message)
    
    def export_monthly_trends(self):
        """Export monthly trends report."""
        success, message, file_path = self.exporter.export_monthly_rental_trends()
        if success:
            self.show_export_success(message, file_path)
        else:
            messagebox.showerror("Export Failed", message)
    
    def export_comprehensive(self):
        """Export comprehensive report."""
        success, message, file_path = self.exporter.export_comprehensive_report()
        if success:
            self.show_export_success(message, file_path)
        else:
            messagebox.showerror("Export Failed", message)
    
    def show_export_success(self, message, file_path):
        """Show export success message with option to open file."""
        result = messagebox.askyesno(
            "Export Successful", 
            f"{message}\n\nWould you like to open the file?",
            icon='info'
        )
        
        if result and file_path:
            try:
                # Open the file with default application
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS, Linux
                    os.system(f'open "{file_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{file_path}"')
            except Exception as e:
                logger.error(f"Failed to open file: {e}")
                messagebox.showinfo("File Location", f"File saved to:\n{file_path}")