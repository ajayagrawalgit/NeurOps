import yaml
import os
import sys
import subprocess

def setup_credentials():
    """
    Ensures Google Application Default Credentials (ADC) are configured.
    Checks for local project credentials, then environment variables, 
    and offers to run setup if missing.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    local_creds = os.path.join(root_dir, "application_default_credentials.json")
    
    # 1. Check if already set in environment
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return

    # 2. Prefer local credentials if they exist (portable)
    if os.path.exists(local_creds):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds
        return

    # 3. Check default gcloud location (standard)
    default_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    if os.path.exists(default_path):
        return # SDK will find it automatically

    # 4. If missing, provide instructions or automate
    print("\n" + "!" * 60)
    print("⚠️  MISSING GOOGLE CLOUD CREDENTIALS")
    print("Pub/Sub and BigQuery require Application Default Credentials.")
    print("!" * 60 + "\n")

    if sys.stdin.isatty():
        choice = input("Would you like to run 'gcloud auth application-default login' now? (y/n): ")
        if choice.lower() == 'y':
            try:
                subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
                print("✅ Credentials configured.")
            except Exception as e:
                print(f"❌ Failed to run gcloud: {e}")
                sys.exit(1)
        else:
            print("Please run the following command manually:")
            print("  gcloud auth application-default login")
            sys.exit(1)
    else:
        print("Non-interactive terminal detected.")
        print("Please run the following command to set up credentials:")
        print("  gcloud auth application-default login")
        print("\nAlternatively, place your credentials JSON in the project root as:")
        print(f"  {local_creds}")
        sys.exit(1)

def load_configs():
    # Setup credentials before returning config so clients can be initialized immediately
    setup_credentials()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    if not os.path.exists(config_path):
        return {}
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config if config else {}
