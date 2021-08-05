# Running this PowerShell (PS) script only sets the environment variables for the life of the script.
# To set them in your PS terminal session, do the following:
#    cat <path and name of this file> | Invoke-Expression
$Env:WHPA_CDP_CLIENT_GATEWAY_NATS_SERVER_URL = "127.0.0.1:4222"
$Env:WHPA_CDP_CLIENT_GATEWAY_HL7_MLLP_HOST = "127.0.0.1"
$Env:WHPA_CDP_CLIENT_GATEWAY_HL7_MLLP_PORT = "2575"
$Env:WHPA_CDP_CLIENT_GATEWAY_TIMEZONE = "America/New_York"
$Env:WHPA_CDP_CLIENT_GATEWAY_TENANT = "cloud1"