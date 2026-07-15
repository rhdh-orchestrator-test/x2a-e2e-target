# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef infrastructure setup. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for web server deployment with HTTPS configuration
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-website-tests**:
    - Description: Compliance tests for website HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **inspec-ssh-profile**:
    - Description: Compliance tests for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing
- `README.md`: Documentation files explaining the repository purpose

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI, role-based access control, and job scheduling
  - Git repositories for playbook/role storage
  - Consider Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The current implementation configures Apache with SSL and disables vulnerable protocols. Migration should:
  - Maintain TLSv1.2 requirement
  - Consider upgrading to include TLSv1.3 support
  - Use Ansible's `openssl_*` modules consistently

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Include equivalent checks in Ansible
  - Consider using the `ansible.posix.sshd` module for SSH configuration
  - Maintain STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated during deployment
  - Recommend replacing with Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using community.general.assert module for test assertions

- **Chef Server Deployment**: The current scripts deploy Chef infrastructure which won't be needed post-migration.
  - Mitigation: Create equivalent Ansible playbooks for AWX/Tower deployment if needed
  - Document the transition process for teams currently using Chef

### Migration Order

1. **website-https module** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and variable parameterization

2. **poodle-fix module** (low risk, already in Ansible)
   - Integrate with website-https as a role or included task
   - Update to include additional security hardening

3. **InSpec tests** (medium complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (optional)
   - Replace with Ansible AWX/Tower deployment if needed
   - Document alternative approaches for teams

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The Chef deployment scripts are used for setting up test environments rather than production infrastructure.
5. No custom Chef cookbooks or resources are being used that would require complex migration.
6. The security requirements (STIG compliance, SSL configuration) must be maintained in the Ansible migration.
7. Test Kitchen is used primarily for development/testing and not for production deployment.