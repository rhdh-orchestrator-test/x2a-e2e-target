# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible playbooks.

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
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for advanced compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login check in ssh_profile.rb needs to be implemented in Ansible.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or another testing framework will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Chef Server Deployment**: Migrating the Chef Server deployment scripts to Ansible will require understanding of Chef Server architecture.
  - Mitigation: Create Ansible roles that replicate the Chef Server deployment process or consider containerized deployment alternatives.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Only need to be reviewed and potentially optimized.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks or consider if Chef Automate/Server is still needed in the new architecture.

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while preserving compliance testing capabilities.
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications.
3. The deployment scripts for Chef Automate and Chef Infra Server may be optional in the new architecture if Chef is being completely replaced.
4. Test Kitchen is used only for development/testing and not in production pipelines.
5. The hardcoded credentials in deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
7. The migration will maintain the same level of security compliance as the original implementation.