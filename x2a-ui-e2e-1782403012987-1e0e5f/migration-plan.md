# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for web server configuration. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. No migration considerations needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Ansible's built-in `verify` tasks
  - Option 3: Integrate with Molecule for testing
  - Option 4: Maintain InSpec as a complementary testing tool alongside Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative infrastructure management:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD or Jenkins for pipeline automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
  - Approach: Ensure TLSv1.2 remains the minimum protocol version in Apache configurations

- **Self-signed Certificates**: Current implementation uses self-signed certificates
  - Recommendation: Consider migrating to Let's Encrypt or other trusted certificate authority

- **SSH Security**: The InSpec profile checks for SSH root login restrictions
  - Approach: Ensure SSH hardening is maintained in Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting Ruby-based InSpec tests to Ansible verification
  - Mitigation: Create equivalent verification tasks using Ansible's assert module or maintain InSpec as a complementary tool

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement Ansible Automation Platform with compliance scanning or integrate with third-party compliance tools

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires replacement with Ansible Automation Platform deployment)

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation of the Ansible playbook results
3. There are no external dependencies or integrations not visible in the repository
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There is no complex state management or data persistence requirements
7. The repository does not include actual Chef cookbooks that need migration
8. The deployment scripts are standalone and not part of a larger automation framework
9. The SSL configuration is primarily for demonstration and not production-grade security
10. There are no specific performance requirements for the deployed applications