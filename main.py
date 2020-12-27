"""
VulRem - Vulnerability Remediaton
(c) 2020 by Mikhail Kondrashin  mkondrashin@gmail.com
Code is distributed under Apache License 2.0 http://www.apache.org/licenses/

main.py - Entry point script
"""
import os
import sys
import time
import socket

import version
import dssc
import dsm


def get_sc_host():
    frontend = socket.gethostbyname('proxy')
    return f"https://{frontend}:443"


def environ(name, default = None):
    value = os.environ.get(name, None)
    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f'{name} environment variable is missing')
    return value


def policy_description(unfixed):
    l = sorted(list(unfixed))
    list_of_cves = "\n".join(l)
    text = f"""Policy configured by Vulnerability Remediation (VulRem {version.version}) on {time.asctime()} 
Following vulnerabilities are not covered by IPS rules of this policy:
{list_of_cves}
"""
    return text


def remediate_vulnerabilities():
    pass


def main():
    sc_url = environ('SMARTCHECK_URL', True)
    if sc_url is True:
        sc_url = get_sc_host()

    sc_skip_tls_verify = environ('SMARTCHECK_SKIP_TLS_VERIFY', 'False') != 'False'
    sc_user = environ('SMARTCHECK_USERNAME', 'administrator')
    sc_password = environ('SMARTCHECK_PASSWORD')
    ds_url = environ('DEEPSECURITY_URL')
    ds_skip_tls_verify = environ('DEEPSECURITY_SKIP_TLS_VERIFY', 'False') != 'False'
    ds_api_key = environ('DEEPSECURITY_API_KEY')
    ds_policy_id = environ('DEEPSECURITY_POLICY_ID')

    print(f"VulRem {version.version} started")
    print(f"SMARTCHECK_URL: {sc_url}")
    print(f"SMARTCHECK_SKIP_TLS_VERIFY: {sc_skip_tls_verify}")
    print(f"SMARTCHECK_USERNAME: {sc_user}")
    print(f"SMARTCHECK_PASSWORD: ********")
    print(f"DEEPSECURITY_API_KEY: {ds_api_key[:3]}...{ds_api_key[-3:]}")
    print(f"DEEPSECURITY_SKIP_TLS_VERIFY: {ds_skip_tls_verify}")
    print(f"DEEPSECURITY_POLICY_ID: {ds_policy_id}")
    cves = dssc.list_vulnerabilities(sc_url,
                                     sc_skip_tls_verify,
                                     sc_user,
                                     sc_password
                                    )
    print(f"Found {len(cves)} vulnerabilities")
    ds = dsm.DSM(
        url=ds_url,
        api_key=ds_api_key,
        verify_ssl=not ds_skip_tls_verify,
        api_version='v1'
    )

    rule_ids, unfixed = ds.get_ips_rules(cves)
    print(f"rules: {len(rule_ids)}, unfixed: {len(unfixed)}")
    ds.configure_policy(policy_id=ds_policy_id, rule_ids=rule_ids)
    description = policy_description(unfixed)
    ds.describe_policy(policy_id=ds_policy_id, description=description)
    print("Policy update finished")
    return 0


if __name__ == '__main__':
    sys.exit(main())
