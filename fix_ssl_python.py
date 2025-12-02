import ssl
import os

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Set certificate paths
os.environ['SSL_CERT_FILE'] = r'C:\Users\Hrapunzel\telegram_bot\cacert.pem'
os.environ['REQUESTS_CA_BUNDLE'] = r'C:\Users\Hrapunzel\telegram_bot\cacert.pem'

print("SSL fixed for this script")
