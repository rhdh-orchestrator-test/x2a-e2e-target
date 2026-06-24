# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use community.general.inspec module to continue using InSpec tests from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 enforcement and disabled SSL3 as verified in the InSpec tests
- **SSH Hardening**: The SSH security controls tested by the InSpec profile must be implemented in the Ansible playbooks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to an Ansible-compatible testing framework will require careful mapping of test assertions
  - Mitigation: Use Molecule with Testinfra which provides similar testing capabilities
  
- **Chef Server Functionality**: Replacing Chef Server's functionality with Ansible-native solutions
  - Mitigation: Use Ansible AWX/Tower for web UI, role-based access control, and job scheduling

- **Compliance Reporting**: Maintaining compliance reporting capabilities without Chef Automate
  - Mitigation: Integrate with compliance tools like OpenSCAP or use Ansible's built-in reporting with custom dashboards

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule/Testinfra tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure setup
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The InSpec tests are the main value to preserve, as they contain the compliance requirements
3. The existing Ansible playbooks can be used with minimal modifications
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment and not critical production infrastructure
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data handling or state management is required
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
8. The migration will maintain the same level of security controls and compliance checks