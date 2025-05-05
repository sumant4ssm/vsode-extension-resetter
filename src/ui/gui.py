"""
Graphical user interface for VSCode Extension Resetter.

This is a simple GUI implementation using tkinter.
For a more advanced GUI, consider using PyQt or wxPython.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import logging

from ..core.utils import (
    get_platform,
    get_extension_list,
    list_backups,
    logger
)
from ..core.machine_id import (
    get_current_machine_id,
    reset_machine_id,
    restore_machine_id
)
from ..core.extension_data import (
    list_extension_data,
    reset_extension_data,
    restore_extension_data,
    backup_extension_data
)
from ..core.storage_cleaner import (
    backup_global_storage,
    clean_global_storage,
    backup_state_db,
    reset_state_db,
    restore_state_db,
    clean_storage_json
)

# Import platform-specific modules
if get_platform() == "windows":
    from ..platforms.windows import clean_vscode_registry, clean_appdata_local
elif get_platform() == "macos":
    from ..platforms.macos import clean_vscode_plist, clean_application_support
else:  # linux
    from ..platforms.linux import clean_vscode_config, clean_dconf_settings

class QueueHandler(logging.Handler):
    """
    A logging handler that puts logs into a queue.
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class VSCodeResetterGUI:
    """
    Graphical user interface for VSCode Extension Resetter.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("VSCode Extension Resetter")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)

        # Set application icon if available
        try:
            if get_platform() == "windows":
                self.root.iconbitmap("icon.ico")
            else:
                icon = tk.PhotoImage(file="icon.png")
                self.root.iconphoto(True, icon)
        except:
            pass

        # Configure style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TCheckbutton", background="#f5f5f5", font=("Segoe UI", 10))
        self.style.configure("TNotebook", background="#f5f5f5", tabposition="n")
        self.style.configure("TNotebook.Tab", padding=[10, 5], font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#f5f5f5", font=("Segoe UI", 10))
        self.style.configure("TLabelframe.Label", background="#f5f5f5", font=("Segoe UI", 10, "bold"))

        # Set up logging to GUI
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)

        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create header with title and description
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(header_frame, text="VSCode Extension Resetter", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W)

        desc_label = ttk.Label(header_frame, text="Reset extension tracking data completely, even after uninstallation")
        desc_label.pack(anchor=tk.W)

        # Create the notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create tabs
        self.info_tab = ttk.Frame(self.notebook, padding=10)
        self.machine_id_tab = ttk.Frame(self.notebook, padding=10)
        self.extensions_tab = ttk.Frame(self.notebook, padding=10)
        self.backup_restore_tab = ttk.Frame(self.notebook, padding=10)
        self.clean_all_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.info_tab, text="Info")
        self.notebook.add(self.machine_id_tab, text="Machine ID")
        self.notebook.add(self.extensions_tab, text="Extensions")
        self.notebook.add(self.backup_restore_tab, text="Backup/Restore")
        self.notebook.add(self.clean_all_tab, text="Clean All")

        # Create the log frame
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create log controls frame
        log_controls = ttk.Frame(self.log_frame)
        log_controls.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

        # Add clear logs button
        clear_logs_button = ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs)
        clear_logs_button.pack(side=tk.RIGHT)

        # Create the log text widget
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(background="#f8f8f8", foreground="#333333")

        # Create status bar
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        status_label = ttk.Label(status_frame, text=f"Platform: {get_platform().capitalize()}")
        status_label.pack(side=tk.LEFT)

        version_label = ttk.Label(status_frame, text="v0.1.0")
        version_label.pack(side=tk.RIGHT)

        # Initialize tabs
        self.init_info_tab()
        self.init_machine_id_tab()
        self.init_extensions_tab()
        self.init_backup_restore_tab()
        self.init_clean_all_tab()

        # Start the log consumer
        self.log_consumer()

    def clear_logs(self):
        """
        Clear the log text widget.
        """
        self.log_text.delete(1.0, tk.END)
        logger.info("Logs cleared")

    def log_consumer(self):
        """
        Consume logs from the queue and display them in the log text widget.
        """
        try:
            while True:
                record = self.log_queue.get_nowait()
                msg = self.queue_handler.format(record)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_queue.task_done()
        except queue.Empty:
            self.root.after(100, self.log_consumer)

    def init_info_tab(self):
        """
        Initialize the Info tab.
        """
        # Create the info frame
        info_frame = ttk.Frame(self.info_tab, padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Create the info text widget
        self.info_text = scrolledtext.ScrolledText(info_frame)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Create the refresh button
        refresh_button = ttk.Button(info_frame, text="Refresh", command=self.refresh_info)
        refresh_button.pack(pady=5)

        # Initial refresh
        self.refresh_info()

    def refresh_info(self):
        """
        Refresh the information in the Info tab.
        """
        self.info_text.delete(1.0, tk.END)

        self.info_text.insert(tk.END, "VSCode Extension Resetter\n")
        self.info_text.insert(tk.END, "------------------------\n\n")

        self.info_text.insert(tk.END, f"Platform: {get_platform()}\n\n")

        machine_id = get_current_machine_id()
        self.info_text.insert(tk.END, f"Machine ID: {machine_id or 'Not found'}\n\n")

        extensions = get_extension_list()
        self.info_text.insert(tk.END, f"Installed extensions: {len(extensions)}\n\n")

        extension_data = list_extension_data()
        self.info_text.insert(tk.END, f"Extensions with data: {len(extension_data)}\n\n")

        backups = list_backups()
        self.info_text.insert(tk.END, f"Available backups: {len(backups)}\n\n")

    def init_machine_id_tab(self):
        """
        Initialize the Machine ID tab.
        """
        # Create the machine ID frame
        machine_id_frame = ttk.Frame(self.machine_id_tab, padding=10)
        machine_id_frame.pack(fill=tk.BOTH, expand=True)

        # Create info section
        info_frame = ttk.LabelFrame(machine_id_frame, text="About Machine ID")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = ttk.Label(
            info_frame,
            text="The Machine ID is a unique identifier used by VSCode to track installations.\n"
                 "Resetting it will make VSCode generate a new ID, which can help with:\n"
                 "• Resetting extension trials\n"
                 "• Preventing extension tracking\n"
                 "• Resolving licensing issues with some extensions",
            wraplength=600,
            justify=tk.LEFT,
            padding=10
        )
        info_text.pack(fill=tk.X)

        # Create the current machine ID label
        current_id_label = ttk.Label(machine_id_frame, text="Current Machine ID:")
        current_id_label.pack(anchor=tk.W, pady=5)

        self.current_id_var = tk.StringVar()
        current_id_entry = ttk.Entry(machine_id_frame, textvariable=self.current_id_var, width=50, state="readonly")
        current_id_entry.pack(fill=tk.X, pady=5)

        # Create the backup checkbox
        self.backup_var = tk.BooleanVar(value=True)
        backup_check = ttk.Checkbutton(
            machine_id_frame,
            text="Create backup before resetting (recommended)",
            variable=self.backup_var
        )
        backup_check.pack(anchor=tk.W, pady=5)

        # Create the reset button
        reset_button = ttk.Button(
            machine_id_frame,
            text="Reset Machine ID",
            command=self.reset_machine_id
        )
        reset_button.pack(pady=5)

        # Initial refresh
        self.refresh_machine_id()

    def refresh_machine_id(self):
        """
        Refresh the machine ID information.
        """
        machine_id = get_current_machine_id()
        self.current_id_var.set(machine_id or "Not found")

    def reset_machine_id(self):
        """
        Reset the machine ID.
        """
        backup = self.backup_var.get()

        def task():
            success, _backup_id, old_id, new_id = reset_machine_id(backup=backup)

            if success:
                messagebox.showinfo("Success", f"Machine ID reset successfully!\nOld ID: {old_id or 'Not found'}\nNew ID: {new_id}")
                self.refresh_machine_id()
                self.refresh_info()
            else:
                messagebox.showerror("Error", "Failed to reset machine ID.")

        threading.Thread(target=task).start()

    def init_extensions_tab(self):
        """
        Initialize the Extensions tab.
        """
        # Create the extensions frame
        extensions_frame = ttk.Frame(self.extensions_tab, padding=10)
        extensions_frame.pack(fill=tk.BOTH, expand=True)

        # Create info section
        info_frame = ttk.LabelFrame(extensions_frame, text="About Extension Data")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = ttk.Label(
            info_frame,
            text="Extensions store data in VSCode's global storage, including:\n"
                 "• License information and activation status\n"
                 "• Usage telemetry and tracking data\n"
                 "• User preferences and settings\n\n"
                 "Resetting an extension will remove all its stored data, which can help with:\n"
                 "• Resolving extension issues\n"
                 "• Resetting trial periods\n"
                 "• Removing tracking information",
            wraplength=600,
            justify=tk.LEFT,
            padding=10
        )
        info_text.pack(fill=tk.X)

        # Create the extensions list frame
        list_frame = ttk.LabelFrame(extensions_frame, text="Extensions with Data")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create the extensions listbox
        self.extensions_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.extensions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.extensions_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.extensions_listbox.config(yscrollcommand=scrollbar.set)

        # Create the buttons frame
        buttons_frame = ttk.Frame(extensions_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        # Create the backup checkbox
        self.ext_backup_var = tk.BooleanVar(value=True)
        backup_check = ttk.Checkbutton(
            buttons_frame,
            text="Create backup before resetting (recommended)",
            variable=self.ext_backup_var
        )
        backup_check.pack(side=tk.LEFT, padx=5)

        # Create the refresh button
        refresh_button = ttk.Button(
            buttons_frame,
            text="Refresh List",
            command=self.refresh_extensions
        )
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Create the reset selected button
        reset_selected_button = ttk.Button(
            buttons_frame,
            text="Reset Selected",
            command=self.reset_selected_extensions
        )
        reset_selected_button.pack(side=tk.LEFT, padx=5)

        # Create the reset all button
        reset_all_button = ttk.Button(
            buttons_frame,
            text="Reset All Extensions",
            command=self.reset_all_extensions
        )
        reset_all_button.pack(side=tk.LEFT, padx=5)

        # Initial refresh
        self.refresh_extensions()

    def refresh_extensions(self):
        """
        Refresh the extensions list.
        """
        self.extensions_listbox.delete(0, tk.END)

        extension_data = list_extension_data()
        for ext_id in extension_data:
            self.extensions_listbox.insert(tk.END, ext_id)

    def reset_selected_extensions(self):
        """
        Reset the selected extensions.
        """
        selected_indices = self.extensions_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No extensions selected.")
            return

        selected_extensions = [self.extensions_listbox.get(i) for i in selected_indices]
        backup = self.ext_backup_var.get()

        if messagebox.askyesno("Confirm", f"Reset data for {len(selected_extensions)} selected extensions?"):
            def task():
                success_count = 0
                for ext_id in selected_extensions:
                    success, _ = reset_extension_data(ext_id, backup=backup)
                    if success:
                        success_count += 1

                messagebox.showinfo("Success", f"Reset data for {success_count}/{len(selected_extensions)} extensions.")
                self.refresh_extensions()
                self.refresh_info()

            threading.Thread(target=task).start()

    def reset_all_extensions(self):
        """
        Reset all extensions.
        """
        extension_data = list_extension_data()
        if not extension_data:
            messagebox.showinfo("Info", "No extension data found.")
            return

        backup = self.ext_backup_var.get()

        if messagebox.askyesno("Confirm", f"Reset data for all {len(extension_data)} extensions?"):
            def task():
                if backup:
                    # Create a backup of all data
                    backup_global_storage()

                success_count = 0
                for ext_id in extension_data:
                    success, _ = reset_extension_data(ext_id, backup=False)  # Already backed up
                    if success:
                        success_count += 1

                messagebox.showinfo("Success", f"Reset data for {success_count}/{len(extension_data)} extensions.")
                self.refresh_extensions()
                self.refresh_info()

            threading.Thread(target=task).start()

    def init_backup_restore_tab(self):
        """
        Initialize the Backup/Restore tab.
        """
        # Create the backup/restore frame
        backup_restore_frame = ttk.Frame(self.backup_restore_tab, padding=10)
        backup_restore_frame.pack(fill=tk.BOTH, expand=True)

        # Create info section
        info_frame = ttk.LabelFrame(backup_restore_frame, text="About Backups")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = ttk.Label(
            info_frame,
            text="Backups save the current state of VSCode configuration, including:\n"
                 "• Machine ID\n"
                 "• Global storage data\n"
                 "• State database\n"
                 "• Extension data (optional)\n\n"
                 "Creating backups before making changes allows you to restore VSCode to its previous state if needed.",
            wraplength=600,
            justify=tk.LEFT,
            padding=10
        )
        info_text.pack(fill=tk.X)

        # Create the backup frame
        backup_frame = ttk.LabelFrame(backup_restore_frame, text="Create Backup")
        backup_frame.pack(fill=tk.X, pady=5)

        # Create the include extensions checkbox
        self.include_extensions_var = tk.BooleanVar(value=True)
        include_extensions_check = ttk.Checkbutton(
            backup_frame,
            text="Include extension data (recommended, but increases backup size)",
            variable=self.include_extensions_var
        )
        include_extensions_check.pack(anchor=tk.W, pady=5)

        # Create the backup button
        backup_button = ttk.Button(
            backup_frame,
            text="Create New Backup",
            command=self.create_backup
        )
        backup_button.pack(pady=5)

        # Create the restore frame
        restore_frame = ttk.LabelFrame(backup_restore_frame, text="Restore from Backup")
        restore_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create the backups listbox
        self.backups_listbox = tk.Listbox(restore_frame)
        self.backups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(restore_frame, orient=tk.VERTICAL, command=self.backups_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backups_listbox.config(yscrollcommand=scrollbar.set)

        # Create the buttons frame
        buttons_frame = ttk.Frame(restore_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        # Create the refresh button
        refresh_button = ttk.Button(
            buttons_frame,
            text="Refresh List",
            command=self.refresh_backups
        )
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Create the restore button
        restore_button = ttk.Button(
            buttons_frame,
            text="Restore Selected Backup",
            command=self.restore_backup
        )
        restore_button.pack(side=tk.LEFT, padx=5)

        # Initial refresh
        self.refresh_backups()

    def refresh_backups(self):
        """
        Refresh the backups list.
        """
        self.backups_listbox.delete(0, tk.END)

        backups = list_backups()
        for backup_id in backups:
            self.backups_listbox.insert(tk.END, backup_id)

    def create_backup(self):
        """
        Create a backup.
        """
        include_extensions = self.include_extensions_var.get()

        def task():
            from ..core.utils import create_backup_id

            backup_id = create_backup_id()

            # Backup machine ID
            machine_id_path = get_current_machine_id()
            if machine_id_path:
                from ..core.utils import backup_file
                backup_file(machine_id_path, backup_id)

            # Backup global storage
            backup_global_storage(backup_id)

            # Backup state database
            backup_state_db(backup_id)

            # Backup extension data
            if include_extensions:
                extension_data = list_extension_data()
                for ext_id in extension_data:
                    backup_extension_data(ext_id, backup_id)

            messagebox.showinfo("Success", f"Backup created with ID: {backup_id}")
            self.refresh_backups()
            self.refresh_info()

        threading.Thread(target=task).start()

    def restore_backup(self):
        """
        Restore from a backup.
        """
        selected_indices = self.backups_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No backup selected.")
            return

        backup_id = self.backups_listbox.get(selected_indices[0])

        if messagebox.askyesno("Confirm", f"Restore from backup {backup_id}?"):
            def task():
                # Restore machine ID
                restore_machine_id(backup_id)

                # Restore state database
                restore_state_db(backup_id)

                # Restore extension data
                from ..core.utils import get_backup_dir
                backup_dir = get_backup_dir() / backup_id / "extensions"
                if backup_dir.exists():
                    extension_data = [d.name for d in backup_dir.iterdir() if d.is_dir()]
                    for ext_id in extension_data:
                        restore_extension_data(ext_id, backup_id)

                messagebox.showinfo("Success", f"Restore from backup {backup_id} completed.")
                self.refresh_machine_id()
                self.refresh_extensions()
                self.refresh_info()

            threading.Thread(target=task).start()

    def init_clean_all_tab(self):
        """
        Initialize the Clean All tab.
        """
        # Create the clean all frame
        clean_all_frame = ttk.Frame(self.clean_all_tab, padding=10)
        clean_all_frame.pack(fill=tk.BOTH, expand=True)

        # Create the warning label
        warning_label = ttk.Label(clean_all_frame, text="Warning: This will clean all VSCode tracking data!", foreground="red")
        warning_label.pack(pady=5)

        # Create the description text
        description_text = scrolledtext.ScrolledText(clean_all_frame, height=10, width=50)
        description_text.pack(fill=tk.BOTH, expand=True, pady=5)
        description_text.insert(tk.END, "This will clean all VSCode tracking data, including:\n\n")
        description_text.insert(tk.END, "- Machine ID\n")
        description_text.insert(tk.END, "- Extension data\n")
        description_text.insert(tk.END, "- Global storage\n")
        description_text.insert(tk.END, "- State database\n\n")

        if get_platform() == "windows":
            description_text.insert(tk.END, "- Registry entries\n")
            description_text.insert(tk.END, "- AppData\\Local files\n")
        elif get_platform() == "macos":
            description_text.insert(tk.END, "- Plist files\n")
            description_text.insert(tk.END, "- Application Support files\n")
        else:  # linux
            description_text.insert(tk.END, "- Config files\n")
            description_text.insert(tk.END, "- dconf settings\n")

        description_text.config(state=tk.DISABLED)

        # Create the backup checkbox
        self.clean_backup_var = tk.BooleanVar(value=True)
        backup_check = ttk.Checkbutton(clean_all_frame, text="Create backup before cleaning", variable=self.clean_backup_var)
        backup_check.pack(anchor=tk.W, pady=5)

        # Create the clean button
        clean_button = ttk.Button(clean_all_frame, text="Clean All", command=self.clean_all)
        clean_button.pack(pady=5)

    def clean_all(self):
        """
        Clean all VSCode tracking data.
        """
        backup = self.clean_backup_var.get()

        if messagebox.askyesno("Confirm", "Are you sure you want to clean all VSCode tracking data?"):
            def task():
                if backup:
                    from ..core.utils import create_backup_id
                    backup_id = create_backup_id()

                    # Backup machine ID
                    machine_id_path = get_current_machine_id()
                    if machine_id_path:
                        from ..core.utils import backup_file
                        backup_file(machine_id_path, backup_id)

                    # Backup global storage
                    backup_global_storage(backup_id)

                    # Backup state database
                    backup_state_db(backup_id)

                # Reset machine ID
                reset_machine_id(backup=False)  # Already backed up

                # Clean global storage
                clean_global_storage(backup=False)  # Already backed up

                # Reset state database
                reset_state_db(backup=False)  # Already backed up

                # Clean storage.json
                clean_storage_json()

                # Platform-specific cleaning
                if get_platform() == "windows":
                    clean_vscode_registry()
                    clean_appdata_local()
                elif get_platform() == "macos":
                    clean_vscode_plist()
                    clean_application_support()
                else:  # linux
                    clean_vscode_config()
                    clean_dconf_settings()

                messagebox.showinfo("Success", "Cleaning completed.")
                self.refresh_machine_id()
                self.refresh_extensions()
                self.refresh_backups()
                self.refresh_info()

            threading.Thread(target=task).start()

def main():
    """
    Entry point for the GUI.
    """
    root = tk.Tk()
    # Create the application instance and keep a reference to prevent garbage collection
    _app = VSCodeResetterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
