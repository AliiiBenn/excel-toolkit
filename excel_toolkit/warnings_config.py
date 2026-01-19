"""Warning configuration for Excel Toolkit.

Suppresses non-critical library warnings for cleaner output.
"""

import warnings
import sys

# Suppress openpyxl UserWarnings about unsupported extensions
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Suppress specific openpyxl warnings by message pattern
warnings.filterwarnings('ignore', message='.*Slicer List.*extension is not supported.*')
warnings.filterwarnings('ignore', message='.*extension is not supported and will be removed.*')
warnings.filterwarnings('ignore', message='.*Unknown extension.*')

# Suppress pandas warnings about performance (optional)
warnings.filterwarnings('ignore', message='.*PerformanceWarning.*')

# Set up warning output to stderr instead of stdout
# This allows users to redirect warnings separately: 2>/dev/null
def show_warnings_as_errors():
    """Show all warnings as errors (for debugging)."""
    warnings.filterwarnings('error')


def setup_warnings(quiet: bool = False, verbose: bool = False):
    """Configure warning display based on verbosity settings.

    Args:
        quiet: Suppress all warnings
        verbose: Show all warnings
    """
    if quiet:
        # Suppress all warnings
        warnings.filterwarnings('ignore')
    elif verbose:
        # Show all warnings
        warnings.resetwarnings()
        warnings.filterwarnings('default')
    else:
        # Default: suppress non-critical library warnings
        # (already applied at module level above)
        pass
