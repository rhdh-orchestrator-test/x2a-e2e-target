# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security compliance

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or incorporate into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider using ansible-test for test execution

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider replacing with:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for role and module management

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security practice should be maintained in the migrated solution.
  
- **SSH Security**: The ssh_profile.rb InSpec test verifies that root login is disabled. This check should be incorporated into the Ansible playbooks or included as an Ansible-native test.

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing security by using Let's Encrypt or another trusted CA in the migrated solution.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the modules

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the equivalent assertions and test structures. Mitigation strategy: Create a mapping of InSpec resources to Ansible modules and gradually convert each test.

- **Chef Automate Replacement**: If Chef Automate functionality is needed, determining the right Ansible ecosystem tools (AWX/Tower, Collections) will be important. Mitigation strategy: Conduct a feature comparison between Chef Automate and Ansible Tower/AWX to ensure all required capabilities are covered.

- **Test Kitchen to Molecule**: Converting the testing framework will require understanding the differences in configuration and execution. Mitigation strategy: Create a parallel Molecule configuration while maintaining the Test Kitchen setup until migration is complete.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, convert to Ansible-native testing)
3. **Chef deployment scripts** (high complexity, requires architectural decisions about Ansible management)

### Assumptions

1. The primary goal is to use Ansible for both configuration management and compliance testing, eliminating the dependency on Chef InSpec.
2. The current setup is used primarily for demonstration/testing purposes rather than production, based on the self-signed certificates and test-oriented structure.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain the same level of security compliance checking currently provided by InSpec.
6. There is no requirement to maintain backward compatibility with Chef tools after migration.