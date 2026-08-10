# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes setup scripts for Chef Automate and Chef Infra Server deployment.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server setup scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate_deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server configuration. Can be reused as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a complementary testing tool if its capabilities are needed

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Playbook testing with `--check` mode

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for enterprise orchestration
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains:
  - Proper SSL protocol settings (TLSv1.2 enforcement)
  - Self-signed certificate generation
  - Virtual host SSL configuration

- **SSH Security**: The InSpec profile checks for SSH root login restrictions. Ensure:
  - SSH hardening is maintained in the Ansible configuration
  - Compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in setup scripts

### Technical Challenges

- **Compliance Testing**: InSpec provides detailed compliance reporting that may be challenging to replicate with Ansible's built-in testing capabilities. Consider:
  - Using Ansible's assert module with detailed output
  - Integrating with external compliance tools
  - Maintaining InSpec as a complementary tool if necessary

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec. Migration will require:
  - Setting up Molecule or another testing framework
  - Ensuring test coverage is maintained

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can be directly reused in the new Ansible-only environment
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for infrastructure setup

### Assumptions

1. The primary goal is to move away from Chef components while maintaining or enhancing the compliance testing capabilities
2. The existing Ansible playbooks are working correctly and don't require significant modifications
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The security compliance requirements (STIG standards referenced in InSpec tests) must be maintained
6. The self-signed certificates are acceptable for the environment (not production)
7. The hardcoded credentials in setup scripts are for demonstration purposes only and will be properly secured in the migration