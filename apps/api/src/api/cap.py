
import datetime
from lxml import etree
import hashlib
import json
import os

# Global state for requirements
KILL_SWITCH_ACTIVE = False
AUDIT_LOG = []
ALERTS_DB = {}

def add_audit(action, user, alert_id, data):
    prev_hash = AUDIT_LOG[-1]["hash"] if AUDIT_LOG else "0"
    record = {"action": action, "user": user, "alert_id": alert_id, "data": data, "prev_hash": prev_hash}
    rec_str = json.dumps(record, sort_keys=True)
    record["hash"] = hashlib.sha256(rec_str.encode()).hexdigest()
    AUDIT_LOG.append(record)

def verify_audit():
    for i, record in enumerate(AUDIT_LOG):
        expected_prev = AUDIT_LOG[i-1]["hash"] if i > 0 else "0"
        if record["prev_hash"] != expected_prev: return False
        rec_copy = dict(record)
        del rec_copy["hash"]
        if hashlib.sha256(json.dumps(rec_copy, sort_keys=True).encode()).hexdigest() != record["hash"]: return False
    return True

# Load CAP 1.2 XSD from docs
XSD_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "docs", "api", "schemas", "CAP-v1.2-os.xsd")
with open(XSD_PATH, "rb") as f:
    CAP_XSD = f.read()

def validate_cap(xml_bytes: bytes) -> bool:
    schema_root = etree.XML(CAP_XSD)
    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    try:
        etree.fromstring(xml_bytes, parser)
        return True
    except etree.XMLSyntaxError:
        return False

def generate_cap(identifier: str, sender: str, sent: str, status: str, msg_type: str, scope: str) -> bytes:
    nsmap = {None: "urn:oasis:names:tc:emergency:cap:1.2"}
    alert = etree.Element("{urn:oasis:names:tc:emergency:cap:1.2}alert", nsmap=nsmap)
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}identifier").text = identifier
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}sender").text = sender
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}sent").text = sent
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}status").text = status
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}msgType").text = msg_type
    etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}scope").text = scope
    
    info = etree.SubElement(alert, "{urn:oasis:names:tc:emergency:cap:1.2}info")
    etree.SubElement(info, "{urn:oasis:names:tc:emergency:cap:1.2}category").text = "Met"
    etree.SubElement(info, "{urn:oasis:names:tc:emergency:cap:1.2}event").text = "Severe Weather"
    etree.SubElement(info, "{urn:oasis:names:tc:emergency:cap:1.2}urgency").text = "Immediate"
    etree.SubElement(info, "{urn:oasis:names:tc:emergency:cap:1.2}severity").text = "Extreme"
    etree.SubElement(info, "{urn:oasis:names:tc:emergency:cap:1.2}certainty").text = "Observed"
    
    return etree.tostring(alert)

def dispatch_webhook(xml_bytes: bytes):
    # Dispatch only to a mock webhook, and say so.
    print("[MOCK WEBHOOK] Dispatching CAP message:")
    print(xml_bytes.decode('utf-8'))
    return {"status": "dispatched_to_mock"}
