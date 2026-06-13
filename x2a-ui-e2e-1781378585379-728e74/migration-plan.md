# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of Ansible playbooks for configuring a web server with HTTPS support and Chef InSpec tests for verification. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file for the web server

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or molecule for testing
  - Alternative: Keep InSpec as a standalone tool and call it from Ansible using the command module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for module testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Preserve the same Apache configuration settings in the Ansible playbooks

- **SSH Security**: The InSpec profile checks for SSH root login being disabled
  - Migration approach: Implement equivalent checks using Ansible's assert module or maintain InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible's assert module with appropriate conditionals or maintain InSpec as a separate tool called from Ansible

- **Chef Automate Deployment**: Replacing Chef Automate with appropriate Ansible tooling
  - Mitigation: Evaluate if Chef Automate functionality is still needed; if so, consider alternatives like AWX/Tower or other compliance tools

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security hardening task

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or maintain as InSpec tests called from Ansible

4. **Chef Automate deployment scripts** (high complexity)
   - Determine if Chef Automate is still needed or can be replaced with Ansible Tower/AWX
   - Create Ansible playbooks to replace the bash scripts if Chef infrastructure is still required

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for compliance verification of infrastructure configured by Ansible
3. The Chef Automate and Chef Server deployment may be optional in the migrated solution if alternative compliance tooling is available
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. Vagrant will continue to be used for development/testing environments
6. No external data sources or complex integrations are present beyond what's visible in the repository
7. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling