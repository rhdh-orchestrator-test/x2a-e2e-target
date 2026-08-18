# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance validation. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec tests need to be converted to Ansible-native solutions. Estimated timeline for migration is 1-2 weeks, with most of the effort focused on replacing InSpec tests with equivalent Ansible functionality.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file for the web server example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Convert InSpec tests to Ansible assert modules or use Molecule for testing
  - For continuous compliance: Consider integrating with AWX/Tower scheduled jobs

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set up equivalent functionality using AWX/Tower for orchestration
  - Configure necessary compliance reporting tools

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache
  - Migration approach: Maintain the same SSL hardening in Ansible playbooks
  - Consider using ansible-vault for storing sensitive certificate information

- **SSH Hardening**: InSpec tests verify SSH security configuration
  - Migration approach: Create equivalent Ansible tasks to enforce and verify SSH security settings
  - Use ansible.posix.sshd module for configuration management

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to ansible-vault
  - SSL certificates should be managed securely, possibly with ansible-vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert module combined with command/shell modules to perform equivalent checks
  - Consider implementing custom Ansible modules for complex compliance checks

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting
  - Mitigation: Integrate with AWX/Tower for reporting or consider additional tools like OpenSCAP

- **Test Kitchen to Molecule**: Converting test infrastructure
  - Mitigation: Molecule provides similar functionality and can be configured to work with existing Vagrant drivers

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Convert any inline templates to separate template files
   - Implement proper variable management

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Medium complexity
   - Convert bash scripts to Ansible playbooks
   - Replace hardcoded variables with proper variable management
   - Implement idempotent deployment logic

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Higher complexity
   - Convert to Ansible assertion tasks
   - Implement equivalent compliance checks
   - Set up reporting mechanism

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a complete production environment
2. The InSpec tests are used for validation rather than continuous compliance monitoring
3. The deployment scripts are examples and may need customization for production use
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex data structures or custom facts are being used
6. The target environment will continue to be Ubuntu 20.04 or similar
7. The migration will maintain the same level of security validation as the original
8. No CI/CD pipeline integration is required beyond what might be implied by Test Kitchen