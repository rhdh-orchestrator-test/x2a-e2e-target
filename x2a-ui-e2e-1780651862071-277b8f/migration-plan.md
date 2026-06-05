# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 WEEKS** due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache web server with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec profile that verifies HTTPS configuration, port status, and SSL/TLS protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration including root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate InSpec tests to Ansible Molecule with testinfra
  - Option 2: Use ansible-lint for static analysis and compliance
  - Option 3: Keep InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab/GitHub for source control and CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Create an Ansible role for Apache SSL hardening that applies the same configuration

- **SSH Security**: The SSH compliance tests check for root login restrictions
  - Approach: Create an Ansible role that applies SSH hardening based on the same compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password in plaintext
    - chef-server-deployment: 1 password in plaintext

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec compliance tests to Ansible-native testing frameworks
  - Mitigation: Consider using Ansible Molecule with testinfra for similar functionality, or keep InSpec as a standalone tool integrated into Ansible workflows

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities
  - Mitigation: Implement compliance reporting using Ansible Automation Platform or integrate with third-party compliance tools

- **Self-Signed Certificates**: Ensuring secure certificate management in the Ansible playbooks
  - Mitigation: Use Ansible's crypto modules consistently and securely manage certificate storage

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the HTTPS configuration role as a security hardening task

3. **InSpec Tests** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Implement chosen testing approach

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for compliance verification of infrastructure configured by Ansible
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There are no complex application dependencies beyond what's visible in the playbooks
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only