"""
VulRem - Vulnerability Remediaton
(c) 2020 by Mikhail Kondrashin mkondrashin@gmail.com
Code is distributed under Apache License 2.0 http://www.apache.org/licenses/

dsm.py - Deep Security SDK wrapper for VulRem required features
"""
import sys, warnings

import deepsecurity as ds


class DSM:
    def __init__(self, url, api_key, verify_ssl, api_version):
        self.configuration = ds.Configuration()
        self.configuration.host = url
        self.configuration.api_key['api-secret-key'] = api_key
        self.configuration.verify_ssl = verify_ssl
        self.api_version = api_version

    def get_ips_rules(self, cves):
        api_instance = ds.IntrusionPreventionRulesApi(
            ds.ApiClient(self.configuration)
        )
        api_response = api_instance.list_intrusion_prevention_rules(self.api_version)
        ids = []
        unfixed = set(cves)

        for rule in api_response.intrusion_prevention_rules:
            if rule.cve is None:
                continue
            for cve in rule.cve:
                if cve in cves:
                    ids.append(rule.id)
                    unfixed.discard(cve)
        return ids, unfixed

    def configure_policy(self, policy_id, rule_ids):
        api_instance = ds.PolicyIntrusionPreventionRuleAssignmentsRecommendationsApi(
            ds.ApiClient(self.configuration))
        intrusion_prevention_rule_ids = ds.RuleIDs()
        intrusion_prevention_rule_ids.rule_ids = rule_ids

        api_response = api_instance.add_intrusion_prevention_rule_ids_to_policy(
            policy_id,
            self.api_version,
            intrusion_prevention_rule_ids=intrusion_prevention_rule_ids,
            overrides=False
        )
        return api_response

    def describe_policy(self, policy_id, description):
        if not sys.warnoptions:
            warnings.simplefilter("ignore")
        api_instance = ds.PoliciesApi(ds.ApiClient(self.configuration))

        policy = ds.Policy()
        description = description[:1998] + (description[1998:] and '..')
        policy.description = description
        api_response = api_instance.modify_policy(policy_id,
                                                  policy,
                                                  self.api_version,
                                                  overrides=False)
        return api_response

