# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web applications. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be kept largely as-is) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Static HTML content for the web server. Migration consideration: Keep as-is, no changes needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: For compliance-specific testing, consider migrating to OpenSCAP with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Maintain the same SSL/TLS configuration parameters in the Ansible tasks

- **SSH Security**: The InSpec tests validate SSH security configurations according to STIG standards.
  - Migration approach: Create equivalent Ansible tasks to validate and enforce SSH security settings

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions is the primary challenge.
  - Mitigation strategy: Use Ansible's assert module for functional tests and consider OpenSCAP integration for compliance testing

- **Chef Automate Deployment**: The repository includes scripts for deploying Chef Automate, which won't be needed in an Ansible-only environment.
  - Mitigation strategy: Replace with Ansible AWX or Ansible Tower deployment if centralized management is required

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be kept largely as-is with minor adjustments to follow best practices
2. **Testing Framework**: Replace Test Kitchen with Molecule
3. **InSpec Tests**: Convert to Ansible-native testing solutions
4. **Deployment Scripts**: Replace Chef Automate/Server deployment scripts with Ansible AWX/Tower deployment if needed

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining or enhancing the security validation capabilities
2. The existing Ansible playbooks are working correctly and don't require significant refactoring
3. There is no dependency on Chef Automate for compliance reporting that needs to be replaced
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are acceptable for the use case, or will be replaced with proper CA-signed certificates
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution