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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment based on setup-automate scripts

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider Ansible's built-in test module

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solutions

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **SSH Security**: The ssh_profile.rb InSpec test checks for SSH root login being disabled. This security check should be preserved in the Ansible migration.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Evaluate integration with compliance tools like OpenSCAP or custom reporting solutions.

- **Chef Server Replacement**: The Chef Server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for Chef Server/Automate.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality with Ansible equivalents.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and follow best practices.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The migration will preserve all existing functionality, including compliance checks and security configurations.
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution.
6. The Test Kitchen configuration is used primarily for testing and demonstration, not for production deployments.
7. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
8. The migration will need to maintain compatibility with existing infrastructure or provide a clear migration path.