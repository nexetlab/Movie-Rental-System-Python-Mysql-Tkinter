"""
Customer Management GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from models.customer_model import CustomerModel

logger = logging.getLogger(__name__)

class CustomerManagementView(ttk.Frame):
    """Customer management interface with CRUD operations."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.customer_model = CustomerModel()
        self.selected_customer_id = None
        
        self.create_widgets()
        self.apply_styling()
        self.load_customers()
    
    def create_widgets(self):
        """Create customer management widgets."""
        # Title
        title_label = ttk.Label(
            self,
            text="Customer Management",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.LabelFrame(self, text="Customer Details", padding=15)
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_form(form_frame)
        
        # Buttons frame
        self.create_buttons(form_frame)
        
        # Search frame
        search_frame = ttk.LabelFrame(self, text="Search Customers", padding=15)
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_search_form(search_frame)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Customers", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.create_results_table(results_frame)
    
    def create_form(self, parent):
        """Create customer form fields."""
        # Grid configuration
        for i in range(4):
            parent.columnconfigure(i, weight=1)
        
        # Row 1: First Name and Last Name
        ttk.Label(parent, text="First Name *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.first_name_entry = ttk.Entry(parent, width=25)
        self.first_name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        ttk.Label(parent, text="Last Name *").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.last_name_entry = ttk.Entry(parent, width=25)
        self.last_name_entry.grid(row=0, column=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 2: Email and Phone
        ttk.Label(parent, text="Email").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(parent, width=25)
        self.email_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        ttk.Label(parent, text="Phone").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(parent, width=25)
        self.phone_entry.grid(row=1, column=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
        
        # Row 3: Address
        ttk.Label(parent, text="Address").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.address_text = tk.Text(parent, width=80, height=3)
        self.address_text.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=5, padx=(0, 10))
    
    def create_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        buttons = [
            ("Add Customer", self.add_customer, '#27ae60'),
            ("Update Customer", self.update_customer, '#3498db'),
            ("Delete Customer", self.delete_customer, '#e74c3c'),
            ("Clear Form", self.clear_form, '#95a5a6'),
            ("View Rentals", self.view_rentals, '#9b59b6'),
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
        
        ttk.Label(search_frame, text="Search (Name or ID):").pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.search_customers)
        
        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_customers,
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
        """Create customers results table."""
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Registered', 'Active')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Specific column widths
        self.tree.column('Email', width=150)
        self.tree.column('Registered', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_customer_select)
    
    def apply_styling(self):
        """Apply styling to widgets."""
        style = ttk.Style()
        
        # Color buttons
        for color, hex_color in [('#27ae60', '#27ae60'), ('#3498db', '#3498db'), 
                               ('#e74c3c', '#e74c3c'), ('#95a5a6', '#95a5a6'),
                               ('#9b59b6', '#9b59b6')]:
            style.configure(f'{color}.TButton', background=hex_color, foreground='white')
    
    def load_customers(self):
        """Load all customers into the table."""
        success, message, customers = self.customer_model.get_all_customers()
        if success:
            self.populate_table(customers)
        else:
            messagebox.showerror("Error", message)
    
    def populate_table(self, customers):
        """Populate table with customer data."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add customers to table
        for customer in customers:
            self.tree.insert('', tk.END, values=(
                customer['customer_id'],
                customer['first_name'],
                customer['last_name'],
                customer['email'] or '',
                customer['phone'] or '',
                customer['date_registered'].strftime('%Y-%m-%d'),
                'Yes' if customer['is_active'] else 'No'
            ))
    
    def on_customer_select(self, event):
        """Handle customer selection from table."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            self.selected_customer_id = int(values[0])
            self.populate_form(values)
    
    def populate_form(self, values):
        """Populate form with selected customer data."""
        self.first_name_entry.delete(0, tk.END)
        self.first_name_entry.insert(0, values[1])
        
        self.last_name_entry.delete(0, tk.END)
        self.last_name_entry.insert(0, values[2])
        
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, values[3])
        
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, values[4])
        
        self.address_text.delete('1.0', tk.END)
    
    def get_form_data(self):
        """Get and validate form data."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_text.get('1.0', tk.END).strip()
        
        # Validate required fields
        if not first_name:
            messagebox.showerror("Error", "First name is required")
            return None
        
        if not last_name:
            messagebox.showerror("Error", "Last name is required")
            return None
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': email or None,
            'phone': phone or None,
            'address': address or None
        }
    
    def add_customer(self):
        """Add new customer."""
        data = self.get_form_data()
        if not data:
            return
        
        success, message, customer_id = self.customer_model.add_customer(**data)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_customers()
        else:
            messagebox.showerror("Error", message)
    
    def update_customer(self):
        """Update selected customer."""
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "Please select a customer to update")
            return
        
        data = self.get_form_data()
        if not data:
            return
        
        success, message = self.customer_model.update_customer(self.selected_customer_id, **data)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_customers()
        else:
            messagebox.showerror("Error", message)
    
    def delete_customer(self):
        """Delete selected customer."""
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
            success, message = self.customer_model.delete_customer(self.selected_customer_id)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_customers()
            else:
                messagebox.showerror("Error", message)
    
    def view_rentals(self):
        """View rental history for selected customer."""
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "Please select a customer to view rentals")
            return
        
        # This would open a rental history window
        # For now, show a message
        success, message, rentals = self.customer_model.get_customer_rental_history(self.selected_customer_id)
        if success:
            if rentals:
                rental_info = "\n".join([f"- {r['title']} ({r['rental_status']})" for r in rentals[:5]])
                messagebox.showinfo(
                    f"Rental History - Customer {self.selected_customer_id}",
                    f"Found {len(rentals)} rentals:\n\n{rental_info}" + 
                    ("\n\n..." if len(rentals) > 5 else "")
                )
            else:
                messagebox.showinfo("Rental History", "No rental history found for this customer")
        else:
            messagebox.showerror("Error", message)
    
    def search_customers(self, event=None):
        """Search customers based on search term."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_customers()
            return
        
        success, message, customers = self.customer_model.search_customers(search_term)
        if success:
            self.populate_table(customers)
        else:
            messagebox.showerror("Error", message)
    
    def clear_search(self):
        """Clear search and show all customers."""
        self.search_entry.delete(0, tk.END)
        self.load_customers()
    
    def clear_form(self):
        """Clear all form fields."""
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_text.delete('1.0', tk.END)
        self.selected_customer_id = None
        
        # Clear tree selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)