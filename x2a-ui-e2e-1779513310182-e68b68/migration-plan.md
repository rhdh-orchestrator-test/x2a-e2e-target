# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope of Chef components and the existing Ansible infrastructure.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Continue using InSpec but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that configure:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD with Ansible for CI/CD pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 4 credentials (username, password, organization name, hostname)
    - chef-server-deployment: 4 credentials (username, password, organization name, hostname)

### Technical Challenges

- **Test Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks requires understanding the compliance requirements and implementing equivalent checks
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec
  
- **Compliance Validation**: Ensuring that the migrated tests provide the same level of compliance validation
  - Mitigation: Create a test matrix mapping InSpec controls to new test framework controls

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with Ansible-compatible alternatives
  - Mitigation: Evaluate AWX/Tower compliance reporting capabilities or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity to replace with Ansible automation

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation with Ansible and InSpec, not to provide production-ready infrastructure
2. The InSpec tests are used for validation only and do not contain remediation logic
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no external dependencies on Chef Infra Server or Chef Automate beyond what's in the deployment scripts
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The repository is intended for educational/demonstration purposes as indicated by the main README.md
7. The migration should maintain the same level of security validation provided by the InSpec tests
8. No custom InSpec resources are being used that would require special handling