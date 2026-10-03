import datetime
from lxml import etree
from signxml import XMLSigner

def generate_cap(identifier: str, sender: str, sent: str, status: str, msg_type: str, scope: str) -> bytes:
    nsmap = {None: "urn:oasis:names:tc:emergency:cap:1.2"}
    alert = etree.Element("alert", nsmap=nsmap)
    etree.SubElement(alert, "identifier").text = identifier
    etree.SubElement(alert, "sender").text = sender
    etree.SubElement(alert, "sent").text = sent
    etree.SubElement(alert, "status").text = status
    etree.SubElement(alert, "msgType").text = msg_type
    etree.SubElement(alert, "scope").text = scope
    return etree.tostring(alert)

def sign_cap(cap_xml: bytes, key_path: str, cert_path: str) -> bytes:
    with open(key_path, "rb") as kf:
        key = kf.read()
    with open(cert_path, "rb") as cf:
        cert = cf.read()
    
    root = etree.fromstring(cap_xml)
    signed_root = XMLSigner().sign(root, key=key, cert=cert)
    return etree.tostring(signed_root)

if __name__ == "__main__":
    xml = generate_cap("123", "sender@example.com", "2026-10-03T12:00:00Z", "Actual", "Alert", "Public")
    print(sign_cap(xml, "dev_key.pem", "dev_cert.pem"))
