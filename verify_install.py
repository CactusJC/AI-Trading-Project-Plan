import sys

try:
    print("Verifying lnmarkets installation...")
    import lnmarkets
    print("lnmarkets imported successfully.")

    print("\\nVerifying stable_baselines3 installation...")
    import stable_baselines3
    print("stable_baselines3 imported successfully.")

    print("\\nVerifying TA-Lib installation...")
    import talib
    print("TA-Lib imported successfully.")

    print("\\nAll key libraries imported successfully!")
    sys.exit(0)

except ImportError as e:
    print(f"\\nError: {e}", file=sys.stderr)
    print("Installation verification failed.", file=sys.stderr)
    sys.exit(1)
