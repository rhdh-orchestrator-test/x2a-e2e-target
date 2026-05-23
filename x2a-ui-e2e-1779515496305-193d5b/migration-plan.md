# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Static HTML content for the web server. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or other compliance tools

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, ensuring only secure protocols (TLSv1.2) are enabled.
- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented and verified in the Ansible solution.
- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of assertions and controls.
  - Mitigation: Consider using a hybrid approach where Ansible handles configuration and a specialized tool handles compliance testing.

- **Chef Server Deployment**: Converting the Chef Server and Automate deployment scripts to Ansible requires understanding of the Chef infrastructure setup process.
  - Mitigation: Create dedicated Ansible roles for Chef infrastructure components, with clear documentation on the deployment process.

### Migration Order

1. **website_https.yml** (already in Ansible format, no migration needed)
2. **poodle_fix.yml** (already in Ansible format, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions or Molecule tests)
4. **ssh_profile.rb** (convert InSpec tests to Ansible assertions or Molecule tests)
5. **deploy-chef-server.sh** and **deploy-automate.sh** (convert to Ansible playbooks with proper variable management)

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or improving the compliance testing capabilities.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes.
3. The deployment scripts for Chef Server and Automate are intended to be migrated to Ansible, rather than kept as shell scripts.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There are no external dependencies or integrations not visible in the provided repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the final solution.