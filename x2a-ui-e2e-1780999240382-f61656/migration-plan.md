# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or included as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for playbook validation
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2
- **SSH Security Controls**: The SSH root login compliance check needs to be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained in the migrated solution
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets identified in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the equivalent assertions and test structures
  - Mitigation: Use Molecule's verifier plugins or Testinfra which has similar capabilities to InSpec
  
- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated in the Ansible solution
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for compliance reporting or use community modules for generating compliance reports

- **Chef Automate Functionality**: The Chef Automate deployment provides compliance and infrastructure visibility that needs equivalent functionality in Ansible
  - Mitigation: Consider Ansible Tower/AWX as a replacement for Chef Automate's dashboard and reporting capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and only need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as they need to be completely rewritten as Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation with Ansible and InSpec, not for production deployment
2. The InSpec tests are used for validation only and not for remediation
3. The deployment scripts are examples and may contain simplified configurations not suitable for production
4. The hardcoded credentials in deployment scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There is no external dependency on Chef Automate for compliance reporting in the current workflow
7. The migration will maintain the same level of security controls and compliance checks
8. No custom InSpec resources are being used that would require special handling