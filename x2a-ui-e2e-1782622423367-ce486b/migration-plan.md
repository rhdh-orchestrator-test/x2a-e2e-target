# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible equivalents.

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be converting the InSpec compliance tests to Ansible-compatible solutions while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with an Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page. Can be preserved as-is or converted to a template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module and assert module to verify HTTP responses
  - For SSL protocol verification: Use Ansible's community.crypto collection
  - For ssh_profile.rb: Use Ansible's lineinfile or template module with assert for validation

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions from the InSpec test
  - Convert the InSpec control to an Ansible task that ensures PermitRootLogin is not set to 'yes'

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible requires careful mapping of test assertions to Ansible modules
  - Solution: Use Ansible's assert module combined with command/shell modules to run verification commands

- **Compliance Reporting**: InSpec provides structured compliance reporting that needs to be replicated in Ansible
  - Solution: Consider using ansible-lint with custom rules or integrating with tools like OpenSCAP

- **Chef Automate Replacement**: Replacing Chef Automate functionality requires an alternative compliance dashboard
  - Solution: Consider AWX/Tower for orchestration and reporting, or integrate with tools like Prometheus/Grafana for monitoring

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible tasks using assert module
3. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible roles for setting up alternative compliance solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes.
3. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
4. The self-signed certificates are for testing purposes only and would be replaced with proper certificates in production.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure alternatives.
6. The compliance requirements specified in the InSpec tests (especially the SSH profile with its security tags) must be maintained in the Ansible migration.
7. The migration will need to provide an alternative to Chef Automate for compliance reporting and visualization.