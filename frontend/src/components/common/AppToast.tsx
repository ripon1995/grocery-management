import { toast, type ToastOptions } from "react-toastify";

export class AppToast {
  // Shared base configuration for all toasts
  private static defaultOptions: ToastOptions = {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  };

  /**
   * Displays a Success Toast (Green by default)
   */
  static success(message: string, options?: ToastOptions): void {
    toast.success(message, {
      ...this.defaultOptions,
      ...options,
      // Optional: Override background color explicitly if needed
      // style: { backgroundColor: "#10B981", color: "#FFFFFF" },
    });
  }

  /**
   * Displays an Error Toast (Red by default)
   */
  static error(message: string, options?: ToastOptions): void {
    toast.error(message, {
      ...this.defaultOptions,
      ...options,
      // Optional: Override background color explicitly if needed
      // style: { backgroundColor: "#EF4444", color: "#FFFFFF" },
    });
  }

  /**
   * Custom helper where you pass any background color explicitly
   */
  static custom(message: string, isError: boolean = false): void {
    toast(message, {
      ...this.defaultOptions,
      style: {
        backgroundColor: isError ? "#dc2626" : "#16a34a", // Red for error, Green for success
        color: "#ffffff",
      },
    });
  }
}