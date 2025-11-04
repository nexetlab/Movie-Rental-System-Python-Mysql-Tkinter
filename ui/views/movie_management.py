"""
Movie Management GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from models.movie_model import MovieModel

logger = logging.getLogger(__name__)

class MovieManagementView(ttk.Frame):
    """Movie management interface with CRUD operations."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.movie_model = MovieModel()
        self.selected_movie_id = None
        
        self.create_widgets()
        self.apply_styling()
        self.load_movies()
    
    def create_widgets(self):
        """Create movie management widgets."""
        # Title
        title_label = ttk.Label(
            self,
            text="Movie Management",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.LabelFrame(self, text="Movie Details", padding=15)
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_form(form_frame)
        
        # Buttons frame
        self.create_buttons(form_frame)
        
        # Search frame
        search_frame = ttk.LabelFrame(self, text="Search Movies", padding=15)
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_search_form(search_frame)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Movies", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.create_results_table(results_frame)
    
    def create_form(self, parent):
        """Create movie form fields."""
        # Grid configuration
        for i in range(6):
            parent.columnconfigure(i, weight=1)
        
        # Row 1: Title and Director
        ttk.Label(parent, text="Title *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(parent, width=25)
        self.title_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        ttk.Label(parent, text="Director").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.director_entry = ttk.Entry(parent, width=25)
        self.director_entry.grid(row=0, column=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 2: Genre and Release Year
        ttk.Label(parent, text="Genre").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.genre_entry = ttk.Entry(parent, width=25)
        self.genre_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        ttk.Label(parent, text="Release Year").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.year_entry = ttk.Entry(parent, width=25)
        self.year_entry.grid(row=1, column=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 3: Duration and Rental Rate
        ttk.Label(parent, text="Duration (min)").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_entry = ttk.Entry(parent, width=25)
        self.duration_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        ttk.Label(parent, text="Rental Rate ($) *").grid(row=2, column=2, sticky=tk.W, pady=5)
        self.rate_entry = ttk.Entry(parent, width=25)
        self.rate_entry.grid(row=2, column=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 4: Total Copies
        ttk.Label(parent, text="Total Copies *").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.copies_entry = ttk.Entry(parent, width=25)
        self.copies_entry.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 5: Description
        ttk.Label(parent, text="Description").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(parent, width=80, height=4)
        self.desc_text.grid(row=4, column=1, columnspan=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
    
    def create_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=4, pady=15)
        
        buttons = [
            ("Add Movie", self.add_movie, '#27ae60'),
            ("Update Movie", self.update_movie, '#3498db'),
            ("Delete Movie", self.delete_movie, '#e74c3c'),
            ("Clear Form", self.clear_form, '#95a5a6'),
        ]
        
        for text, command, color in buttons:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                style=f'{color}.TButton'
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_search_form(self, parent):
        """Create search form."""
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.search_movies)
        
        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_movies,
            style='Primary.TButton'
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(
            search_frame,
            text="Clear Search",
            command=self.clear_search,
            style='Secondary.TButton'
        )
        clear_btn.pack(side=tk.LEFT)
    
    def create_results_table(self, parent):
        """Create movies results table."""
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('ID', 'Title', 'Director', 'Genre', 'Year', 'Duration', 'Rate', 'Stock', 'Available')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        # Specific column widths
        self.tree.column('Title', width=150)
        self.tree.column('Director', width=120)
        self.tree.column('Genre', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_movie_select)
    
    def apply_styling(self):
        """Apply styling to widgets."""
        style = ttk.Style()
        
        # Color buttons
        for color, hex_color in [('#27ae60', '#27ae60'), ('#3498db', '#3498db'), 
                               ('#e74c3c', '#e74c3c'), ('#95a5a6', '#95a5a6')]:
            style.configure(f'{color}.TButton', background=hex_color, foreground='white')
    
    def load_movies(self):
        """Load all movies into the table."""
        success, message, movies = self.movie_model.get_all_movies()
        if success:
            self.populate_table(movies)
        else:
            messagebox.showerror("Error", message)
    
    def populate_table(self, movies):
        """Populate table with movie data."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add movies to table
        for movie in movies:
            self.tree.insert('', tk.END, values=(
                movie['movie_id'],
                movie['title'],
                movie['director'] or '',
                movie['genre'] or '',
                movie['release_year'] or '',
                movie['duration'] or '',
                f"${movie['rental_rate']:.2f}",
                movie['stock_quantity'],
                'Yes' if movie['is_available'] else 'No'
            ))
    
    def on_movie_select(self, event):
        """Handle movie selection from table."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            self.selected_movie_id = int(values[0])
            self.populate_form(values)
    
    def populate_form(self, values):
        """Populate form with selected movie data."""
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, values[1])
        
        self.director_entry.delete(0, tk.END)
        self.director_entry.insert(0, values[2])
        
        self.genre_entry.delete(0, tk.END)
        self.genre_entry.insert(0, values[3])
        
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, values[4])
        
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, values[5])
        
        # Remove $ from rate
        rate = values[6].replace('$', '')
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, rate)
        
        # For copies, we'd need to get the actual movie data
        # This is a simplification
        self.copies_entry.delete(0, tk.END)
        self.copies_entry.insert(0, values[7])
        
        self.desc_text.delete('1.0', tk.END)
    
    def get_form_data(self):
        """Get and validate form data."""
        title = self.title_entry.get().strip()
        director = self.director_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        duration = self.duration_entry.get().strip()
        rate = self.rate_entry.get().strip()
        copies = self.copies_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        
        # Validate required fields
        if not title:
            messagebox.showerror("Error", "Title is required")
            return None
        
        if not rate:
            messagebox.showerror("Error", "Rental rate is required")
            return None
        
        if not copies:
            messagebox.showerror("Error", "Total copies is required")
            return None
        
        # Convert numeric fields
        try:
            release_year = int(year) if year else None
            duration_min = int(duration) if duration else None
            rental_rate = float(rate)
            total_copies = int(copies)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for numeric fields")
            return None
        
        return {
            'title': title,
            'director': director or None,
            'genre': genre or None,
            'release_year': release_year,
            'duration': duration_min,
            'description': description or None,
            'rental_rate': rental_rate,
            'total_copies': total_copies
        }
    
    def add_movie(self):
        """Add new movie."""
        data = self.get_form_data()
        if not data:
            return
        
        success, message, movie_id = self.movie_model.add_movie(**data)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_movies()
        else:
            messagebox.showerror("Error", message)
    
    def update_movie(self):
        """Update selected movie."""
        if not self.selected_movie_id:
            messagebox.showwarning("Warning", "Please select a movie to update")
            return
        
        data = self.get_form_data()
        if not data:
            return
        
        success, message = self.movie_model.update_movie(self.selected_movie_id, **data)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_movies()
        else:
            messagebox.showerror("Error", message)
    
    def delete_movie(self):
        """Delete selected movie."""
        if not self.selected_movie_id:
            messagebox.showwarning("Warning", "Please select a movie to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this movie?"):
            success, message = self.movie_model.delete_movie(self.selected_movie_id)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_movies()
            else:
                messagebox.showerror("Error", message)
    
    def search_movies(self, event=None):
        """Search movies based on search term."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_movies()
            return
        
        success, message, movies = self.movie_model.search_movies(title=search_term)
        if success:
            self.populate_table(movies)
        else:
            messagebox.showerror("Error", message)
    
    def clear_search(self):
        """Clear search and show all movies."""
        self.search_entry.delete(0, tk.END)
        self.load_movies()
    
    def clear_form(self):
        """Clear all form fields."""
        self.title_entry.delete(0, tk.END)
        self.director_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)
        self.copies_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)
        self.selected_movie_id = None
        
        # Clear tree selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)