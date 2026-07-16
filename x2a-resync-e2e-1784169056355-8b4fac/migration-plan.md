# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and converting Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https-verification**:
    - Description: InSpec tests for verifying HTTPS website configuration, including port listening, content verification, and SSL/TLS protocol checks
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content testing, SSL/TLS protocol validation

- **ssh-security-profile**:
    - Description: InSpec compliance profile for SSH security configuration, focusing on root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks, CCI compliance mapping

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `website_https.yml`: Ansible playbook for configuring HTTPS website - already in Ansible format, no migration needed
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability - already in Ansible format, no migration needed
- `index.html`: Sample HTML file used by the website playbook - no migration needed

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more advanced testing

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule (recommended for Ansible role testing)
  - Option 2: Ansible Tower/AWX for workflow testing

- **Chef Server/Automate**: Replace with Ansible automation platform:
  - Option 1: Ansible Tower/AWX
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSH Security Profile**: The SSH security profile (ssh_profile.rb) needs to be migrated to Ansible security scanning:
  - Consider using ansible-lint with custom security rules
  - Alternatively, use OpenSCAP with Ansible integration

- **SSL/TLS Configuration**: The SSL/TLS verification tests need to be migrated:
  - Use Ansible's uri module with appropriate SSL verification options
  - Consider integrating with external tools like testssl.sh via Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely using Ansible Vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach:
  - Challenge: InSpec's resource-based testing model doesn't directly map to Ansible
  - Mitigation: Use Ansible assert module combined with command/shell modules to achieve similar functionality

- **Compliance Reporting**: Replacing InSpec's compliance reporting capabilities:
  - Challenge: InSpec provides rich compliance reporting that isn't natively available in Ansible
  - Mitigation: Consider integrating with OpenSCAP or maintaining a hybrid approach where Ansible runs InSpec

- **Chef Server Deployment**: Converting Chef server deployment to Ansible:
  - Challenge: The deployment scripts contain Chef-specific commands and configurations
  - Mitigation: Research Ansible roles for Chef server deployment or create custom roles based on the installation steps in the scripts

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, no migration needed
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles/playbooks
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Ansible-native testing framework

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts are designed to work in both on-premises and cloud environments.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
4. The repository is primarily educational/demonstrative rather than production-ready code.
5. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already working correctly and don't need modification beyond potential security improvements.
6. The Chef InSpec tests are currently being used to validate the configurations applied by the Ansible playbooks.
7. There are no external dependencies or integrations beyond what's explicitly mentioned in the repository.