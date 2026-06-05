# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platforms

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login verification must be maintained in the new testing framework
- **Self-signed Certificates**: The process for generating self-signed certificates should be preserved or improved
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible's testing capabilities may require additional modules or custom scripts
  - Mitigation: Use Ansible's assert module combined with command/shell modules to replicate InSpec functionality
  
- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for compliance reporting or use community modules

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires understanding of Chef server architecture
  - Mitigation: Create Ansible roles that replicate the Chef server deployment process or consider alternative configuration management approaches

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires creating equivalent Ansible roles

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The InSpec tests are currently used for compliance validation and their functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure which may be replaced entirely with Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. No external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
7. The repository is primarily for demonstration/educational purposes as indicated by the README.md
8. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling