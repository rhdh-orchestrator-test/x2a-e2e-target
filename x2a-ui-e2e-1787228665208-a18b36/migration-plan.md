# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but the integration with Chef InSpec for compliance testing requires careful consideration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration should consider converting to Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible-compatible testing framework.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Options include:
  1. Continue using InSpec as a standalone tool called from Ansible
  2. Replace with Ansible-native testing using ansible-lint and custom modules
  3. Use alternative compliance tools like OSCAP with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. Migration must maintain these security settings.
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible implementation.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional tooling or custom modules.
  - Mitigation: Consider using ansible-test, testinfra, or maintaining InSpec as a separate tool called from Ansible.
  
- **Chef Automate/Server Deployment**: The current deployment uses bash scripts to install Chef components.
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment, or consider if these components are still needed after migration.

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure (low risk, high value)
2. **poodle_fix.yml** (Priority 1): Convert to Ansible role or include in the website_https role (low complexity)
3. **InSpec Tests** (Priority 2): Convert to Ansible-compatible testing framework (moderate complexity)
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles or evaluate if still needed (moderate complexity)

### Assumptions

1. The repository is primarily used for demonstration purposes as indicated by the main README.md ("working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams").
2. The InSpec tests are an integral part of the workflow and need to be preserved in some form.
3. The Chef Automate and Chef Infra Server deployment scripts may not be needed after migration to Ansible, but their functionality should be documented.
4. The current implementation uses Vagrant for local testing, which can be maintained or replaced with other virtualization technologies.
5. No external inventory or variable files were found, suggesting that the playbooks are self-contained or use default values.
6. No complex role structure or dependencies exist in the current Ansible implementation.
7. The target environment is Ubuntu 20.04, but the solution should be flexible enough to work with other distributions if needed.