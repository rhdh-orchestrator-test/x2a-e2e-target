# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks. The migration scope is limited as most content is already Ansible-based or consists of deployment utilities. The primary migration effort involves consolidating the existing Ansible playbooks and replacing Chef InSpec testing with Ansible-native testing approaches. Estimated timeline: 1-2 weeks for a single engineer.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates via OpenSSL, Apache virtual host setup, security configuration with TLS 1.2 enforcement

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation

**chef-automate-deployment**:
- Description: Bash script for deploying Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash shell script
- Key Features: Chef Automate installation, Chef server configuration, user/org provisioning

**chef-server-deployment**:
- Description: Bash script for deploying standalone Chef Infra Server without Automate
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash shell script  
- Key Features: Chef server installation, user/org provisioning, system tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Ansible provisioner and InSpec verifier - needs migration to molecule or native Ansible testing
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality - requires conversion to Ansible testing modules
- `tests/ssh_profile.rb`: InSpec security compliance tests for SSH configuration - needs conversion to Ansible security testing
- `index.html`: Static test content file - can remain as-is or be templated in Ansible

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification and package versions in playbooks)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible testing modules (ansible.builtin.uri, ansible.builtin.service_facts, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Deployment scripts can be converted to Ansible playbooks for infrastructure provisioning

### Security Considerations
- SSL/TLS certificate management: Current playbooks use self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- SSH security hardening: InSpec tests verify SSH root login disabled - convert to Ansible security role validation
- Apache security configuration: TLS protocol enforcement and SSL cipher suite management need validation in Ansible testing
- Credential management: Deployment scripts contain hardcoded passwords and user credentials - implement Ansible Vault for secrets management

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec tests to Ansible native testing requires rewriting test logic and assertions
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification approaches  
- **Chef Server Dependencies**: Deployment scripts assume Chef ecosystem - may need alternative configuration management server if Chef is being phased out
- **SSL Certificate Validation**: Current InSpec tests verify SSL protocol support - need equivalent Ansible modules for certificate and protocol validation

### Migration Order
1. **website-https-demo** and **poodle-ssl-fix** (already Ansible - consolidate and enhance)
2. **InSpec test conversion** (moderate complexity - requires new testing approach)
3. **Chef deployment scripts** (convert to Ansible playbooks if Chef infrastructure still needed)
4. **Test Kitchen to Molecule migration** (requires test framework restructuring)

### Assumptions
- The existing Ansible playbooks are functional and represent the desired end state for web server configuration
- Chef InSpec testing functionality needs to be preserved in the migrated solution using Ansible native testing
- The Chef server deployment scripts may still be needed if Chef infrastructure is maintained alongside Ansible
- Test Kitchen integration with Vagrant is acceptable to migrate to Molecule with similar VM-based testing
- SSL certificate management approach (self-signed vs CA-issued) requirements are not changing
- Ubuntu 20.04 target platform will remain consistent in the migrated solution
- The repository serves as examples/demos rather than production infrastructure code