# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible-based deployment methods.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities (POODLE) in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server deployment. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook/role storage
  - CI/CD pipeline integration for automated testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Migration approach: Convert to an Ansible role that applies the same security configurations

- **SSH Security**: The SSH security checks in the InSpec profile need to be preserved
  - Migration approach: Create Ansible tasks that implement the same checks using the assert module

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Create custom Ansible modules or use the assert module with carefully crafted conditions

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Integrate with tools like OpenSCAP or AWX/Tower's reporting capabilities

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible infrastructure
  - Mitigation: Document AWX/Tower setup procedures or create playbooks for deploying AWX/Tower

### Migration Order

1. **website_https_verify** (low risk, high value) - Convert InSpec tests to Ansible assertions
2. **ssh_profile** (low risk, high value) - Convert InSpec SSH tests to Ansible assertions
3. **chef-automate-deployment** and **chef-server-deployment** (moderate complexity) - Create Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be used as-is without modification
2. The primary goal is to replace Chef InSpec testing with Ansible-native solutions
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The security compliance requirements (like STIG compliance in the SSH profile) need to be maintained in the Ansible solution
7. No custom InSpec resources are being used that would require special handling
8. The migration does not need to address scaling concerns as the repository appears to be for demonstration/example purposes