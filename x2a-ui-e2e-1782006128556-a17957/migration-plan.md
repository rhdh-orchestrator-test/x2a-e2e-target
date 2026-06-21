# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance checks

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Incorporate these checks into Ansible-native testing
  - Consider adding an Ansible role for SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module or integrate with tools like OpenSCAP

- **Chef Automate Functionality**: Replacing Chef Automate's compliance scanning and reporting capabilities.
  - Mitigation: Implement a combination of Ansible AWX/Tower with OpenSCAP or other compliance tools

- **Test Kitchen to Molecule**: Converting the testing workflow from Test Kitchen to Molecule.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor updates for best practices
2. **InSpec Tests**: Convert to Ansible-native testing or Molecule
3. **Chef Deployment Scripts**: Create Ansible playbooks to replace the bash scripts for deploying infrastructure

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use, based on the README content.
2. The InSpec tests are used to verify the Ansible playbook configurations and not as part of a larger compliance framework.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
4. The Apache configuration is basic and doesn't include complex customizations that might be challenging to migrate.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The target environment is Ubuntu 20.04, and the migration will maintain this target OS.
7. The self-signed certificates are for testing purposes, and a production environment would use proper CA-signed certificates.