# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance requirements

Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server that will need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2 in Apache configuration

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security requirements (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing the web server configuration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements
  - Deploy alternative compliance and automation tools (e.g., AWX/Ansible Tower)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables vulnerable protocols (SSLv3) and enforces TLSv1.2
  - Approach: Use Ansible's `lineinfile` or `template` modules to manage Apache SSL configuration

- **SSH Security Hardening**: Ensure SSH root login remains disabled
  - Approach: Use Ansible's `lineinfile` or `template` modules to manage SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in bash scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks will require careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible
  - Mitigation: Integrate with additional tools like Ansible Tower/AWX for reporting or maintain InSpec as a separate tool called from Ansible

- **Certificate Management**: The current solution generates self-signed certificates using Ansible's openssl modules
  - Mitigation: Ensure the Ansible playbooks continue to use these modules correctly or consider integrating with external certificate management solutions

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Simply review and optimize the existing Ansible playbook

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and potentially merge with the main website configuration playbook

3. **chef-automate-deployment** and **chef-server-deployment** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

4. **https-compliance-tests** and **ssh-security-compliance** (high complexity)
   - Convert InSpec tests to Ansible-native testing or integrate InSpec with Ansible workflow

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, replacing Chef InSpec for testing
2. The current setup uses Test Kitchen to orchestrate Ansible and InSpec, which will be replaced
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. Self-signed certificates are acceptable for the web server configuration
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migration
6. The SSH compliance profile is intended to be run against the same systems configured by the Ansible playbooks
7. There may be additional Chef components or dependencies not visible in the provided files
8. The migration will maintain the same level of security compliance checking currently provided by InSpec