import pytest
from apps.api.src.api.cap import validate_cap

def test_oasis_example_cap_valid():
    # Example from OASIS CAP 1.2 spec
    valid_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>43b080713727</identifier>
  <sender>hsas@dhs.gov</sender>
  <sent>2003-04-02T14:39:01-05:00</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Security</category>
    <event>Homeland Security Advisory System Update</event>
    <urgency>Immediate</urgency>
    <severity>Severe</severity>
    <certainty>Likely</certainty>
    <senderName>U.S. Government, Department of Homeland Security</senderName>
    <headline>Homeland Security Sets Threat Rating to High</headline>
    <description>The Department of Homeland Security has elevated the Homeland Security Advisory System threat level to HIGH (Orange).</description>
  </info>
</alert>'''
    # Note: Our cap validator might require strict schema conformance which this example should pass.
    # If not, the test will correctly flag schema mismatches.
    assert validate_cap(valid_xml) == True

def test_invalid_cap_fails():
    invalid_xml = b'''<?xml version="1.0" encoding="UTF-8"?><alert><invalid>element</invalid></alert>'''
    assert validate_cap(invalid_xml) == False
