# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which can be kept largely as-is) and moderate complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be kept as-is or integrated into Ansible content.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-compatible management solutions

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated Ansible content.
  - Migration approach: Keep the existing SSL configurations in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH security settings. Ensure these checks are implemented in the new testing framework.
  - Migration approach: Convert InSpec SSH tests to equivalent Ansible assertions or Molecule tests.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and test structures.
  - Mitigation strategy: Create a mapping of InSpec resources to Ansible modules/assertions and systematically convert each test.

- **Chef Server Deployment**: Replacing the Chef server deployment scripts with equivalent Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for infrastructure management that replace the functionality of Chef Automate/Infra Server.

### Migration Order

1. **website_https** and **poodle_fix** playbooks (low risk, already in Ansible)
2. **website_https_verify** and **ssh_profile** tests (moderate complexity, requires framework conversion)
3. **chef-server-deployment** and **automate-deployment** scripts (high complexity, requires architectural decisions)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies, not to maintain the hybrid approach currently demonstrated.
2. The InSpec tests are used for compliance validation and their functionality needs to be preserved in an Ansible-compatible way.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible automation for managing infrastructure.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The self-signed certificate approach is acceptable for the migrated solution rather than integrating with a certificate authority.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
7. The Test Kitchen setup is primarily for development/testing and not part of the production deployment process.