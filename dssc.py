"""
VulRem - Vulnerability Remediaton
(c) 2020 by Mikhail Kondrashin  mkondrashin@gmail.com
Code is distributed under Apache License 2.0 http://www.apache.org/licenses/

dssc.py: provides list_vulnerabilities function using Deep Security Smart Check SDK
"""
from smartcheck import Smartcheck


def list_vulnerabilities(smartcheck_host,
                         insecure_skip_tls_verify,
                         smartcheck_user,
                         smartcheck_password):
    """

    :param smartcheck_host: URL of Smart Check Web Interface
    :param insecure_skip_tls_verify: Ignore invalid certificates
    :param smartcheck_user: Smart Check console username
    :param smartcheck_password: Smart Check console user password
    :return: list of all CVEs for all images for all registries configured in DSSC
    """
    skip = " (skip verify TLS)" if insecure_skip_tls_verify else ""
    print(f'Connect to {smartcheck_host} using username {smartcheck_user}{skip}')
    with Smartcheck(
            base=smartcheck_host,
            verify=not insecure_skip_tls_verify,
            user=smartcheck_user,
            password=smartcheck_password
    ) as session:
        cves = set()
        for registry in session.list_registries():
            #print(f'Registry: {registry}')
            print(f'Registry: {registry["name"]} ({registry["host"]}): {registry["description"]}')
            for image in session.list_images(registry['id']):
                print(f'Image: {image["repository"]}:{image["tag"]}')
                scan = session.last_scan(image)
                print(f'Scan: {scan["details"]["completed"]}')
                for package in session.list_vulnerable_packages(scan):
                    for vulnerability in package['vulnerabilities']:
                        if 'fixed' in vulnerability:
                            continue
                        if 'override' in vulnerability:
                            continue
                        cves.add(vulnerability['name'])
        return cves

