import logging

def format_size(size):
    if size == 0:
        return "Unknown size"
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def log_operation(start_time, end_time, status, error_message=None, use_cuda=False, operation="conversion", format=None, resolution=None):
    duration = end_time - start_time
    method = "CUDA" if use_cuda else "CPU"
    if status == "success":
        logging.info(f"{operation.capitalize()} successful. Duration: {duration:.2f} seconds. Method: {method}. Format: {format}. Resolution: {resolution}p.")
    else:
        logging.error(f"{operation.capitalize()} failed. Duration: {duration:.2f} seconds. Method: {method}. Format: {format}. Resolution: {resolution}p. Error: {error_message}")
