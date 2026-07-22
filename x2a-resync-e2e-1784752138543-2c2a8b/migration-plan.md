# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The repository is relatively small and focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance testing rather than being a full-fledged infrastructure-as-code repository. The migration effort is estimated to be low to medium complexity, with the primary focus being on converting Chef InSpec tests to Ansible-native testing solutions.

Estimated timeline: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
A thorough search of the repository was conducted using the following patterns:
- `file_search(pattern="**/manifests/init.pp")` - No Puppet modules found
- `file_search(pattern="**/recipes/default.rb")` - No Chef cookbooks found
- `file_search(pattern="**/*.psd1")` - No PowerShell modules found

Based on the verification above, this repository does not contain traditional Puppet modules, Chef cookbooks, or PowerShell modules that would be identified by the patterns above. Instead, it contains Ansible playbooks, Chef InSpec test files, and bash scripts that need to be migrated:

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
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler testing
  - Option 3: Convert InSpec tests to Ansible assert tasks for basic validation

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles that can:
  - Option 1: Deploy alternative compliance solutions like OpenSCAP
  - Option 2: Deploy Ansible AWX/Tower for centralized management
  - Option 3: Integrate with cloud-native compliance tools if moving to cloud

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Replace self-signed certificates with Let's Encrypt integration for production

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement:
  - Create an Ansible role for SSH hardening that implements the same controls
  - Consider expanding to include additional SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks:
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Use Ansible's assert module with custom commands or Testinfra for more complex tests

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent functionality:
  - Challenge: Determining if Chef Server functionality is actually needed or if it can be replaced entirely with Ansible
  - Mitigation: Evaluate if AWX/Tower can provide the required functionality or if a different solution is needed

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already Ansible playbooks, low risk)
   - Review and optimize according to current Ansible best practices
   - Combine into a single role with appropriate tags for modularity

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible Molecule tests
   - Convert ssh_profile.rb to Ansible Molecule tests or standalone playbook with assert tasks

3. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef Server/Automate functionality is still required
   - Create Ansible roles to either deploy Chef or replace with alternative solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production infrastructure codebase
2. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
3. The deployment scripts for Chef Automate/Server are examples and not critical production code
4. The security tests (InSpec profiles) represent the actual compliance requirements that need to be maintained
5. There is no complex data structure or external data sources (like Hiera in Puppet) that need migration
6. The migration will maintain the same level of security validation currently provided by InSpec
7. No external Chef cookbooks or complex Chef-specific features are being used that would require special handling