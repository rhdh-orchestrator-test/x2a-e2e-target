# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

[This repository contains a mix of Ansible playbooks and Chef InSpec tests. The migration will focus on standardizing the Ansible components and integrating or replacing the Chef InSpec testing framework. The estimated timeline is 1-2 weeks for a complete migration.]

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

After thorough examination using file_search for patterns "**/recipes/default.rb", "**/manifests/init.pp", and "**/*.psd1", no traditional Chef cookbooks, Puppet modules, or PowerShell modules were found in this repository.

The repository primarily contains:
1. Ansible playbooks in the chef-and-ansible directory
2. Chef InSpec tests in the chef-and-ansible/tests directory
3. Shell scripts for Chef Automate and Chef Infra Server deployment in the setup-automate directory

**CRITICAL PATH VERIFICATION:**
All paths listed below have been verified to exist using the `list_directory` tool.

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache web server with HTTPS support
  - Purpose: Deploys a secure web server with self-signed certificates
  - Migration considerations: Convert to Ansible role with proper variable parameterization

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL vulnerabilities
  - Purpose: Security hardening for Apache SSL configuration
  - Migration considerations: Integrate into a comprehensive security hardening role

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration
  - Purpose: Test orchestration for Ansible playbooks with InSpec verification
  - Migration considerations: Replace with Ansible Molecule

- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test
  - Purpose: Verifies HTTPS configuration and security
  - Migration considerations: Convert to Ansible Molecule tests with Testinfra or maintain InSpec integration

- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test
  - Purpose: Verifies SSH security compliance
  - Migration considerations: Convert to Ansible Molecule tests with Testinfra or maintain InSpec integration

- `setup-automate/deploy-automate.sh`: Shell script
  - Purpose: Deploys Chef Automate and Chef Infra Server
  - Migration considerations: Convert to Ansible playbook

- `setup-automate/deploy-chef-server.sh`: Shell script
  - Purpose: Deploys Chef Infra Server
  - Migration considerations: Convert to Ansible playbook

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec (latest)**: Currently used for compliance testing
  - Replace with: Ansible Molecule with Testinfra for testing, or maintain InSpec integration with Ansible
  
- **Test Kitchen (latest)**: Used for test orchestration
  - Replace with: Ansible Molecule for test orchestration

- **Apache2 (2.4.41-4ubuntu3.10)**: Web server package
  - Replace with: Ansible apache2 role with version pinning

- **OpenSSL (latest)**: Used for certificate generation
  - Replace with: Ansible crypto modules

### Security Considerations
- **SSL/TLS Configuration**: The playbooks enforce TLS 1.2 and disable older protocols
  - Migration approach: Maintain the same security standards in Ansible roles
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening with equivalent controls
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated during playbook execution
  - Migration approach: Use Ansible Vault for storing credentials

### Technical Challenges
- **InSpec Test Integration**: The repository uses Chef InSpec for compliance testing
  - Mitigation strategy: Either maintain InSpec tests and call them from Ansible, or convert to Ansible Molecule tests
  
- **Self-signed Certificate Generation**: The playbook generates self-signed certificates
  - Mitigation strategy: Use Ansible's crypto modules which are more current

### Migration Order
1. Convert setup scripts to Ansible playbooks (low risk, high value)
2. Standardize existing Ansible playbooks into roles (moderate complexity)
3. Migrate testing framework from Test Kitchen to Molecule (moderate complexity)
4. Convert or integrate InSpec tests (moderate complexity)

### Assumptions
- The repository is primarily used for demonstration purposes rather than production deployment
- The InSpec tests are considered valuable and should be preserved in some form
- The self-signed certificates are acceptable for the use case
- The hardcoded credentials in setup scripts are for demonstration purposes
- The target environment is Ubuntu 20.04 as specified in the kitchen.yml file