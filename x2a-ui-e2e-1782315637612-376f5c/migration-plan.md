# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns between the configuration management (Ansible) and compliance testing (Chef InSpec) components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. No migration needed as it's a static content file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-testinfra for Python-based infrastructure testing as an alternative to InSpec

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible playbooks

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Tower/AWX for job execution and reporting
  - OpenSCAP for compliance scanning
  - Prometheus and Grafana for monitoring and reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider using Ansible's crypto modules or certbot for Let's Encrypt integration.
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This compliance check should be preserved in the Ansible testing framework.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the equivalent assertions and test structures.
  - Mitigation: Use Molecule's verifier plugins or pytest-testinfra which provide similar functionality to InSpec.

- **Compliance Reporting**: If compliance reporting is a requirement, replacing Chef Automate's compliance capabilities will require additional tooling.
  - Mitigation: Integrate with OpenSCAP or other compliance tools that can work with Ansible.

- **Test Kitchen Workflow**: Users familiar with Test Kitchen workflow will need to adapt to Molecule's workflow.
  - Mitigation: Provide documentation and examples of equivalent Molecule configurations.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and can be preserved as-is.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests or pytest-testinfra.
3. **Chef Automate Deployment Scripts**: Convert bash scripts to Ansible roles for deploying alternative compliance and automation tools.

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving the functionality of the Ansible playbooks.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require significant changes.
3. The repository is primarily used for demonstration/educational purposes rather than production, based on the README description.
4. The Chef Automate and Chef Server deployment scripts are included for reference but may not be central to the main functionality.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
7. The security compliance requirements represented in the InSpec tests need to be preserved in the migrated solution.