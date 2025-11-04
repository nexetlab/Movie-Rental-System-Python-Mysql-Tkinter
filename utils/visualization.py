"""
Modern data visualization using matplotlib with contemporary styling.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import tkinter as tk
from datetime import datetime
import logging
from models.rental_model import RentalModel
from models.movie_model import MovieModel

logger = logging.getLogger(__name__)

class ModernDataVisualizer:
    """Modern data visualization with contemporary styling."""
    
    def __init__(self):
        self.rental_model = RentalModel()
        self.movie_model = MovieModel()
        
        # Modern color palette
        self.colors = {
            'primary': '#4361ee',
            'secondary': '#7209b7', 
            'accent': '#f72585',
            'success': '#4cc9f0',
            'warning': '#f8961e',
            'error': '#e63946',
            'dark': '#1d3557',
            'light': '#f1faee',
            'gray': '#a8dadc'
        }
        
        # Modern matplotlib style
        self.set_modern_style()
    
    def set_modern_style(self):
        """Configure modern matplotlib style."""
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Customize rcParams for modern look
        plt.rcParams.update({
            'figure.facecolor': '#f8f9fa',
            'axes.facecolor': '#ffffff',
            'axes.edgecolor': '#dee2e6',
            'axes.labelcolor': '#1d3557',
            'axes.titlecolor': '#1d3557',
            'text.color': '#1d3557',
            'xtick.color': '#457b9d',
            'ytick.color': '#457b9d',
            'grid.color': '#dee2e6',
            'grid.alpha': 0.3,
            'font.family': 'Segoe UI, sans-serif',
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 11,
            'legend.fontsize': 10
        })
    
    def create_modern_genre_chart(self, parent):
        """Create modern rentals by genre donut chart."""
        try:
            success, message, rentals = self.rental_model.search_rentals()
            if not success or not rentals:
                return self._create_empty_chart(parent, "No rental data available")
            
            movie_success, movie_message, movies = self.movie_model.get_all_movies()
            if not movie_success:
                return self._create_empty_chart(parent, "No movie data available")
            
            # Count rentals by genre
            movie_genres = {}
            for movie in movies:
                movie_genres[movie['movie_id']] = movie.get('genre', 'Unknown')
            
            genre_counts = {}
            for rental in rentals:
                genre = movie_genres.get(rental['movie_id'], 'Unknown')
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            if not genre_counts:
                return self._create_empty_chart(parent, "No genre data available")
            
            # Prepare data
            genres = list(genre_counts.keys())
            counts = list(genre_counts.values())
            
            # Create modern donut chart
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Use modern color palette
            colors = [self.colors['primary'], self.colors['secondary'], 
                     self.colors['accent'], self.colors['success'],
                     self.colors['warning'], self.colors['gray']]
            
            # Create donut chart
            wedges, texts, autotexts = ax.pie(
                counts,
                labels=genres,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(genres)],
                wedgeprops={'edgecolor': 'white', 'linewidth': 2},
                textprops={'fontsize': 10, 'color': self.colors['dark']}
            )
            
            # Draw circle in the center for donut effect
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            # Style the chart
            ax.set_title('Rentals by Genre', 
                        fontsize=16, 
                        fontweight='bold', 
                        color=self.colors['dark'],
                        pad=20)
            
            # Improve text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            # Equal aspect ratio ensures pie is drawn as circle
            ax.axis('equal')
            plt.tight_layout()
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            
            return canvas
            
        except Exception as e:
            logger.error(f"Create modern genre chart failed: {e}")
            return self._create_empty_chart(parent, f"Error creating chart: {str(e)}")
    
    def create_modern_trend_chart(self, parent):
        """Create modern monthly trend chart with gradient fill."""
        try:
            success, message, rentals = self.rental_model.search_rentals()
            if not success or not rentals:
                return self._create_empty_chart(parent, "No rental data available")
            
            # Group by month
            monthly_data = {}
            for rental in rentals:
                rental_date = rental['rental_date']
                month_key = rental_date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += 1
            
            # Sort by month
            sorted_months = sorted(monthly_data.keys())
            counts = [monthly_data[month] for month in sorted_months]
            
            if len(sorted_months) < 2:
                return self._create_empty_chart(parent, "Insufficient data for trend analysis")
            
            # Create modern area chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create gradient fill under line
            ax.fill_between(sorted_months, counts, alpha=0.3, color=self.colors['primary'])
            
            # Create modern line
            line = ax.plot(sorted_months, counts, 
                          marker='o', 
                          linewidth=3, 
                          markersize=8,
                          color=self.colors['primary'],
                          markerfacecolor=self.colors['accent'],
                          markeredgecolor='white',
                          markeredgewidth=2)[0]
            
            # Style the chart
            ax.set_title('Monthly Rental Trends', 
                        fontsize=16, 
                        fontweight='bold', 
                        color=self.colors['dark'],
                        pad=20)
            
            ax.set_xlabel('Month', fontsize=12, color=self.colors['dark'], labelpad=10)
            ax.set_ylabel('Number of Rentals', fontsize=12, color=self.colors['dark'], labelpad=10)
            
            # Modern grid
            ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Add value annotations with modern style
            for i, (month, count) in enumerate(zip(sorted_months, counts)):
                ax.annotate(str(count), (month, count), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center', 
                           fontsize=9,
                           fontweight='bold',
                           color=self.colors['dark'])
            
            plt.tight_layout()
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            
            return canvas
            
        except Exception as e:
            logger.error(f"Create modern trend chart failed: {e}")
            return self._create_empty_chart(parent, f"Error creating chart: {str(e)}")
    
    def create_modern_revenue_chart(self, parent):
        """Create modern horizontal bar chart for revenue by genre."""
        try:
            success, message, rentals = self.rental_model.search_rentals()
            if not success or not rentals:
                return self._create_empty_chart(parent, "No rental data available")
            
            movie_success, movie_message, movies = self.movie_model.get_all_movies()
            if not movie_success:
                return self._create_empty_chart(parent, "No movie data available")
            
            # Calculate revenue by genre
            movie_genres = {}
            for movie in movies:
                movie_genres[movie['movie_id']] = movie.get('genre', 'Unknown')
            
            genre_revenue = {}
            for rental in rentals:
                genre = movie_genres.get(rental['movie_id'], 'Unknown')
                revenue = float(rental['total_charge'] or 0)
                genre_revenue[genre] = genre_revenue.get(genre, 0) + revenue
            
            if not genre_revenue:
                return self._create_empty_chart(parent, "No revenue data available")
            
            # Prepare data and sort by revenue
            genres = list(genre_revenue.keys())
            revenues = list(genre_revenue.values())
            
            # Sort by revenue (descending)
            sorted_data = sorted(zip(genres, revenues), key=lambda x: x[1], reverse=True)
            genres, revenues = zip(*sorted_data) if sorted_data else ([], [])
            
            # Create modern horizontal bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create gradient bars
            bars = ax.barh(genres, revenues, 
                          color=self.colors['primary'],
                          alpha=0.8,
                          height=0.6)
            
            # Add value labels
            for i, (bar, revenue) in enumerate(zip(bars, revenues)):
                width = bar.get_width()
                ax.text(width + max(revenues) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'${revenue:.2f}', 
                       ha='left', va='center',
                       fontsize=10, fontweight='bold',
                       color=self.colors['dark'])
            
            # Style the chart
            ax.set_title('Revenue by Genre', 
                        fontsize=16, 
                        fontweight='bold', 
                        color=self.colors['dark'],
                        pad=20)
            
            ax.set_xlabel('Total Revenue ($)', fontsize=12, color=self.colors['dark'], labelpad=10)
            
            # Modern styling
            ax.grid(True, alpha=0.2, axis='x')
            ax.set_axisbelow(True)
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Tight layout
            plt.tight_layout()
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            
            return canvas
            
        except Exception as e:
            logger.error(f"Create modern revenue chart failed: {e}")
            return self._create_empty_chart(parent, f"Error creating chart: {str(e)}")
    
    def create_modern_metrics_dashboard(self, parent):
        """Create a modern metrics dashboard with multiple charts."""
        try:
            # Create a 2x2 grid of charts
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Rental Analytics Dashboard', fontsize=20, fontweight='bold', 
                        color=self.colors['dark'], y=0.95)
            
            # Get data
            success, message, rentals = self.rental_model.search_rentals()
            if not success or not rentals:
                return self._create_empty_chart(parent, "No rental data available")
            
            # Chart 1: Rental status (simplified pie)
            status_counts = {'Active': 0, 'Returned': 0, 'Overdue': 0}
            for rental in rentals:
                status = rental['rental_status'].title()
                status_counts[status] = status_counts.get(status, 0) + 1
            
            ax1.pie(status_counts.values(), labels=status_counts.keys(), 
                   autopct='%1.1f%%', colors=[self.colors['primary'], self.colors['success'], self.colors['error']])
            ax1.set_title('Rental Status', fontweight='bold')
            
            # Chart 2: Monthly trend (mini)
            monthly_data = {}
            for rental in rentals:
                month_key = rental['rental_date'].strftime('%Y-%m')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
            
            sorted_months = sorted(monthly_data.keys())[-6:]  # Last 6 months
            counts = [monthly_data[month] for month in sorted_months]
            
            ax2.plot(sorted_months, counts, marker='o', color=self.colors['primary'])
            ax2.set_title('Recent Trends (6 Months)', fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)
            
            # Chart 3: Top genres (horizontal bars)
            # ... implementation similar to previous methods
            
            # Chart 4: Revenue distribution
            revenues = [float(r['total_charge'] or 0) for r in rentals]
            ax4.hist(revenues, bins=10, color=self.colors['primary'], alpha=0.7)
            ax4.set_title('Revenue Distribution', fontweight='bold')
            ax4.set_xlabel('Revenue ($)')
            ax4.set_ylabel('Frequency')
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            return canvas
            
        except Exception as e:
            logger.error(f"Create metrics dashboard failed: {e}")
            return self._create_empty_chart(parent, f"Error creating dashboard: {str(e)}")
    
    def _create_empty_chart(self, parent, message):
        """Create a modern empty chart with message."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', 
               transform=ax.transAxes, fontsize=12, style='italic',
               bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['light'], 
                        edgecolor=self.colors['border'], alpha=0.7))
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas