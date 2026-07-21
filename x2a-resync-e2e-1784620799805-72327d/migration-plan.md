# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests focused on demonstration and educational purposes. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache and fixing SSL vulnerabilities
2. Chef InSpec tests for verifying configurations and security compliance
3. Bash scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests that need to be consolidated into a pure Ansible solution. The estimated timeline for migration is 1-2 days given the limited scope and straightforward configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Puppet modules with manifests/init.pp, Chef cookbooks with recipes/default.rb, or PowerShell modules with .psd1 files) were found in this repository. The repository contains:

- **Ansible Playbooks**:
  - Path: chef-and-ansible/website_https.yml
  - Path: chef-and-ansible/poodle_fix.yml

- **Chef InSpec Tests**:
  - Path: chef-and-ansible/tests/website_https_verify.rb
  - Path: chef-and-ansible/tests/ssh_profile.rb

- **Bash Deployment Scripts**:
  - Path: setup-automate/deploy-automate.sh
  - Path: setup-automate/deploy-chef-server.sh

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation for using Chef InSpec with Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic verification
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles that perform the same checks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or simplify to use Vagrant directly with Ansible provisioning

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The ssh_profile.rb InSpec test checks for SSH root login being disabled
  - This security check needs to be maintained in the Ansible solution
  - Consider implementing as an Ansible role that enforces this configuration

- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials:
  - Username: jtonello
  - Password: password
  - These should be replaced with Ansible Vault or another secure secret management solution

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Consider integrating with Let's Encrypt for production environments
  - Ensure certificate permissions are properly set (currently mode 0640)

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting the InSpec tests to Ansible-native testing will require:
  - Finding equivalent ways to test SSL protocols
  - Implementing HTTP response checking
  - Ensuring port listening verification
  - Converting SSH security profile checks to Ansible

- **Chef Automate/Server Deployment**: Converting the bash scripts to Ansible:
  - Research if there are existing Ansible roles for Chef deployment
  - Or create custom roles that perform the same steps as the bash scripts
  - Ensure proper idempotence in the Ansible implementation

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role structure
2. **poodle_fix.yml** (Priority 1): Incorporate into the website-https role
3. **InSpec Tests** (Priority 2): Convert to Ansible testing framework
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles or consider if they're still needed

### Assumptions

1. The repository is primarily for educational/demonstration purposes and not a production system
2. The Chef InSpec tests are used for verification only and not for ongoing compliance monitoring
3. The deployment scripts are examples and not used in automated pipelines
4. There is no complex state management or data persistence requirements
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The Apache configuration requirements will remain the same
7. There are no external dependencies or integrations not visible in the repository

## Migration Steps

1. **Create Ansible Role Structure**:
   ```
   roles/
     apache-https/
       tasks/
       templates/
       handlers/
       defaults/
       tests/
     ssh-security/
       tasks/
       templates/
       handlers/
       defaults/
       tests/
     chef-deployment/  # if needed
       tasks/
       templates/
       defaults/
       vars/
   ```

2. **Convert Website HTTPS Configuration**:
   - Move the Apache configuration to templates
   - Move the website content to files
   - Structure tasks in logical groups
   - Use variables for all configurable elements

3. **Implement Testing**:
   - Create Molecule scenarios to replace InSpec tests
   - Implement equivalent checks for HTTPS, SSL protocols, and content
   - Implement SSH security checks

4. **Chef Deployment** (if needed):
   - Create a role for Chef server deployment
   - Use Ansible Vault for credentials
   - Implement proper idempotence checks

5. **Documentation**:
   - Update README with new Ansible-only approach
   - Document role usage and variables
   - Provide examples for testing

## Conclusion

This migration is relatively straightforward as most of the content is already in Ansible format. The main work will be in converting the InSpec tests to an Ansible-native testing approach and properly structuring the existing Ansible playbooks into roles. The Chef deployment scripts can either be converted to Ansible roles or potentially removed if they're not needed for the core functionality.