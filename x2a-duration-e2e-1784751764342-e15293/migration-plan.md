# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing files and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The primary challenge will be replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for testing playbooks
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  - Install and configure equivalent Ansible automation platform (AAP)
  - Or maintain Chef server deployment if it's still required in the environment

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already addressed in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Implement automatic certificate renewal if moving to production

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Incorporate SSH hardening directly into Ansible playbooks
  - Maintain compliance with security standards referenced (SRG-OS-000112, etc.)

- **Vault/secrets management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of assertions and controls.
  - Mitigation: Use Ansible's assert module for functional tests and consider ansible-lint for static analysis.

- **Compliance Reporting**: If Chef InSpec is being used for compliance reporting, an alternative solution will be needed.
  - Mitigation: Consider using Ansible's built-in reporting or integrate with tools like OpenSCAP.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor updates for best practices.
2. **Testing Framework**: Replace Test Kitchen with Ansible Molecule.
3. **InSpec Tests**: Convert to Ansible assertions or Molecule verifiers.
4. **Deployment Scripts**: Replace Chef Automate/Server deployment scripts with Ansible playbooks.

### Assumptions

1. The repository is primarily educational/demonstrative and not used in production.
2. There are no external dependencies on Chef InSpec for compliance reporting.
3. The goal is to standardize on Ansible rather than maintain a hybrid approach.
4. The SSH and HTTPS configurations are representative examples and not comprehensive security policies.
5. The Chef Automate/Server deployment scripts are examples and not critical infrastructure components.
6. No external data sources or inventory systems are integrated with these examples.
7. No CI/CD pipelines are dependent on the current structure of tests and playbooks.