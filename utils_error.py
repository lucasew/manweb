import sys
import traceback

def report_error(err: Exception, context: str = ""):
    """Centralized error reporting function."""
    if context:
        sys.stderr.write(f"[Error] {context}: {str(err)}\n")
    else:
        sys.stderr.write(f"[Error] {str(err)}\n")
    traceback.print_exc(file=sys.stderr)
