# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily focused on examples rather than production infrastructure code. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH security checks in ssh_profile.rb need to be implemented in Ansible
  - Use ansible-lint security rules to enforce SSH best practices
  - Create equivalent Ansible assertions or Molecule tests to verify SSH configuration

- **Vault/secrets management**: 
  - No encrypted secrets were detected in the repository
  - Plain text passwords are used in the deployment scripts (userpassword='password')
  - Migration should implement Ansible Vault for securing these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule's verifier plugins or Ansible's assert module to recreate test functionality
  - Consider using ansible-test for integration testing

- **Deployment Scripts**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible roles
  - Mitigation: Create Ansible roles that perform the same server setup and configuration
  - Use Ansible variables instead of Bash variables for configuration

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
   - Review and optimize according to Ansible best practices
   - Add documentation and comments

2. **poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize according to Ansible best practices
   - Add documentation and comments

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Molecule tests or Ansible assertions
   - Convert ssh_profile.rb to Ansible security checks

4. **Deployment Scripts** (high complexity)
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible roles
   - Implement Ansible Vault for securing credentials

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The InSpec tests are used for verification after Ansible playbook execution
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely with Ansible
4. No external dependencies or modules are required beyond what's visible in the repository
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No complex data structures or custom facts are used in the existing code
7. No external inventory or host management system is in use
8. The migration will maintain the same level of security compliance checking
9. No CI/CD pipeline integration is required beyond what Test Kitchen provides