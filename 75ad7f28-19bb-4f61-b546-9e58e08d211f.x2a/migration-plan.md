# MIGRATION FROM CHEF INSPEC/ANSIBLE HYBRID TO ANSIBLE

This repository contains a hybrid Chef InSpec and Ansible setup used for compliance automation examples, along with Chef server deployment scripts. The migration scope is limited as most content is already in Ansible format, with Chef InSpec used solely for testing and validation. The primary migration effort involves replacing Chef InSpec tests with native Ansible testing approaches and consolidating the infrastructure deployment scripts.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 2-3 weeks
**Primary Challenge**: Replacing Chef InSpec compliance tests with Ansible-native testing solutions

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec testing integration that need migration planning:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**ssl-security-hardening**:
- Description: Apache SSL protocol hardening to disable vulnerable SSL protocols and enforce TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: SSL protocol configuration, POODLE vulnerability mitigation, Apache configuration management

**chef-server-deployment**:
- Description: Chef Automate and Chef Infra Server deployment automation for on-premises or cloud VMs
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user and organization creation

**chef-infra-deployment**:
- Description: Standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef Infra Server installation, user management, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Chef InSpec verification
- `index.html`: Static web content (minimal impact on migration)
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility indicated in SSH compliance tests
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible testing modules (ansible.builtin.uri, ansible.builtin.command, ansible.builtin.assert)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate CLI**: Migrate deployment scripts to Ansible playbooks using package management and service modules

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates and hardcoded SSL protocols
  - Migration approach: Implement Ansible Vault for certificate management, parameterize SSL configurations
- **SSH Security**: InSpec tests verify SSH root login restrictions
  - Migration approach: Use Ansible's lineinfile module with validation, implement continuous compliance checking
- **Hardcoded Credentials**: Deployment scripts contain plaintext passwords and user information
  - Migration approach: Implement Ansible Vault for sensitive data, use variable files for environment-specific configurations
- **Certificate Management**: Self-signed certificates generated during deployment
  - Migration approach: Integrate with Let's Encrypt or corporate CA using Ansible certificate modules

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native testing
  - Mitigation: Use ansible.builtin.uri for HTTP/HTTPS testing, ansible.builtin.command for SSL protocol verification, custom fact gathering for compliance validation
- **Bash Script Conversion**: Chef server deployment scripts need conversion to idempotent Ansible playbooks
  - Mitigation: Use package, service, and command modules with proper error handling and state management
- **Test Kitchen Replacement**: Current testing framework relies on Kitchen + InSpec integration
  - Mitigation: Implement Molecule with testinfra or native Ansible assertions for comprehensive testing

### Migration Order

1. **ssl-security-hardening** (Low risk, already in Ansible format, minimal testing requirements)
2. **website-https-deployment** (Moderate complexity, requires test migration from InSpec to Ansible)
3. **chef-infra-deployment** (High complexity, bash-to-Ansible conversion, service management)
4. **chef-server-deployment** (Highest complexity, full stack deployment with user management)

### Assumptions

- The target environment will continue to use Ubuntu 20.04 or migrate to a newer LTS version
- Chef InSpec testing functionality needs to be preserved in the migrated solution
- The deployment scripts are intended for development/lab environments based on the hardcoded credentials
- SSL certificate management will transition from self-signed to a proper certificate authority
- The current Vagrant-based testing approach is acceptable to replace with Molecule
- Network connectivity and package repository access patterns will remain consistent
- The Chef server deployment functionality may be deprecated in favor of pure Ansible automation
- Compliance requirements currently met by InSpec tests must be maintained in the Ansible-native solution