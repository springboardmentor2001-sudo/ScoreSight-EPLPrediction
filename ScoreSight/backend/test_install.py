try:
    import flask
    print("✓ Flask installed")
except ImportError:
    print("✗ Flask missing")

try:
    import flask_cors
    print("✓ Flask-CORS installed")
except ImportError:
    print("✗ Flask-CORS missing")

try:
    import numpy
    print(f"✓ NumPy {numpy.__version__} installed")
except ImportError:
    print("✗ NumPy missing")

try:
    import pandas
    print(f"✓ Pandas {pandas.__version__} installed")
except ImportError:
    print("✗ Pandas missing")

try:
    import google.generativeai
    print("✓ Google Generative AI installed")
except ImportError:
    print("✗ Google Generative AI missing")

try:
    import dotenv
    print("✓ python-dotenv installed")
except ImportError:
    print("✗ python-dotenv missing")